import os
from pathlib import Path

from dynaconf import settings

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = settings.ENVIRONMENT.SECRET_KEY
DEBUG = bool(settings.ENVIRONMENT.get('DEBUG', 0))
DEBUG_TOOLBAR_ENABLED = bool(settings.ENVIRONMENT.get('DEBUG_TOOLBAR_ENABLED', 0))
ALLOWED_HOSTS = [host(settings) if callable(host) else host for host in settings.ENVIRONMENT.ALLOWED_HOSTS]

# Application definition

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

OUTER_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'drf_yasg',
]

CREATED_APPS = ['app_users', 'app_infrastructure', 'budgets', 'entities', 'categories', 'predictions']

INSTALLED_APPS = DJANGO_APPS + OUTER_APPS + CREATED_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG_TOOLBAR_ENABLED:
    INSTALLED_APPS += ['debug_toolbar']  # NOQA
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1', '0.0.0.0', 'localhost']
    DEBUG_TOOLBAR_CONFIG = {'SHOW_TOOLBAR_CALLBACK': lambda request: True}


ROOT_URLCONF = 'app_config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
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

WSGI_APPLICATION = 'app_config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

if 'DATABASE' in settings:
    DATABASES = {
        'default': {
            'ENGINE': settings.DATABASE.ENGINE,
            'NAME': settings.DATABASE.NAME,
            'USER': settings.DATABASE.USER,
            'PASSWORD': settings.DATABASE.PASSWORD,
            'HOST': settings.DATABASE.HOST,
            'PORT': settings.DATABASE.PORT,
        }
    }
else:
    DATABASES = {  # pragma: no cover
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'app_users.User'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'app_infrastructure.paginations.DefaultPagination',
    'EXCEPTION_HANDLER': 'app_infrastructure.exception_handlers.default_exception_handler',
}

SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'DEFAULT_AUTO_SCHEMA_CLASS': 'app_config.swagger_schemas.CustomAutoSchema',
    'SECURITY_DEFINITIONS': {
        'token': {'type': 'apiKey', 'description': 'User token', 'name': 'Authorization', 'in': 'header'}
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default_formatter': {'format': '[%(asctime)s] "%(levelname)s: %(message)s"', 'datefmt': '%d/%b/%Y %H:%M:%S'},
    },
    'handlers': {
        'default_stream_handler': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'default_formatter',
        },
    },
    'loggers': {
        'default_logger': {
            'handlers': ['default_stream_handler'],
            'level': 'INFO',
        },
    },
}
