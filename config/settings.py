# encoding=utf-8
"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 1.10.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), os.pardir)

SETTINGS_DIR = os.path.abspath(os.path.dirname(__file__))

try:
    from secret_key import SECRET_KEY
except:
    from django.utils.crypto import get_random_string

    CHARS = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    FILE = open(os.path.join(SETTINGS_DIR, 'secret_key.py'), 'w')
    FILE.write('SECRET_KEY = "' + get_random_string(50, CHARS) + '"\n')
    FILE.close()
    import sys
    sys.path.append(SETTINGS_DIR)
    from secret_key import SECRET_KEY

# for flake8
assert SECRET_KEY

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

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
    'django.contrib.sites',
    'django.contrib.flatpages',
    'debug_toolbar',
    'posts',
    'precise_bbcode',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Cache

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

CACHE_TTL = 60 * 15

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

PASSW_VALIDATOR = 'django.contrib.auth.password_validation.'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': PASSW_VALIDATOR + 'UserAttributeSimilarityValidator',
    },
    {
        'NAME': PASSW_VALIDATOR + 'MinimumLengthValidator',
    },
    {
        'NAME': PASSW_VALIDATOR + 'CommonPasswordValidator',
    },
    {
        'NAME': PASSW_VALIDATOR + 'NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'uk'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

LOCALE_PATHS = [
    PROJECT_ROOT+'/locale',
]


USE_TZ = True

INTERNAL_IPS = ['127.0.0.1']

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
STATIC_URL = '/static/'

# Media files

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

config = {
    'title': "Кропивач",
    'url_favicon': "favicon.ico",
    'url_stylesheet': "style.css",
    'default_stylesheet': {
        '1': 'ukrchan.css'
    },
    'stylesheets': [['Ukrchan', 'ukrchan.css'], ['Futaba', 'futaba.css']],
    'additional_javascript': [
        'jquery.js',
        'multi-image.js',
        'style-select.js',
        'dollchan.js',
        'report.js',
    ],
    'footer': ['Кропивач 2016-2017'],
    'max_filesize': 40 * 1024 * 1024,  # 40MB
    'max_images': 4,
    'allowed_ext': ['png', 'jpeg', 'gif', 'jpg', 'webm'],
    'uri_stylesheets': '',
    'font_awesome': True,
    'post_date': "%d-%m-%y о %H:%M:%S",
    'recent': "recent.css",
    'url_javascript': 'main.js',
    'catalog_link': 'catalog.html',
    'button_reply': "Відповісти",
    'button_newtopic': "Створити нитку",
    'allow_delete': True,
    'slogan': [
        "Український іміджборд",
        "Насирматри!",
        "... просто приклади до болючого місця",
        "Режисерська версія Січі",
        "Я ти дам колєґи, я ти дам рове́ри!",
        "Лікує буряк!",
        "Бордити по-новому!",
        "Завантаження…",
        "З коментарями Ґордона Фрімена!",
        "Відтепер безкоштовний!",
        "БЕЗ ГМО!",
        "Виготовлений з повторно використаних html теґів!",
        "[ОК]   [Скасувати]",
        "Передай привіт товаришу майору!",
        "Надає денну норму вітаміну К!",
        "Твій улюблений!",
        "Лише 10,44₴ на Аукро!",
        "Майбутня головна партія країни!",
        "Надто крутий, щоб бути справжнім!",
        "Від творців Кропивача!",
        "Без барвників та консервантів!",
        "Передбачений Ностардамусом!",
        "… садок зелений коло хати!",
        "За це відвідування ви отримали 10 кропиводоларів!",
        "Місце, де ти не хуй дурний!",
        "Викликає звикання!",
        "Додано досягнення та колекційні картки!",
        "Припечи свою рану!",
        "Для реєстрації натисни Ctrl+W",
        "Четверте з половиною диво України!",
        "Щоб продовжити, вкиньте монетку!",
        "Будь-яка схожість з іншими іміджбордами, \
            живими чи мертвими, є абсолютно випадковою!",
        "Ласкаво просимо в інтернет, курво!",
        "Ми крадемо у Футурами!",
        "Європа б ним пишалася, але він наш!",
        "Відтепер дводомний!",
        "Комарики-дзюбрики, Кропивач!",
        "MACHT FREI!",
        "Ґрантується держдепом США!",
        "Схвалено Трампом!",
        "МОЗ рекомендує!",
        "Часте відвідування знижує рівень холостерину в крові!",
        "Штаб диванних військ!",
        "У нас ніколи не болить голова!",
        "Zip-file!"
    ]
}
