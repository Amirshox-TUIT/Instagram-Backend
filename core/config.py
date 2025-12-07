import os
import environ
from pathlib import Path

# BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent

# .env faylini yuklash
env = environ.Env(
    DEBUG=(bool, True)  # default qiymat
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# STATIC & MEDIA
MEDIA_ROOT = env('MEDIA_ROOT', default=os.path.join(BASE_DIR, 'media'))
STATIC_ROOT = env('STATIC_ROOT', default=os.path.join(BASE_DIR, 'static'))

# DATABASE SETTINGS
DB_HOST = env('DB_HOST', default='localhost')  # local uchun localhost
DB_NAME = env('DB_NAME')
DB_USER = env('DB_USER')
DB_PASS = env('DB_PASS')
DB_PORT = env('DB_PORT', default='5432')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASS,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    }
}

# DJANGO SETTINGS
DJANGO_SECRET_KEY = env('DJANGO_SECRET_KEY', default='amirshoxamirshoxghjkghjk')
DEBUG = env.bool('DEBUG', default=True)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=['*'])

# TELEGRAM
TELEGRAM_BOT_TOKEN = env('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = env('TELEGRAM_CHANNEL_ID', default='id')
DATABASE_URL=env.db('DATABASE_URL')