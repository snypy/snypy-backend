import os
import environ


env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, "../.env"))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS")

# Application definition

INSTALLED_APPS = [
    # core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third party
    "rest_framework",
    "django_rest_multitokenauth",
    "corsheaders",
    "django_userforeignkey",
    "django_filters",
    "rest_registration",
    "django_rest_passwordreset",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "django_linear_migrations",
    # local
    "snippets",
    "shares",
    "teams",
    "users",
    "content_pages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_userforeignkey.middleware.UserForeignKeyMiddleware",
]

ROOT_URLCONF = "snypy.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "snypy.wsgi.application"


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    "default": env.db(),
}

# Email config
EMAIL_CONFIG = env.email_url("EMAIL_URL", default="smtp://user:password@localhost:25")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="SnyPy <noreply@snypy.com>")

vars().update(EMAIL_CONFIG)

# User model
AUTH_USER_MODEL = "users.User"

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = env("STATIC_URL", default="/static/")
STATIC_ROOT = env("STATIC_ROOT", default="/static/")

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "django_rest_multitokenauth.coreauthentication.MultiTokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": (
        "rest_framework.filters.SearchFilter",
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

CORS_ORIGIN_WHITELIST = env.list("CORS_ORIGIN_WHITELIST")
CORS_ALLOW_CREDENTIALS = True

REST_REGISTRATION = {
    "REGISTER_VERIFICATION_ENABLED": True,
    "RESET_PASSWORD_VERIFICATION_ENABLED": False,
    "REGISTER_EMAIL_VERIFICATION_ENABLED": False,
    "REGISTER_VERIFICATION_URL": env("REGISTER_VERIFICATION_URL"),
    "REGISTER_EMAIL_VERIFICATION_URL": env("REGISTER_EMAIL_VERIFICATION_URL"),
    "VERIFICATION_FROM_EMAIL": DEFAULT_FROM_EMAIL,
    "REGISTER_VERIFICATION_EMAIL_TEMPLATES": {
        "subject": "email/register/subject.txt",
        "text_body": "email/register/body.txt",
        "html_body": "email/register/body.html",
    },
}
REGISTRATION_DEFAULT_GROUPS = env.list("REGISTRATION_DEFAULT_GROUPS", default=["User"])
RESET_PASSWORD_VERIFICATION_URL = env("RESET_PASSWORD_VERIFICATION_URL", default="http://tld/reset/?token={token}")

SPECTACULAR_SETTINGS = {
    "TITLE": "SnyPy API",
    "DESCRIPTION": "REST API for SnyPy",
    "VERSION": "1.0.0",
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "COMPONENT_SPLIT_REQUEST": True,
}
