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
                        execute,
                        get,
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
    sudo('apt-get -y install %s' % packages)
    sudo('easy_install pip')
    sudo('pip install -U --force-reinstall pip')
    sudo('pip install -U --force-reinstall setuptools')
    sudo('pip install -U --force-reinstall virtualenvwrapper')
    sudo('pip install -U --force-reinstall wheel')

#
# Tasks for reading configuration information.
#

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
    filename = ".codalabconfig"
    if 'cfg_path' not in env:
        env.cfg_path = os.path.join(os.getcwd(), filename)
        if os.path.exists(env.cfg_path) == False:
            env.cfg_path = os.path.join(os.path.expanduser("~"), filename)
    print "Loading configuration from: ", env.cfg_path
    configuration = DeploymentConfig(label, env.cfg_path)
    print "Configuring logger..."
    logging.config.dictConfig(configuration.getLoggerDictConfig())
    logger.info("Loaded configuration from file: %s", configuration.getFilename())

    env.user = configuration.getVirtualMachineLogonUsername()
    env.password = configuration.getVirtualMachineLogonPassword()
    env.key_filename = configuration.getServiceCertificateKeyFilename()
    env.roledefs = {'build' : [configuration.getBuildHostname()]}

    if label is not None:
        env.roledefs.update({'web' : configuration.getWebHostnames()})
        # Information about main CodaLab repo
        env.git_user = configuration.getGitUser()
        env.git_repo = configuration.getGitRepo()
        env.git_tag = configuration.getGitTag()
        env.git_repo_url = 'https://github.com/{0}/{1}.git'.format(env.git_user, env.git_repo)
        # Information about Bundles repo
        env.git_bundles_user = configuration.getBundleServiceGitUser()
        env.git_bundles_repo = configuration.getBundleServiceGitRepo()
        env.git_bundles_tag = configuration.getBundleServiceGitTag()
        env.git_bundles_repo_url = 'https://github.com/{0}/{1}.git'.format(env.git_user, env.git_repo)
        env.deploy_dir = 'deploy'
        env.build_archive = '{0}.tar.gz'.format(env.git_tag)
        env.django_settings_module = 'codalab.settings'
        env.django_configuration = configuration.getDjangoConfiguration()
        env.config_http_port = '80'
        env.config_server_name = "{0}.cloudapp.net".format(configuration.getServiceName())

    env.configuration = True

#
# Tasks for provisioning machines
#

@task
@roles('build')
def provision_build():
    """
    Installs required software packages on a newly provisioned build machine.
    """
    packages = ('build-essential python-crypto python2.7-dev python-setuptools ' +
                'libmysqlclient-dev mysql-client-core-5.5 ' +
                'libpcre3-dev libpng12-dev libjpeg-dev git')
    provision_packages(packages)

@task
@roles('web')
def provision_web():
    """
    Installs required software packages on a newly provisioned web instance.
    """
    packages = ('language-pack-en python2.7 python-setuptools libmysqlclient18 ' +
                'libpcre3 libjpeg8 libpng3 nginx supervisor git python2.7-dev ' +
                'libmysqlclient-dev mysql-client-core-5.5 uwsgi-plugin-python')
    provision_packages(packages)

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
        execute(provision_build)
    if 'web' in assets:
        logger.info("Installing sofware on web instances.")
        execute(provision_web)
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

@task
@roles('build', 'web')
def test_connections():
    """
    Verifies that we can connect to all instances.
    """
    require('configuration')
    sudo('hostname')

#
# Tasks for creating and installing build artifacts
#

@roles("build")
@task
def build():
    """
    Builds artifacts to install on the deployment instances.
    """
    require('configuration')

    # Assemble source and configurations for the web site
    build_dir = "/".join(['builds', env.git_user, env.git_repo])
    src_dir = "/".join([build_dir, env.git_tag])
    if exists(src_dir):
        run('rm -rf %s' % (src_dir.rstrip('/')))
    with settings(warn_only=True):
        run('mkdir -p %s' % src_dir)
    with cd(src_dir):
        run('git clone --depth=1 --branch %s --single-branch %s .' % (env.git_tag, env.git_repo_url))
        # Generate settings file (local.py)
        configuration = DeploymentConfig(env.cfg_label, env.cfg_path)
        dep = Deployment(configuration)
        buf = StringIO()
        buf.write(dep.getSettingsFileContent())
        settings_file = "/".join(['codalab', 'codalab', 'settings', 'local.py'])
        put(buf, settings_file)
    # Assemble source and configurations for the bundle service
    build_dir_b = "/".join(['builds', env.git_bundles_user, env.git_bundles_repo])
    src_dir_b = "/".join([build_dir_b, env.git_bundles_tag])
    if exists(src_dir_b):
        run('rm -rf %s' % (src_dir_b.rstrip('/')))
    with settings(warn_only=True):
        run('mkdir -p %s' % src_dir_b)
    with cd(src_dir_b):
        run('git clone --depth=1 --branch %s --single-branch %s .' % (env.git_bundles_tag, env.git_bundles_repo_url))
    # Replace current bundles dir in main CodaLab other bundles repo.
    bundles_dir = "/".join(src_dir, 'bundles')
    run('rm -rf %s' % (bundles_dir.rstrip('/')))
    run('mv %s %s' & (src_dir_b, bundles_dir))
    # Package everything
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
    build_dir = "/".join(['builds', env.git_user, env.git_repo])
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
    if exists(env.deploy_dir):
        run('rm -rf %s' % env.deploy_dir)
    run('tar -xvzf %s' % env.build_archive)
    run('mv %s deploy' % env.git_tag)
    run('source /usr/local/bin/virtualenvwrapper.sh && mkvirtualenv venv')
    env.SHELL_ENV = dict(
        DJANGO_SETTINGS_MODULE=env.django_settings_module,
        DJANGO_CONFIGURATION=env.django_configuration,
        CONFIG_HTTP_PORT=env.config_http_port,
        CONFIG_SERVER_NAME=env.config_server_name)
    print env.SHELL_ENV
    with cd(env.deploy_dir):
        with prefix('source /usr/local/bin/virtualenvwrapper.sh && workon venv'), shell_env(**env.SHELL_ENV):
            requirements_path = "/".join(['codalab', 'requirements', 'dev_azure_nix.txt'])
            pip_cmd = 'pip install -r {0}'.format(requirements_path)
            run(pip_cmd)
            # additional requirements for bundle service
            run('pip install SQLAlchemy simplejson')
            with cd('codalab'):
                run('python manage.py config_gen')
                run('python manage.py syncdb --migrate')
                run('python scripts/initialize.py')
                run('python manage.py collectstatic --noinput')
                sudo('ln -sf `pwd`/config/generated/nginx.conf /etc/nginx/sites-enabled/codalab.conf')

