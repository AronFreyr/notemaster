import os
import configparser

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_DIR = BASE_DIR + '/notemaster/config/'
config = configparser.ConfigParser(allow_no_value=True)

log_location = 'logs/'
# importing logger settings
try:
    from .logger_settings import LoggerSettings
except Exception as e:
    pass

with open(BASE_DIR + '/notemaster/secrets/secret_key.txt') as f:
    SECRET_KEY = f.read().strip()

ALLOWED_HOSTS = []
CACHE_TIME = 0
cache_location = ''

# When the environment is not defined it usually means we are running tests.
if not 'ENVIRONMENT' in os.environ:
    os.environ['ENVIRONMENT'] = 'test'


# Access the config file for either the test or production environment.
if os.environ['ENVIRONMENT'] == 'test':
    config.read(CONFIG_DIR + 'dev.ini')
    DEBUG = True
    # If the debug log folder does not exist, create it.
    if not os.path.exists(os.path.join(BASE_DIR, config['DEFAULT']['LOG_LOCATION'])):
        os.makedirs(os.path.join(BASE_DIR, config['DEFAULT']['LOG_LOCATION']))
else:
    config.read(CONFIG_DIR + 'prod.ini')
    DEBUG = False

ALLOWED_HOSTS = [config['DEFAULT']['ALLOWED_HOSTS_IP'], config['DEFAULT']['ALLOWED_HOSTS_URL']]
CACHE_TIME = int(config['DEFAULT']['CACHE_TIME_MINUTES']) * int(config['DEFAULT']['CACHE_TIME_SECONDS'])
cache_location = config['DEFAULT']['CACHE_LOCATION']
log_location = config['DEFAULT']['LOG_LOCATION']

logger_settings = LoggerSettings(log_location)
LOGGING = logger_settings.get_logger_settings()

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'notes',
    'xml_converter',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'notemaster.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'notemaster.wsgi.application'

ASGI_APPLICATION = 'notemaster.routing.application'

# If the environment is prod, use prod database, else use the default django test database.
if os.environ['ENVIRONMENT'] == 'prod':
    DATABASES = {
        'default': {
            'ENGINE': config['DATABASE']['DB_ENGINE'],
            'NAME': config['DATABASE']['DB_NAME'],
            'USER': config['DATABASE']['DB_USERNAME'],
            'PASSWORD': config['DATABASE']['DB_PASSWORD'],
            'HOST': config['DATABASE']['DB_HOST'],
            'PORT': config['DATABASE']['DB_PORT'],
        }
    }
elif os.environ['ENVIRONMENT'] == 'test':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        },
        'test': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'test.sqlite3'),
        }
    }
else:
    raise EnvironmentError('Neither PRODUCTION nor DEBUG environments detected')


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
LOGIN_REDIRECT_URL = '/notemaster/'
LOGOUT_REDIRECT_URL = 'login_screen'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': cache_location
    }
}

# This fixes a problem with the being run twice in Django when it is in debug mode.
# The solution was found here:
# https://stackoverflow.com/questions/26682413/django-rotating-file-handler-stuck-when-file-is-equal-to-maxbytes
if DEBUG and os.environ.get('RUN_MAIN', None) != 'true':
    LOGGING = {}
