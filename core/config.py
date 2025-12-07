import os


MEDIA_ROOT = os.environ.get('MEDIA_ROOT', '/vol/web/media/')
STATIC_ROOT = os.environ.get('STATIC_ROOT', default='/vol/web/static/')

# DATABASE SETTINGS
DB_HOST = os.environ.get('DB_HOST', default='db')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_PORT = os.environ.get('DB_PORT')

DJANGO_SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', default='amirshoxamirshoxghjkghjk')
DEBUG = os.environ.get('DEBUG', default=True)
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", '*').split(',')

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.environ.get('TELEGRAM_CHANNEL_ID', default='id')