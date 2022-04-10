"""
Django settings for VoiceComp project.

Generated by 'django-admin startproject' using Django 2.2.8.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '85ou+a35a_v&d@qf=q#umawhkkvaij@3#fb2v03sz41lhybxa-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', '*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'menu.apps.MenuConfig',
    "compressor"
]

MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'htmlmin.middleware.MarkRequestMiddleware',

    'menu.views.byte_range_middleware.RangesMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]



# pip install django_compressor
COMPRESS_ENABLED = True
# COMPRESS_OFFLINE = True

# pip install django-htmlmin
HTML_MINIFY = False


COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter',
]


COMPRESS_UGLIFY_BINARY = "uglifyjs"
COMPRESS_UGLIFY_JS_ARGUMENTS = "--compress --mangle --toplevel"

COMPRESS_YUGLIFY_BINARY = "yuglify"

COMPRESS_CLOSURE_COMPILER_BINARY = 'google-closure-compiler'
COMPRESS_CLOSURE_COMPILER_ARGUMENTS = '-O ADVANCED'


STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

ROOT_URLCONF = 'VoiceComp.urls'

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

WSGI_APPLICATION = 'VoiceComp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Helsinki'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

URL = 'https://www.voicecomp.net/'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'menu/static'),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGIN_REDIRECT_URL = 'choices_list'
LOGOUT_REDIRECT_URL = 'choices_list'

# APP SPECIFIC SETTINGS
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880
THEME = 'dark'
DEFAULT_CONTROL = 'Admin'
CONFIDENCE_INSTRUCTION = 'How sure are you?'

STARTING_SEQUENCE = 0
NEXT_SEQUENCE = 2
STARTING_LEVEL = 1
MAX_LEVEL = 3

LEVEL_INCREMENT_INTERNALLY = 2
LEVEL_MULTIPLY_INTERNALLY = 3

TOTALTRIALS_PER_LEVEL = 10

ENABLE_LIFE = 'false'
TOTAL_LIFE = 5
TOTAL_FAIL = 0

GAMIFIED = 'true'





