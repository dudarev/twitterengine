import os

DEBUG = True

TEMPLATE_DEBUG = DEBUG
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

#ADMINS = (
#)

#MANAGERS = ADMINS

#SEND_BROKEN_LINK_EMAILS = True

TIME_ZONE = 'Europe/Kiev'
LANGUAGE_CODE = 'en-US'

USE_I18N = True

SECRET_KEY = '*(&^8723rhbkJGO8rg3y-[8YU{)JI[IUTer0fg7P{UIG>LFB,HGFLKJlkfs9fu=[09u_*(Y'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
)

ROOT_URLCONF = 'project.urls'

TEMPLATE_DIRS = (
    PROJECT_ROOT + '/templates/'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.core.context_processors.i18n',
)

INSTALLED_APPS = (
)

