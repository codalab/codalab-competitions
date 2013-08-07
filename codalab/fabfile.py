import os,sys
from fabric.operations import local as lrun, run, put
from fabric.api import env, task, hosts, roles, cd
from fabvenv import make_virtualenv, virtualenv

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PATH = os.path.join(THIS_DIR,'venv')
THIS_SETTINGS_DIR = os.path.join(THIS_DIR,'codalab','settings')

env.conf.DEPLOY_USER = 'wwwuser'
env.conf.DEPLOY_PATH = 'codalab_src'

def env_setup(config=env.CONFIG,settings_module='codalab.settings'):
    if config is None:
        
    sys.path.append('.')
    os.environ['DJANGO_CONFIGURATION'] = config
    os.environ["DJANGO_SETTINGS_MODULE"] = settings_module
    from fabric.contrib import django
    
    from configurations import importer

    importer.install()
    
    django.settings_module(settings_module)
    from django.conf import settings as django_settings

    env.roledefs = django_settings.DEPLOY_ROLES
    env.django_settings = django_settings

@task
def local(**kwargs):    
    env.run = lrun
    env_setup(**kwargs)

@task
def remote(**kwargs):    
    env.run = run
    env_setup(**kwargs)

@task
def clone_repo(repo_url='https://github.com/codalab/codalab.git',path=env.conf.DEPLOY_PATH):
    env.run('git clone %s %s' % (repo_url, path))
    
@task
def provision(config='Dev'):
    clone_repo()
    with cd(env.conf.DEPLOY_PATH):
        sudo('/bin/bash codalab/scripts/provision %s' % env.conf.DEPLOY_USER)
        sudo('python manage.py config_gen --configuration=%s' % config,
             user=env.conf.DEPLOY_USER)
        
@task
def bootstrap():
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
