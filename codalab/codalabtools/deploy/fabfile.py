"""
Defines deployment commands.
"""

import logging
import logging.config
import os
from os.path import (abspath,
                     dirname)
import sys

# Add codalabtools to the module search path
sys.path.append(dirname(dirname(dirname(abspath(__file__)))))

from StringIO import StringIO
from fabric.api import (cd,
                        env,
                        prefix,
                        put,
                        require,
                        task,
                        roles,
                        require,
                        run,
                        settings,
                        shell_env,
                        sudo)
from fabric.contrib.files import exists
from codalabtools.deploy import DeploymentConfig, Deployment


logger = logging.getLogger('codalabtools')

#
# Internal helpers
#

def _validate_asset_choice(choice):
    """
    Translate the choice string into a list of assets. See Deploy and Teardown functions.

    choice: One of 'all', 'build' or 'web'.
    """
    if choice == 'all':
        assets = {'build', 'web'}
    elif choice == 'build':
        assets = {'build'}
    elif choice == 'web':
        assets = {'web'}
    else:
        raise ValueError("Invalid choice: %s. Valid choices are: 'build', 'web' or 'all'." % (choice))
    return assets

def provision_packages(packages=None):
    """
    Installs a set of packages on a host machine.

    packages: A string listing the packages which will get installed with the command:
        sudo apt-get -y install <packages>
    """
    sudo('apt-get update')
    sudo('apt-get -y install %s' % packages )
    sudo('easy_install pip')
    sudo('pip install -U --force-reinstall pip')
    sudo('pip install -U --force-reinstall setuptools')
    sudo('pip install -U --force-reinstall virtualenvwrapper')
    sudo('pip install -U --force-reinstall wheel')

#
# Tasks
#

@task
@roles('build', 'web')
def connect():
    """
    Verifies that we can connect to all instances.
    """
    require('configuration')
    sudo('hostname')


@roles("build")
@task
def build():
    """
    Builds artifacts to install on the deployment instances.
    """
    require('configuration')

    pip_cache_dir = os.path.join('builds', 'pip_cache')
    if not exists(pip_cache_dir):
        run('mkdir -p %s' % pip_cache_dir)
    with cd(pip_cache_dir):
        pip_download_cache = run('pwd')

    build_dir = os.path.join('builds', env.git_user, env.git_repo)
    src_dir = os.path.join(build_dir, env.git_tag)
    if exists(src_dir):
        run('rm -rf %s' % (src_dir.rstrip('/')))
    with settings(warn_only=True):
        run('mkdir -p %s' % src_dir)
    with cd(src_dir):
        run('git clone --depth=1 --branch %s --single-branch %s .' % (env.git_tag, env.git_repo_url))
        buf = StringIO()
        buf.write(env.settings_content)
        settings_file = os.path.join('codalab', 'codalab', 'settings', 'local.py')
        put(buf, settings_file)
    wheel_dir = os.path.join(src_dir, 'wheel_packages')
    requirements_dir = os.path.join(src_dir, 'codalab', 'requirements')
    run('pip wheel --download-cache %s --wheel-dir=%s -r %s/dev_azure_nix.txt' % (pip_download_cache,
                                                                                  wheel_dir,
                                                                                  requirements_dir))
    with cd(build_dir):
        run('rm -f %s' % env.build_archive)
        run('tar -cvf - %s | gzip -9 -c > %s' % (env.git_tag, env.build_archive))

@roles("build")
@task
def push_build():
    """
    Pushes the output of the build task to the instances where the build artifacts will be installed.
    """
    require('configuration')
    build_dir = os.path.join('builds', env.git_user, env.git_repo)
    with cd(build_dir):
        for host in env.roledefs['web']:
            parts = host.split(':', 1)
            host = parts[0]
            port = parts[1]
            run('scp -P {0} {1} {2}@{3}:{4}'.format(port, env.build_archive, env.user, host, env.build_archive))

