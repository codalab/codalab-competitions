import os,sys,datetime
from fabric.operations import local as lrun, run, put
from fabric.api import env, task, hosts, roles, cd, shell_env, sudo, lcd, settings, prefix
from fabric.contrib.files import exists
from fabvenv import make_virtualenv, virtualenv

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PATH = os.path.join(THIS_DIR,'venv')
THIS_SETTINGS_DIR = os.path.join(THIS_DIR,'codalab','settings')


# Environment variables will take precidence

## Use fab --set key=value,... to alter these
try:
    env.DJANGO_CONFIG
except AttributeError:
    env.DJANGO_CONFIG = 'Dev'
try:
    env.SETTINGS_MODULE
except AttributeError:
    env.SETTINGS_MODULE = 'codalab.settings'

sys.path.append('.')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", env.SETTINGS_MODULE)
os.environ.setdefault('DJANGO_CONFIGURATION', env.DJANGO_CONFIG)

env.django_configuration = os.environ['DJANGO_CONFIGURATION']
env.django_settings_module = os.environ['DJANGO_SETTINGS_MODULE']

from fabric.contrib import django

from configurations import importer
importer.install()

django.settings_module(env.django_settings_module)
from django.conf import settings as django_settings


env.REMOTE_USER = 'djangodev'
env.DEPLOY_USER = 'djangodev'
env.DEPLOY_PATH = 'codalab'

env.venvpath = os.path.join('/home',env.DEPLOY_USER,'venv')

def env_setup(config=env.DJANGO_CONFIG, settings_module='codalab.settings', fab_module='codalab.settings.fabfile'):
    try:
        fab_module = __import__(fab_module)
        from fab_module import *
    except ImportError:
        print "fab module not found to import"
        pass
    

    
@task
def local(**kwargs):    
    env.run = lrun
    env_setup(**kwargs)

@task
def remote(**kwargs):    
    env.run = run
    env_setup(**kwargs)

 
@task
def clone_repo(url='https://github.com/codalab/codalab.git',target=env.DEPLOY_PATH):
    run("git clone %s %s" % (url, target))
   
@task
def provision():
    """
    This will copy the provision script from the repo and execute it.
    """
    run('mkdir -p codalab_scripts')
    put(os.path.join(THIS_DIR,'scripts/ubuntu/'), 'codalab_scripts/', mirror_local_mode=True)
    sudo('codalab_scripts/ubuntu/provision %s' % env.DEPLOY_USER)

@task
def config_gen():
    with cd(env.DEPLOY_PATH), shell_env(DJANGO_CONFIGURATION=env.django_configuration,DJANGO_SETTINGS_MODULE=env.django_settings_module):
        sudo('python manage.py config_gen' % config,
             user=env.DEPLOY_USER) 
@task
def bootstrap():    
    make_virtualenv(path=env.venvpath, system_site_packages=False)
    #run('virtualenv --distribute %s' % env.venvpath)
    #with prefix('source %s' % os.path.join(env.venvpath, 'bin/activate')):
    with virtualenv(env.venvpath):
        run('pip install --upgrade pip')
        run('pip install --upgrade Distribute')
        if exists(env.DEPLOY_PATH):
            run('mv %s %s' %  (env.DEPLOY_PATH, env.DEPLOY_PATH + '_' + str(datetime.datetime.now().strftime('%Y%m%d%s%f'))))
            #sudo('rm -rf %s' % env.DEPLOY_PATH)
        clone_repo(target=env.DEPLOY_PATH)
        with cd(env.DEPLOY_PATH):
            run('./requirements dev.txt azure.txt')
    #put(os.path.join(THIS_SETTINGS_DIR,'deploy.py'), '%s/codalab/codalab/settings' % env.DEPLOY_PATH)

@task
def requirements():
    with virtualenv('venv'):
        run('cd codalab_src && bash ./requirements')
            
        
@task
def install():
    env.run('deploymentcmd')

@task
def whoami():
    with settings(sudo_user=env.DEPLOY_USER):
        sudo('whoami')

