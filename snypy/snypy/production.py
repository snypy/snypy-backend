from .settings import *

DEBUG = False


ALLOWED_HOSTS = [
    'cf-snypy-api.cfapps.io',
]

STATIC_URL = 'http://cf-snypy-api-static.cfapps.io',

CORS_ORIGIN_WHITELIST = (
    'cf-snypy-static.cfapps.io',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '5432',
    }
}
