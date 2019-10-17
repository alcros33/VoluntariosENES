"""
Django settings.
"""

import os, json
from pathlib import Path

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR_PATH = Path(__file__).resolve().parent.parent
BASE_DIR = str(BASE_DIR_PATH)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
with (BASE_DIR_PATH/"Root"/"SECRET.txt").open('r') as f:
    SECRET_KEY = f.read()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

if DEBUG:
    print("## WARNING: Running Server in DEBUG MODE!!!! ##")

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'Registro.apps.RegistroConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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

ROOT_URLCONF = 'Root.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'Templates'),],
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


WSGI_APPLICATION = 'Root.wsgi.application'

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = "correo@dominio.com"
else:
    with (BASE_DIR_PATH/"Root"/"EMAIL_SETTINGS.json").open('r') as f:
        EMAIL_SETTINGS_DIC = json.load(f)
    EMAIL_BACKEND = EMAIL_SETTINGS_DIC["BACKEND"]
    EMAIL_USE_TLS = bool(EMAIL_SETTINGS_DIC["USE_TLS"])
    EMAIL_HOST = EMAIL_SETTINGS_DIC["HOST"]
    EMAIL_HOST_USER = EMAIL_SETTINGS_DIC["USER"]
    EMAIL_HOST_PASSWORD = EMAIL_SETTINGS_DIC["PASSWORD"]
    EMAIL_PORT = EMAIL_SETTINGS_DIC["PORT"]
    DEFAULT_FROM_EMAIL = EMAIL_SETTINGS_DIC["DEFAULT_FROM"]


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
with (BASE_DIR_PATH/"Root"/"DB_SETTINGS.json").open('r') as f:
    DATABASES = json.load(f)

# Auto logout after 30 minutes
SESSION_COOKIE_AGE = 30*60


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = 'Registro.User'

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'es-mx'

TIME_ZONE = 'America/Mexico_City'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
#STATIC_ROOT = os.path.join(BASE_DIR, 'Static')

if DEBUG:
    STATICFILES_DIRS = (os.path.join(BASE_DIR,'Static'),)

MEDIA_URL = '/img/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'Img')

