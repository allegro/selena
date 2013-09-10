#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

from lck.django import current_dir_support

execfile(current_dir_support)
from lck.django import namespace_package_support
execfile(namespace_package_support)
from datetime import timedelta


DEBUG = False
PROJECT_DIR = CURRENT_DIR + '/../'
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = []
ADMINS = ()
MANAGERS = ADMINS
DATABASES = None
TIME_ZONE = 'Europe/Warsaw'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True
MEDIA_ROOT = ''
MEDIA_URL = ''
STATIC_ROOT = ''
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, 'selena', 'static'),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)
SECRET_KEY = None
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)
ROOT_URLCONF = 'selena.urls'
WSGI_APPLICATION = 'selena.wsgi.application'
TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'selena', 'templates'),
)
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django_rq',
    'services',
    'south',
    'boards',
    'planner',
    'stats',
    'tastypie',
    'lck.django.common',
)
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_HTTPONLY = True
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/admin/'
LOGOUT_URL = '/admin/logout/'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
DEFAULT_LIST_ITEMS_PER_PAGE = 60
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)
DEFAULT_PARAMS_PERFORMANCE_ISSUES_TIME = 15
DEFAULT_PARAMS_CONNECTION_TIMEOUT = 30
DEFAULT_SERVICE_WORKING_PROBES = 5
DEFAULT_TIME_DELTA = 3
DEFAULT_PARAMS_USERAGENT = 'Mozilla/5.0 (X11; U; Linux x86_64; pl-PL; rv:1.9.2.3) Gecko/20100423 Ubuntu/10.04 (lucid) Firefox/3.6.3'
DEFAULT_PARAMS_REFERER = ''
CACHES = None
CACHE_STATE_TIME = 3600
AES_SECRET_KEY = b'Sixteen byte key'
ERROR_TIME_INTERVAL = 30
RQ_QUEUES = None

from lck.django import profile_support
execfile(profile_support)
