# asset_mgmt/settings.py

import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ===================================================================
# LOAD ENVIRONMENT VARIABLES FROM .env FILE
# ===================================================================
# This crucial line finds the .env file in your project's root directory
# and loads its key-value pairs as environment variables.
load_dotenv(os.path.join(BASE_DIR, '.env'))

# ===================================================================
# CORE SETTINGS
# ===================================================================

# SECURITY WARNING: The secret key is now read securely from the environment.
SECRET_KEY = os.getenv('SECRET_KEY', 'default-insecure-key-for-emergency')

# SECURITY WARNING: DEBUG is now controlled by the .env file.
# This logic correctly handles string-to-boolean conversion (e.g., 'True' -> True).
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')

# Allowed hosts are read from a comma-separated string in the .env file.
ALLOWED_HOSTS_str = os.getenv('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_str.split(',') if host.strip()]
if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ['*'] # Allows all hosts in debug mode for convenience.


# ===================================================================
# APPLICATION DEFINITION
# ===================================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'widget_tweaks',
    
    # Your apps - Using the AppConfig is best practice for signal handling.
    'inventory.apps.InventoryConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'inventory.middleware.RequestMiddleware',  # Your custom middleware is correctly placed.
]

ROOT_URLCONF = 'asset_mgmt.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [], # Django will automatically find templates in each app's 'templates' directory.
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

WSGI_APPLICATION = 'asset_mgmt.wsgi.application'


# ===================================================================
# DATABASE CONFIGURATION
# ===================================================================
# Reads all database credentials securely from your .env file.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': os.getenv('DATABASE_PORT'),
    }
}


# ===================================================================
# PASSWORD VALIDATION
# ===================================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ===================================================================
# INTERNATIONALIZATION & STATIC FILES
# ===================================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
# This directory is for collecting all static files for production deployment.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# ===================================================================
# DEFAULT PRIMARY KEY & AUTHENTICATION URLS
# ===================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# These URLs are now correctly namespaced to point to your 'inventory' app.
LOGIN_URL = 'inventory:login'
LOGOUT_REDIRECT_URL = 'inventory:login'
# After login, redirect to the smart dashboard view that handles roles.
LOGIN_REDIRECT_URL = 'inventory:dashboard'