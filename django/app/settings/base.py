"""
Django settings for app project.

Generated by 'django-admin startproject' using Django 3.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os, string, random
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

def get_environment(var_name):
  """환경 변수를 가져오거나 예외를 반환한다."""
  try:
    return os.environ[var_name]
  except KeyError:
    error_msg = "Set the {} environment variable".format(var_name)
    raise ImproperlyConfigured(error_msg)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
chars = ''.join([string.ascii_letters, string.digits, string.punctuation]).replace('\'', '').replace('"', '').replace('\\', '')

SECRET_KEY = ''.join([random.SystemRandom().choice(chars) for i in range(50)])

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
]

INSTALLED_APPS += [  # plugin
    'widget_tweaks',
    'django_markdown2',
    'mdeditor',
    'django.contrib.sites',
    'disqus',
    'import_export',
    'storages',
    'mathfilters',
]

INSTALLED_APPS += [  # app
    'account.apps.AccountConfig',
    'home.apps.HomeConfig',
    'board.apps.BoardConfig',
    'books.apps.BooksConfig',
    'excel.apps.ExcelConfig',
    'rebs.apps.RebsConfig',
    'rebs_company.apps.RebsCompanyConfig',
    'rebs_project.apps.RebsProjectConfig',
    'rebs_contract.apps.RebsContractConfig',
    'rebs_cash.apps.RebsCashConfig',
    'rebs_notice.apps.RebsNoticeConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'app.urls'

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

WSGI_APPLICATION = 'app.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': get_environment('DATABASE_NAME'),
        'USER': get_environment('DATABASE_USER'),
        'PASSWORD': get_environment('DATABASE_PASSWORD'),
        "DEFAULT-CHARACTER-SET": 'utf8',
        'HOST': 'master',
        'PORT': 3306,
    },
    'master': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': get_environment('DATABASE_NAME'),
        'USER': get_environment('DATABASE_USER'),
        'PASSWORD': get_environment('DATABASE_PASSWORD'),
        "DEFAULT-CHARACTER-SET": 'utf8',
        'HOST': 'master',
        'PORT': 3306,
    },
    'slave1': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': get_environment('DATABASE_NAME'),
        'USER': get_environment('DATABASE_USER'),
        'PASSWORD': get_environment('DATABASE_PASSWORD'),
        "DEFAULT-CHARACTER-SET": 'utf8',
        'HOST': 'slave',
        'PORT': 3306,
    },
    'slave2': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': get_environment('DATABASE_NAME'),
        'USER': get_environment('DATABASE_USER'),
        'PASSWORD': get_environment('DATABASE_PASSWORD'),
        "DEFAULT-CHARACTER-SET": 'utf8',
        'HOST': 'slave',
        'PORT': 3306,
    }
}

# DATABASE_ROUTERS = ['app.routers.MasterSlaveRouter']

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
AUTH_USER_MODEL = 'account.User'

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

X_FRAME_OPTIONS = 'SAMEORIGIN'
MDEDITOR_CONFIGS = {
    'default': {
        'language': 'en',
        'width': '100%',  # Custom edit box width
        'heigth': 500,  # Custom edit box height
        'toolbar': ["undo", "redo", "|",
                    "bold", "del", "italic", "quote", "ucwords", "uppercase", "lowercase", "|",
                    "h1", "h2", "h3", "h5", "h6", "|",
                    "list-ul", "list-ol", "hr", "|",
                    "link", "reference-link", "code", "preformatted-text", "code-block", "table", "datetime", "emoji",
                    "html-entities", "pagebreak", "|", "goto-line", "|", "help", "info",
                    "||", "preview", "watch", "fullscreen"],  # custom edit box toolbar
        'upload_image_formats': ["jpg", "jpeg", "gif", "png"],  # image upload format type
        'image_folder': 'editor',  # image save the folder name
        'theme': 'default',  # edit box theme, dark / default
        'preview_theme': 'default',  # Preview area theme, dark / default
        'editor_theme': 'default',  # edit area theme, pastel-on-dark / default
        'toolbar_autofixed': True,  # Whether the toolbar capitals
        'search_replace': True,  # Whether to open the search for replacement
        'emoji': True,  # whether to open the expression function
        'tex': True,  # whether to open the tex chart function
        'flow_chart': True,  # whether to open the flow chart function
        'sequence': True,  # Whether to open the sequence diagram function
        'watch': True,  # Live preview
        'lineWrapping': True,  # lineWrapping
        'lineNumbers': True  # lineNumbers
    }
}

SITE_ID = 1
DISQUS_API_KEY = get_environment('DISQUS_API_KEY')
DISQUS_API_SECRET = get_environment('DISQUS_API_SECRET')
DISQUS_WEBSITE_SHORTNAME = get_environment('DISQUS_WEBSITE_SHORTNAME')

EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = BASE_DIR / 'sent_emails'

APP_ORDER = [
    'rebs_company',
    'rebs_project',
    'rebs_contract',
    'rebs_cash',
    'rebs',
    'account'
]

AWS_ACCESS_KEY_ID = get_environment('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = get_environment('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = 'drebs'
AWS_REGION = 'ap-northeast-2'
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400',}
DEFAULT_FILE_STORAGE = 'app.asset_storage.MediaStorage'

AWS_DEFAULT_ACL = 'public-read'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# STATIC_URL = 'https://%s/static/' % (AWS_S3_CUSTOM_DOMAIN)
STATIC_URL = '/static/'
STATIC_ROOT = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = 'https://%s/media/' % (AWS_S3_CUSTOM_DOMAIN) # 각 media 파일에 관한 URL prefix
MEDIA_ROOT = BASE_DIR / 'media'  # 업로드된 파일을 저장할 디렉토리 경로
