import os
from pathlib import Path
from dotenv import load_dotenv
from django.conf import settings
from django.conf.urls.static import static

# Load environment variables from .env
load_dotenv(dotenv_path=os.path.join(Path(__file__).resolve().parent.parent, ".env"))

BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = os.getenv('SECRET_KEY', 'default-fallback-secret-key')  
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')
MICROSOFT_AUTH_TENANT_ID = os.getenv('MICROSOFT_AUTH_TENANT_ID') 
MICROSOFT_AUTHORITY = f"https://login.microsoftonline.com/170bbabd-a2f0-4c90-ad4b-0e8f0f0c4259"
MICROSOFT_AUTH_REDIRECT_URI = os.getenv("MICROSOFT_AUTH_REDIRECT_URI")
MICROSOFT_AUTH_CLIENT_ID = os.getenv("MICROSOFT_AUTH_CLIENT_ID")
MICROSOFT_AUTH_CLIENT_SECRET = os.getenv("MICROSOFT_AUTH_CLIENT_SECRET")

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = 'accounts/login/' 
LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    #'allauth.socialaccount.providers.microsoft',
    'delta',
]

SITE_ID = 1

AUTH_USER_MODEL = 'delta.CustomUser'
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # This tells Django where to find static files
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'delta.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'delta.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME', 'delta_db'),
        'USER': os.getenv('DATABASE_USER', 'postgres'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST', 'localhost'),
        'PORT': os.getenv('DATABASE_PORT', '5432'),
    }
}

AUTHENTICATION_BACKENDS = [
    'delta.backends.AllowInactiveModelBackend',  # Your custom backend
    #'allauth.account.auth_backends.AuthenticationBackend',  # Keep Allauth
    'django.contrib.auth.backends.ModelBackend',
]

# Authentication
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Microsoft OAuth Configuration
SOCIALACCOUNT_PROVIDERS = {
    'microsoft': {
        'APP': {
            'client_id': os.getenv('MICROSOFT_AUTH_CLIENT_ID'),
            'secret': os.getenv('MICROSOFT_AUTH_CLIENT_SECRET'),
            'key': '',
        },
        "AUTH_PARAMS": {"scope": "openid email profile"},
        "TENANT": '170bbabd-a2f0-4c90-ad4b-0e8f0f0c4259',  
    }
}

# Media settings 
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# A temporary directory for LaTeX compilation output
TEMP_PDF_DIR = os.path.join(BASE_DIR, 'temp_pdf')

print("Loaded DB password:", os.getenv("DATABASE_PASSWORD"))

# Disable rate limit in local/dev
if DEBUG:
    ACCOUNT_RATE_LIMITS = {"login_failed": None}
    
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
ACCOUNT_ADAPTER = "delta.adapters.CustomAccountAdapter"
ACCOUNT_FORMS = {
    'login': 'delta.forms.MyLoginForm', 
}