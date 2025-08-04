"""
Django settings for analytiQA project.
Django Version: 4.0
"""
import os
from pathlib import Path
from datetime import timedelta
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-_m0rc09s$wa@4^6snye)o2=l(e-gf00g1zwry5aq_pl4b7ic3t"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# if ALLOWED_HOSTS:
#     ALLOWED_HOSTS.append(os.environ.get('ALLOWED_HOSTS'))

CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]
CORS_ORIGIN_ALLOW_ALL= True 
CORS_ALLOW_CREDENTIALS =  True

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third Party Apps
    'drf_spectacular',
    'debug_toolbar',
    'corsheaders',
    'import_export',
    'django_extensions',
    'simple_history',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_yasg',
    'ckeditor',
    'django_celery_results',

    # Local Apps
    'apps.account',
    'apps.stb',
    'apps.core',
    'apps.general',
    'apps.nightly_sanity',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'analytiQA.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
                BASE_DIR / 'frontend/build',  # Assuming you have a build directory for frontend
                BASE_DIR / 'templates',
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

WSGI_APPLICATION = 'analytiQA.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": os.environ.get('DATABASE_ENGINE'),
        "NAME": os.environ.get('NAME'),
        "USER": os.environ.get('USERNAME'),
        "PASSWORD": os.environ.get('PASSWORD'),
        "HOST": os.environ.get('HOST'),
        "PORT": os.environ.get('PORT'),
    },
    'sanity': {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("SANITY_DB_NAME", None),
        "USER": os.environ.get("SANITY_DB_USER", None),
        "PASSWORD": os.environ.get("SANITY_DB_PASSWORD", None),
        "HOST": os.environ.get("SANITY_DB_HOST", "None"),
        "PORT": os.environ.get("SANITY_DB_PORT", "None"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = 'account.Account'

DATABASES_ROUTERS = [
    "analytiQA.helpers.db_router.STBRouter",
]

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=180),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'QA Portal API',
    'DESCRIPTION': 'This is a Website to Show the TestCase Data to Innowave Users',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_DIST': 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest',
    'SWAGGER_UI_FAVICON_HREF': 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/favicon-32x32.png',
    'REDOC_DIST': 'https://cdn.jsdelivr.net/npm/redoc@latest'
}

INTERNAL_IPS = [
    # ...
    "127.0.0.1"
    # ...
]

# Cache

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://redis:6379/0',
        'TIMEOUT': 60 * 60 * 5, # 5 Hours
    }
}

# Celery Configuration Options
CELERY_BROKER_URL = 'redis://redis:6379/1'
CELERY_TIMEZONE = 'Asia/Kolkata'
CELERY_RESULT_BACKEND = 'redis://redis:6379/1'

CELERY_BEAT_SCHEDULE = {
    "get_stb_node_info" : {
        "task": "apps.stb.tasks.get_stb_node_info",
        "schedule": crontab(minute="*/1")
    },
    "get_testcase_result" : {
        "task": "apps.stb.tasks.get_testcase_result",
        "schedule": crontab(minute="*/1")
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": "general.log",
            "level": "ERROR",
            "formatter": "verbose"
        },
    },
    "loggers": {
        "": {
            "level": "DEBUG",
            "handlers": ['file'],
            "propagate": True
        }
    },
    "formatters": {
        "verbose": {
            "format": "{asctime}:{levelname} - {name} {module}.py (line {lineno:d}) {message}",
            "style": "{"
        }
    }
}

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = '/images/'
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"
FIXTURE_DIRS = [
    os.path.join(BASE_DIR, 'fixtures')
]

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'frontend/build/static'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    }
}

# MEDIA_ROOT = os.path.join(BASE_DIR, 'static/images')

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
USER_ACTIVATE_TOKEN_TIMEOUT = 60 * 60

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