@roles('web')
@task
def deploy_web():
    """
    Installs the output of the build on the web instances.
    """
    require('configuration')

    #export CONFIG_SERVER_NAME=cxpdev.cloudapp.net
    #export DJANGO_SETTINGS_MODULE=codalab.settings
    #export CONFIG_HTTP_PORT=80
    #export DJANGO_CONFIGURATION=Prod
    if exists(env.deploy_dir):
        run('rm -rf %s' % env.deploy_dir)
    run('tar -xvzf ../%s' % env.build_archive)
    run('mv %s deploy' % env.git_tag)
    run('source /usr/local/bin/virtualenvwrapper.sh')
    run('mkvirtualenv venv')
    with cd(env.deploy_dir):
        with prefix('workon venv'), shell_env(**env.SHELL_ENV):
            requirements_path = os.path.join('codalab', 'requirements', 'dev_azure_nix.txt')
            pip_cmd = 'pip install --use-wheel --no-index --find-links=wheel_packages -r {0}'.format(requirements_path)
            run(pip_cmd)
            with cd('codalab'):
                run('python manage.py config_gen')
                run('python manage.py syncdb --migrate')
                run('python manage.py collectstatic --noinput')
                sudo('ln -sf `pwd`/config/generated/nginx.conf /etc/nginx/sites-enabled/codalab.conf')

@task
def using(path):
    """
    Specifies a location for the CodaLab configuration file.
    """
    env.cfg_path = path

@task
def config(label=None):
    """
    Reads deployment parameters for the given setup.

    label: Label identifying the desired setup.
    """
    env.cfg_label = label
    print "Deployment label is: ", env.cfg_label
    if 'cfg_path' not in env:
        env.cfg_path = os.path.join(os.environ['HOME'], '.codalabconfig')
    print "Loading configuration from: ", env.cfg_path
    configuration = DeploymentConfig(label, env.cfg_path)
    print "Configuring logger..."
    logging.config.dictConfig(configuration.getLoggerDictConfig())
    logger.info("Loaded configuration from file: %s", configuration.getFilename())

    env.user = configuration.getVirtualMachineLogonUsername()
    env.password = configuration.getVirtualMachineLogonPassword()
    env.key_filename = configuration.getServiceCertificateKeyFilename()
    env.roledefs = { 'build' : [ configuration.getBuildHostname() ] }

    if label is not None:
        env.roledefs.update({ 'web' : configuration.getWebHostnames() })
        env.git_user = configuration.getGitUser()
        env.git_repo = configuration.getGitRepo()
        env.git_tag = configuration.getGitTag()
        env.git_repo_url = 'https://github.com/{0}/{1}.git'.format(env.git_user, env.git_repo)

        dep = Deployment(configuration)
        env.settings_content = dep.getSettingsFileContent()
        print env.settings_content
        env.deploy_dir = 'deploy'
        env.build_archive = '{0}.tar.gz'.format(env.git_tag)

    env.configuration = True

@task
def provision(choice):
    """
    Provisions specified assets in the deployment.

    choice: Indicates which assets to provision:
        'build' -> provision the build machine
        'web'   -> provision the web instances
        'all'   -> provision everything
    """
    assets = _validate_asset_choice(choice)
    require('configuration')
    logger.info("Provisioning begins: %s.", assets)
    configuration = DeploymentConfig(env.cfg_label, env.cfg_path)
    dep = Deployment(configuration)
    dep.Deploy(assets)
    if 'build' in assets:
        logger.info("Installing sofware on the build machine.")
        packages = ('build-essential python-crypto python2.7-dev python-setuptools' +
                    'libmysqlclient-dev mysql-client-core-5.5' +
                    'libpcre3-dev libpng12-dev libjpeg-dev' +
                    'git')
        provision_packages(packages)
    if 'web' in assets:
        logger.info("Installing sofware on web instances.")
        packages = ('language-pack-en' +
                    'python2.7 python-setuptools' +
                    'libmysqlclient18' +
                    'libpcre3 libjpeg8 libpng3' +
                    'nginx supervisor' +
                    'git')
        provision_packages(packages)
    logger.info("Provisioning is complete.")

@task
def teardown(choice):
    """
    Deletes specified assets in the deployment. Be careful: there is no undoing!

    choice: Indicates which assets to delete:
        'build' -> provision the build machine
        'web'   -> provision the web instances
        'all'   -> provision everything
    """
    assets = _validate_asset_choice(choice)
    require('configuration')
    logger.info("Teardown begins: %s.", assets)
    configuration = DeploymentConfig(env.cfg_label, env.cfg_path)
    dep = Deployment(configuration)
    dep.Teardown(assets)
    logger.info("Teardown is complete.")
