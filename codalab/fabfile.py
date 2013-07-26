import os,sys
from fabric.operations import local as lrun, run, put
from fabric.api import env, task, hosts, roles, cd
from fabvenv import make_virtualenv, virtualenv

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PATH = os.path.join(THIS_DIR,'venv')
THIS_SETTINGS_DIR = os.path.join(THIS_DIR,'codalab','settings')

def env_setup(config=env.CONFIG,settings_module='codalab.settings'):
    sys.path.append('.')
    os.environ['DJANGO_CONFIGURATION'] = config
    os.environ["DJANGO_SETTINGS_MODULE"]= settings_module
    
    from configurations import importer

    importer.install()
    from fabric.contrib import django
    django.settings_module(settings_module)
    from django.conf import settings

    #env.roledefs = settings.DEPLOY_ROLES
    env.django_settings = settings
env_setup()

@task
def local():    
    env.run = lrun
    
@task
def remote():    
    env.run = run

@task
def bootstrap_on_linux():
    make_virtualenv(path='venv', system_site_packages=False)
    with virtualenv('venv'):
        run('pip install --upgrade pip')
        run('pip install --upgrade distribute')
        run('rm -rf codalab_src')
        run("git clone %s codalab_src" % env.django_settings.SOURCE_GIT_URL)
    put(os.path.join(THIS_SETTINGS_DIR,'deploy.py'), 'codalab_src/codalab/codalab/settings')

    with virtualenv('venv'):
        run('cd codalab_src && bash ./requirements')
            
        
@task
def install():
    env.run('deploymentcmd')
