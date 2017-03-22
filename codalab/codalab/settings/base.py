import re
import uuid
from textwrap import dedent

from configurations import importer
from django.utils.text import slugify

if not importer.installed:
    importer.install()

from configurations import Settings
import os, sys
from os.path import abspath, basename, dirname, join, normpath


def _uuidpathext(filename, prefix):
    filename = basename(filename)
    filepath = join(prefix, str(uuid.uuid4()), filename)
    return filepath


class Base(Settings):
    SETTINGS_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_APP_DIR = os.path.dirname(SETTINGS_DIR)
    PROJECT_DIR = os.path.dirname(PROJECT_APP_DIR)
    ROOT_DIR = os.path.dirname(PROJECT_DIR)
    PORT = '8000'
    DOMAIN_NAME = 'localhost'
    SERVER_NAME = 'localhost'
    DEBUG = os.environ.get('DEBUG', False)
    TEMPLATE_DEBUG = DEBUG
    COMPILE_LESS = True # is the less -> css already done or would you like less.js to compile it on render
    LOCAL_MATHJAX = False # see prep_for_offline
    LOCAL_ACE_EDITOR = False # see prep_for_offline
    IS_DEV = False

    if 'CONFIG_SERVER_NAME' in os.environ:
        SERVER_NAME = os.environ.get('CONFIG_SERVER_NAME')
    if 'CONFIG_HTTP_PORT' in os.environ:
        PORT = os.environ.get('CONFIG_HTTP_PORT')

    MAINTENANCE_MODE=0
    if 'MAINTENANCE_MODE' in os.environ:
        MAINTENANCE_MODE = os.environ.get('MAINTENANCE_MODE')

    STARTUP_ENV = {
        'DJANGO_CONFIGURATION': os.environ['DJANGO_CONFIGURATION'],
        'DJANGO_SETTINGS_MODULE': os.environ['DJANGO_SETTINGS_MODULE'],
        'NEW_RELIC_CONFIG_FILE': '%s/newrelic.ini' % PROJECT_DIR,
    }

    TEST_DATA_PATH = os.path.join(PROJECT_DIR,'test_data')
    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'  #'codalab.test_runner.CodalabTestRunner'
    CONFIG_GEN_TEMPLATES_DIR = os.path.join(PROJECT_DIR,'config','templates')
    CONFIG_GEN_GENERATED_DIR = os.path.join(PROJECT_DIR,'config','generated')

    DJANGO_ROOT = dirname(dirname(abspath(__file__)))
    SITE_ROOT = dirname(DJANGO_ROOT)

    SOURCE_GIT_URL = 'https://github.com/codalab/codalab.git'
    VIRTUAL_ENV = os.environ.get('VIRTUAL_ENV',None)

    AUTH_USER_MODEL = 'authenz.ClUser'

    # Keep in sync with codalab-cli
    CODALAB_VERSION = '0.1.1'

    # Hosts/domain names that are valid for this site; required if DEBUG is False
    # See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
    ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', ['*'])

    ADMINS = (
        # ('Your Name', 'your_email@example.com'),
    )

    MANAGERS = ADMINS

    # Local time zone for this installation. Choices can be found here:
    # http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
    # although not all choices may be available on all operating systems.
    # In a Windows environment this must be set to your system time zone.
    TIME_ZONE = 'UTC'

    # Language code for this installation. All choices can be found here:
    # http://www.i18nguy.com/unicode/language-identifiers.html
    LANGUAGE_CODE = 'en-us'

    SITE_ID = 1
    CODALAB_SITE_DOMAIN = os.environ.get('CODALAB_SITE_DOMAIN', 'localhost')
    CODALAB_SITE_NAME = 'CodaLab'

    # If you set this to False, Django will make some optimizations so as not
    # to load the internationalization machinery.
    USE_I18N = True

    # If you set this to False, Django will not format dates, numbers and
    # calendars according to the current locale.
    USE_L10N = True

    # If you set this to False, Django will not use timezone-aware datetimes.
    USE_TZ = True

    # Absolute filesystem path to the directory that will hold user-uploaded files.
    # Example: "/var/www/example.com/media/"
    MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')

    # URL that handles the media served from MEDIA_ROOT. Make sure to use a
    # trailing slash.
    # Examples: "http://example.com/media/", "http://media.example.com/"
    MEDIA_URL = '/media/'

    # Absolute path to the directory static files should be collected to.
    # Don't put anything in this directory yourself; store your static files
    # in apps' "static/" subdirectories and in STATICFILES_DIRS.
    # Example: "/var/www/example.com/static/"
    STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')

    # URL prefix for static files.
    # Example: "http://example.com/static/", "http://static.example.com/"
    STATIC_URL = '/static/'

    # Additional locations of static files
    STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    )

    # List of finder classes that know how to find static files in
    # various locations.
    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'compressor.finders.CompressorFinder',
    )

    # Make this unique, and don't share it with anybody.
    SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', "a-hidden-secret")

    # List of callables that know how to import templates from various sources.
    TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )

    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    )

    ROOT_URLCONF = 'codalab.urls'

    # Python dotted path to the WSGI application used by Django's runserver.
    WSGI_APPLICATION = 'codalab.wsgi.application'

    TEMPLATE_DIRS = (
        # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
        # Always use forward slashes, even on Windows.
        # Don't forget to use absolute paths, not relative paths.
        os.path.join(PROJECT_DIR,'templates'),
    )

    TEMPLATE_CONTEXT_PROCESSORS = Settings.TEMPLATE_CONTEXT_PROCESSORS + (
        "allauth.account.context_processors.account",
        "allauth.socialaccount.context_processors.socialaccount",
        "codalab.context_processors.app_version_proc",
        "django.core.context_processors.request",
        "codalab.context_processors.common_settings",
    )

    AUTHENTICATION_BACKENDS = (
        "django.contrib.auth.backends.ModelBackend",
        "allauth.account.auth_backends.AuthenticationBackend",
        'guardian.backends.ObjectPermissionBackend',
    )

    INSTALLED_APPS = (
        # Standard django apps
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.admin',
        'django.contrib.humanize',

        # Analytics app that works with many services - IRJ 2013.7.29
        'analytical',
        'rest_framework',

        # This is used to manage the HTML page hierarchy for the competition
        'mptt',

        # TODO: Document the need for these
        'django_config_gen',
        'compressor',
        'django_js_reverse',
        'guardian',
        'captcha',
        'bootstrapform',

        # Storage API
        'storages',
        's3direct',

        # Migration app
        'south',

        # Django Nose !!Important!! This needs to come after South.
        'django_nose',

        # CodaLab apps
        'apps.authenz',
        'apps.jobs',
        'apps.api',
        'apps.web',
        'apps.health',
        'apps.analytics',
        'apps.forums',
        'apps.coopetitions',
        'apps.common',
        'apps.queues',
        'apps.teams',

        # Authentication app, enables social authentication
        'allauth',
        'allauth.account',
        'allauth.socialaccount',
        'tinymce',
        'oauth2_provider',

        # Search
        'haystack',
        'django_extensions',
    )

    ACCOUNT_ADAPTER = ("apps.authenz.adapter.CodalabAccountAdapter")

    OPTIONAL_APPS = []
    INTERNAL_IPS = []

    OAUTH2_PROVIDER = {
        'OAUTH2_VALIDATOR_CLASS': 'apps.authenz.oauth.Validator',
        'ACCESS_TOKEN_EXPIRE_SECONDS': 60 * 60 * 24 * 3,  # 3 days
    }

    # Authentication configuration
    LOGIN_REDIRECT_URL = '/'
    ANONYMOUS_USER_ID = -1
    ACCOUNT_AUTHENTICATION_METHOD='username_email'
    ACCOUNT_EMAIL_REQUIRED = True
    ACCOUNT_USERNAME_REQUIRED = True
    ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
    ACCOUNT_SIGNUP_FORM_CLASS = 'apps.authenz.forms.CodalabSignupForm'

    # Django Analytical configuration
    # GOOGLE_ANALYTICS_PROPERTY_ID = 'UA-42847758-2'

    # Compress Configuration
    COMPRESS_PRECOMPILERS = (
        ('text/less', 'lessc {infile} {outfile}'),
        ('text/typescript', 'tsc {infile} --out {outfile}'),
    )

    REST_FRAMEWORK = {
        'DEFAULT_RENDERER_CLASSES': (
            'rest_framework.renderers.JSONRenderer',
        ),
    }

    SOUTH_MIGRATION_MODULES = {
        'captcha': 'captcha.south_migrations',
    }

    BUNDLE_SERVICE_URL = ""

    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
        },
    }

    # =========================================================================
    # SSL
    # =========================================================================
    SSL_PORT = os.environ.get('SSL_PORT', '443')
    SSL_CERTIFICATE = os.environ.get('SSL_CERTIFICATE')
    SSL_CERTIFICATE_KEY = os.environ.get('SSL_CERTIFICATE_KEY')

    if SSL_CERTIFICATE:
        SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
        # SECURE_SSL_REDIRECT = True
        SESSION_COOKIE_SECURE = True
        CSRF_COOKIE_SECURE = True


    # =========================================================================
    # Caching
    # =========================================================================
    try:
        # Don't force people to install/use this
        import memcached

        MEMCACHED_PORT = os.environ.get('MEMCACHED_PORT', 11211)
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
                'LOCATION': 'memcached:{}'.format(MEMCACHED_PORT),
            }
        }

        # Store information for celery
        CELERY_RESULT_BACKEND = 'cache+memcached://memcached:{}/'.format(MEMCACHED_PORT)
    except ImportError:
        pass


    # =========================================================================
    # Email
    # =========================================================================
    EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.sendgrid.net')
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
    EMAIL_PORT = os.environ.get('EMAIL_PORT', 587)
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', True)
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'CodaLab <noreply@codalab.org>')
    SERVER_EMAIL = os.environ.get('SERVER_EMAIL', 'noreply@codalab.org')


    # =========================================================================
    # Storage
    # =========================================================================
    DEFAULT_FILE_STORAGE = os.environ.get('DEFAULT_FILE_STORAGE', 'django.core.files.storage.FileSystemStorage')

    # S3 from AWS
    USE_AWS = DEFAULT_FILE_STORAGE == 'storages.backends.s3boto.S3BotoStorage'
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_STORAGE_PRIVATE_BUCKET_NAME = os.environ.get('AWS_STORAGE_PRIVATE_BUCKET_NAME')
    AWS_S3_CALLING_FORMAT = os.environ.get('AWS_S3_CALLING_FORMAT', 'boto.s3.connection.OrdinaryCallingFormat')
    AWS_S3_HOST = os.environ.get('AWS_S3_HOST', 's3-us-west-2.amazonaws.com')
    AWS_QUERYSTRING_AUTH = os.environ.get(
        # This stops signature/auths from appearing in saved URLs
        'AWS_QUERYSTRING_AUTH',
        False
    )
    if isinstance(AWS_QUERYSTRING_AUTH, str) and 'false' in AWS_QUERYSTRING_AUTH.lower():
        AWS_QUERYSTRING_AUTH = False  # Was set to string, convert to bool

    # Azure
    AZURE_ACCOUNT_NAME = os.environ.get('AZURE_ACCOUNT_NAME')
    AZURE_ACCOUNT_KEY = os.environ.get('AZURE_ACCOUNT_KEY')
    AZURE_CONTAINER = os.environ.get('AZURE_CONTAINER', 'public')
    BUNDLE_AZURE_ACCOUNT_NAME = os.environ.get('BUNDLE_AZURE_ACCOUNT_NAME', AZURE_ACCOUNT_NAME)
    BUNDLE_AZURE_ACCOUNT_KEY = os.environ.get('BUNDLE_AZURE_ACCOUNT_KEY', AZURE_ACCOUNT_KEY)
    BUNDLE_AZURE_CONTAINER = os.environ.get('BUNDLE_AZURE_CONTAINER', 'bundles')


    # =========================================================================
    # S3Direct (S3 uploads)
    # =========================================================================
    S3DIRECT_REGION = os.environ.get('S3DIRECT_REGION', 'us-west-2')
    S3DIRECT_DESTINATIONS = {
        'competitions': {
            'key': lambda f: _uuidpathext(f, 'uploads/competitions/'),
            'auth': lambda u: u.is_authenticated(),
            'bucket': AWS_STORAGE_PRIVATE_BUCKET_NAME,
            'allowed': ['application/zip', 'application/octet-stream']
        },
        'submissions': {
            'key': lambda f: _uuidpathext(f, 'uploads/submissions/'),
            'auth': lambda u: u.is_authenticated(),
            'bucket': AWS_STORAGE_PRIVATE_BUCKET_NAME,
            'allowed': ['application/zip', 'application/octet-stream']
        }
    }


    # =========================================================================
    # RabbitMQ
    # =========================================================================
    RABBITMQ_DEFAULT_USER = os.environ.get('RABBITMQ_DEFAULT_USER', 'guest')
    RABBITMQ_DEFAULT_PASS = os.environ.get('RABBITMQ_DEFAULT_PASS', 'guest')
    RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbit')
    RABBITMQ_PORT = os.environ.get('RABBITMQ_PORT', '5672')
    RABBITMQ_MANAGEMENT_PORT = os.environ.get('RABBITMQ_MANAGEMENT_PORT', '15672')


    # =========================================================================
    # Celery
    # =========================================================================
    BROKER_URL = os.environ.get('BROKER_URL')
    if not BROKER_URL:
        # BROKER_URL might be set but empty, make sure it's set!
        BROKER_URL = 'pyamqp://{}:{}@{}:{}//'.format(RABBITMQ_DEFAULT_USER, RABBITMQ_DEFAULT_PASS, RABBITMQ_HOST, RABBITMQ_PORT)
    BROKER_POOL_LIMIT = None  # Stops connection timeout
    BROKER_USE_SSL = SSL_CERTIFICATE or os.environ.get('BROKER_USE_SSL', False)
    # Don't use pickle -- dangerous
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    # Keep celery from becoming unresponsive
    CELERY_ACKS_LATE = True
    CELERYD_PREFETCH_MULTIPLIER = 1
    CELERYD_TASK_SOFT_TIME_LIMIT = 180  # 3 minutes
    FLOWER_PORT = os.environ.get('FLOWER_PORT', '15672')
    # Run as *not* root
    CELERYD_USER = "workeruser"
    CELERYD_GROUP = "workeruser"


    # =========================================================================
    # Single Competition Mode
    # =========================================================================
    # Single competition mode? Uncomment this and specify a
    # competition pk to focus on
    SINGLE_COMPETITION_VIEW_PK = os.environ.get('SINGLE_COMPETITION_VIEW_PK')


    # =========================================================================
    # Logging
    # =========================================================================
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '%(asctime)s %(levelname)s %(message)s'
            },
        },
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
                'stream': sys.stdout
            },
            'mail_admins': {
                'level': 'ERROR',
                'filters': ['require_debug_false'],
                'class': 'django.utils.log.AdminEmailHandler'
            }
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': True,
            },
            'django.request': {
                'handlers': ['mail_admins'],
                'level': 'ERROR',
                'propagate': True,
            },
            'codalab': {
                'handlers': ['console'],
                'level': 'INFO'
            },
            'codalabtools': {
                'handlers': ['console'],
                'level': 'INFO'
            },
            'apps': {
                'handlers': ['console'],
                'level': 'INFO'
            }
        }
    }


    # =========================================================================
    # Database
    # =========================================================================
    mysqldb = os.environ.get('MYSQL_DATABASE')

    if 'test' in sys.argv or any('py.test' in arg for arg in sys.argv):
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        }
    elif mysqldb:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': os.environ.get('MYSQL_DATABASE'),
                'USER': os.environ.get('MYSQL_USERNAME', 'root'),
                'PASSWORD': os.environ.get('MYSQL_ROOT_PASSWORD'),
                'HOST': 'mysql',
                'OPTIONS': {
                    'init_command': "SET time_zone='+00:00';",
                },
            }
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'codalab.sqlite3',
            }
        }

    # =========================================================================
    # Misc
    # =========================================================================
    GRAPH_MODELS = {
        'all_applications': True,
        'group_models': True,
    }

    USERSWITCH_OPTIONS = {
        'auth_backend': 'django.contrib.auth.backends.ModelBackend',
        'css_inline': 'position:fixed !important; bottom: 10px !important; left: 10px !important; opacity:0.50; z-index: 9999;',
    }

    @classmethod
    def pre_setup(cls):
        if hasattr(cls,'OPTIONAL_APPS'):
            for a in cls.OPTIONAL_APPS:
                try:
                    __import__(a)
                except ImportError as e:
                    print e
                else:
                    cls.INSTALLED_APPS += (a,)
        if hasattr(cls, 'EXTRA_MIDDLEWARE_CLASSES'):
            cls.MIDDLEWARE_CLASSES += cls.EXTRA_MIDDLEWARE_CLASSES
        cls.STARTUP_ENV.update({ 'CONFIG_HTTP_PORT': cls.PORT,
                                 'CONFIG_SERVER_NAME': cls.SERVER_NAME })
        if cls.SERVER_NAME not in cls.ALLOWED_HOSTS:
            cls.ALLOWED_HOSTS.append(cls.SERVER_NAME)

    @classmethod
    def post_setup(cls):
        if not hasattr(cls,'PORT'):
            raise AttributeError("PORT environmenment variable required")
        if not hasattr(cls,'SERVER_NAME'):
            raise AttributeError("SERVER_NAME environment variable required")


class DevBase(Base):

    if os.environ.get('DEBUG', False):
        OPTIONAL_APPS = ('debug_toolbar','django_extensions',)
        INTERNAL_IPS = ('127.0.0.1',)
        ACCOUNT_EMAIL_VERIFICATION = None
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
            }
        }
        EXTRA_MIDDLEWARE_CLASSES = (
            'debug_toolbar.middleware.DebugToolbarMiddleware',
            'userswitch.middleware.UserSwitchMiddleware',)
        DEBUG_TOOLBAR_CONFIG = {
            'SHOW_TEMPLATE_CONTEXT': True,
            'ENABLE_STACKTRACES' : True,
        }
        # Increase amount of logging output in Dev mode.
        # for logger_name in ('codalab', 'apps'):
        #     Base.LOGGING['loggers'][logger_name]['level'] = 'DEBUG'
