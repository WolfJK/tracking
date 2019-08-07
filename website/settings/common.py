# coding: utf-8
# __author__: "James"
from __future__ import unicode_literals

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'co3or_xi#wmgadg=hy^5!o8&ybmr^b^zeh5as_#$i8(r@de(k0'

# SECURITY WARNING: don't run with debug turned on in production!

# Application definition
INSTALLED_APPS = (
    # 'django.contrib.user',
    # 'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    "corsheaders",
)

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'website.urls'
WSGI_APPLICATION = 'website.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'zh-CN'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

# CORS settings
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = ( '*')
CORS_ALLOW_METHODS = (
    'GET',
    'POST',
    'OPTIONS',
)
CORS_ALLOW_HEADERS = (
    'XMLHttpRequest',
    'accept-encoding',
    'authorization',
    'content-type',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
)

## APPs settings
INSTALLED_APPS += (
    'common',
    'apps',
)

## Middlewares settings
MIDDLEWARE_CLASSES += (
    'website.middleware.GatewayMiddleware',
    # 'website.middleware.AuthMiddleware',
)

# user backends
AUTH_USER_MODEL = 'common.SmUser'
AUTHENTICATION_BACKENDS = (
    "common.user.backends.AuthenticationBackend",
)

# user skip urls
SKIP_AUTHENTICATION_URLS = [
    '/user/code/',
    '/user/login/',
    '/hello/hello-world/',
    '/hello/exception/',
    '/hello/needcode-exception/',
    '/user/asign-user/',
]

SKIP_AUTHORIZATION_URLS = [
    '/user/logout/',
    '/user/get-user-menus-apis/',
    '/user/asign-user/',

    #"/hello/auth-hello/",
    "/apps/common/common-param/",
    "/apps/common/brand-list/",
    "/apps/common/category-list/",
    "/apps/common/sales-point-list/",
    "/apps/common/report-template-list/",
    "/apps/common/throw-account-upload/",

] + SKIP_AUTHENTICATION_URLS

# session
SESSION_ENGINE = 'redis_sessions.session'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_AGE = 10 * 60

# 认证失败次数
FAIL_AUTH_ATTEMPTS_KEY = "FAIL_AUTH_ATTEMTPS"
FAIL_AUTH_ATTEMPTS_CODE = 3
FAIL_AUTH_ATTEMPTS_MAX = 10
FAIL_AUTH_ATTEMPTS_EXPIRE = 5 * 60


# user.username
SESSION_KEY_USER = "USER"
# menu api list
SESSION_KEY_MENU_API_LIST = "MENU-API-LIST"

# enable js access cookie
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = False

tcp_port = 3001
