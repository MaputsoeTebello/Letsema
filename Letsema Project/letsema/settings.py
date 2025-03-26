import os
from pathlib import Path
SECRET_KEY = os.getenv('SECRET_KEY', 'fallback_key_for_dev')

# Define BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent

# Static files settings
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",  # Or use os.path.join(BASE_DIR, "static")
]


# Debugging should be enabled for local testing
DEBUG = False

# Allow all hosts during local testing
ALLOWED_HOSTS = ['*']

# Installed apps include all core, required, and third-party dependencies
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',  # Django REST framework
     'rest_framework_simplejwt',
    'api',  # Replace with your actual app name
]

# Middleware configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Root URL configuration
ROOT_URLCONF = 'letsema.urls'

# Template settings
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # Optional: Add templates directory
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

# WSGI application
WSGI_APPLICATION = 'letsema.wsgi.application'


# Database configuration for local development (PostgreSQL example)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'letsema_db'),  # Default to 'letsema_db'
        'USER': os.getenv('POSTGRES_USER', 'postgres'),  # Default user is 'postgres'
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'postgres'),  # Default password
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),  # Localhost for testing
        'PORT': os.getenv('POSTGRES_PORT', '5432'),  # Default PostgreSQL port
    }
}

# Password validation (can be disabled in local testing)
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