@roles('web')
@task
def install_mysql(choice='all'):
    """
    Installs a local instance of MySQL of the web instance. This will only work
    if the number of web instances is one.

    choice: Indicates which assets to create/install:
        'mysql'      -> just install MySQL; don't create the databases
        'site_db'    -> just create the site database
        'bundles_db' -> just create the bundle service database
        'all' or ''  -> install all three
    """
    require('configuration')
    if len(env.roledefs['web']) != 1:
        raise Exception("Task install_mysql requires exactly one web instance.")

    if choice == 'mysql':
        choices = {'mysql'}
    elif choice == 'site_db':
        choices = {'site_db'}
    elif choice == 'bundles_db':
        choices = {'bundles_db'}
    elif choice == 'all':
        choices = {'mysql', 'site_db', 'bundles_db'}
    else:
        raise ValueError("Invalid choice: %s. Valid choices are: 'build', 'web' or 'all'." % (choice))

    configuration = DeploymentConfig(env.cfg_label, env.cfg_path)
    dba_password = configuration.getDatabaseAdminPassword()

    if 'mysql' in choices:
        sudo('DEBIAN_FRONTEND=noninteractive apt-get -q -y install mysql-server')
        sudo('mysqladmin -u root password {0}'.format(dba_password))

    if 'site_db' in choices:
        db_name = configuration.getDatabaseName()
        db_user = configuration.getDatabaseUser()
        db_password = configuration.getDatabasePassword()
        cmds = ["create database {0};".format(db_name),
                "create user '{0}'@'localhost' IDENTIFIED BY '{1}';".format(db_user, db_password),
                "GRANT ALL PRIVILEGES ON {0}.* TO '{1}'@'localhost' WITH GRANT OPTION;".format(db_name, db_user)]
        run('mysql --user=root --password={0} --execute="{1}"'.format(dba_password, " ".join(cmds)))

    if 'bundles_db' in choices:
        db_name = configuration.getBundleServiceDatabaseName()
        db_user = configuration.getBundleServiceDatabaseUser()
        db_password = configuration.getBundleServiceDatabasePassword()
        cmds = ["create database '{0}';".format(db_name),
                "create user '{0}'@'localhost' IDENTIFIED BY '{1}';".format(db_user, db_password),
                "GRANT ALL PRIVILEGES ON '{0}'.* TO '{1}'@'localhost' WITH GRANT OPTION;".format(db_name, db_user)]
        run('mysql --user=root --password={0} --execute="{1}"'.format(dba_password, " ".join(cmds)))

@roles('web')
@task
def install_ssl_certificates():
    """
    Installs SSL certificates on the web instance.
    """
    require('configuration')
    cfg = DeploymentConfig(env.cfg_label, env.cfg_path)
    put(cfg.getSslCertificatePath(), cfg.getSslCertificateInstalledPath(), use_sudo=True)
    put(cfg.getSslCertificateKeyPath(), cfg.getSslCertificateKeyInstalledPath(), use_sudo=True)

@roles('web')
@task
def supervisor():
    """
    Starts the supervisor on the web instances.
    """
    with cd(env.deploy_dir):
        with prefix('source /usr/local/bin/virtualenvwrapper.sh && workon venv'):
            run('supervisord -c codalab/config/generated/supervisor.conf')

@roles('web')
@task
def supervisor_stop():
    """
    Stops the supervisor on the web instances.
    """
    with cd(env.deploy_dir):
        with prefix('source /usr/local/bin/virtualenvwrapper.sh && workon venv'):
            run('supervisorctl -c codalab/config/generated/supervisor.conf shutdown')

@roles('web')
@task
def supervisor_restart():
    """
    Restarts the supervisor on the web instances.
    """
    with cd(env.deploy_dir):
        with prefix('source /usr/local/bin/virtualenvwrapper.sh && workon venv'):
            run('supervisorctl -c codalab/config/generated/supervisor.conf restart all')

@roles('web')
@task
def nginx_restart():
    """
    Restarts nginx on the web instances.
    """
    sudo('/etc/init.d/nginx restart')

#
# Maintenance and diagnostics
#

@roles('web')
@task
def fetch_logs():
    """
    Fetch logs from the web instances into ~/logs.
    """
    require('configuration')
    with cd(env.deploy_dir):
        get('codalab/var/*.log', '~/logs/%(host)s/%(path)s')
