import os
from pathlib import Path
from dotenv import load_dotenv
from django.conf import settings
from django.conf.urls.static import static

# load environment variables from .env file
load_dotenv()

# base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# for security
SECRET_KEY = os.getenv('SECRET_KEY', 'default-fallback-secret-key')  
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

# apps used in this project
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # allauth for login stuff
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.microsoft',

    # my app
    'delta',
]

# needed for allauth to work right
SITE_ID = 1

# we use a custom user model
AUTH_USER_MODEL = 'delta.CustomUser'

# where static files like css live
STATIC_URL = '/static/'

# extra folder for static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# collected static files go here
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# middlewares = behind the scenes helpers
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # needed for allauth
    'allauth.account.middleware.AccountMiddleware',
]

# points to urls.py
ROOT_URLCONF = 'delta.urls'

# html template settings
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # our templates folder
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

# wsgi app entry point
WSGI_APPLICATION = 'delta.wsgi.application'

# database config (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME', 'delta_db'),
        'USER': os.getenv('DATABASE_USER', 'postgres'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'caonhatnam2003'),
        'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
        'PORT': os.environ.get('DATABASE_PORT', '5432'),
    }
}

# password rules
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# after login/logout go to homepage
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

# language + timezone settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# static and media setup
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# microsoft login settings
SOCIALACCOUNT_PROVIDERS = {
    'microsoft': {
        'APP': {
            'client_id': os.getenv('MICROSOFT_CLIENT_ID'),
            'secret': os.getenv('MICROSOFT_SECRET'),
            'key': '',
        },
        "AUTH_PARAMS": {"scope": "openid email profile"},
        "TENANT": '170bbabd-a2f0-4c90-ad4b-0e8f0f0c4259',  # your tenant id
    }
}

# media files like uploads
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# used for LaTeX to save temp files
TEMP_PDF_DIR = os.path.join(BASE_DIR, 'temp_pdf')
