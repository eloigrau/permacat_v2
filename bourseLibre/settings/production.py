from . import *

SECRET_KEY='xxxxx'
GAPI_KEY = 'xxxxx'
DB_PWD='xxxxx'
#DB_PWD = os.environ['DB_PWD']

DEBUG = True
LOCALL = True

ALLOWED_HOSTS = ['127.0.0.1']

DATABASES = {

    'default': {
          'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.db'),
    }
}

DJANGO_ADMIN_LOGS_ENABLED = True
EMAIL_USE_LOCALTIME = True

# Email settings
SERVER_EMAIL = ''
EMAIL_BACKEND = ''
EMAIL_HOST = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_HOST_USER = SERVER_EMAIL
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
GMAIL_SMTP_USER = ''
EMAIL_SUBJECT_PREFIX = "[PermaCat]"
GMAIL_SMTP_PASSWORD = ''
#print('Production ok')
ACME_CHALLENGE_URL_SLUG = ''
ACME_CHALLENGE_TEMPLATE_CONTENT = ''

PERMAGORA_USER_MAIL = ""
PERMAGORA_PWD_MAIL = ""


EMAIL_BACKEND = "anymail.backends.sendinblue.EmailBackend"

ANYMAIL = {
    "SENDINBLUE_API_KEY": "",
}


WEBPUSH_SETTINGS = {
    "VAPID_PUBLIC_KEY": "",
    "VAPID_PRIVATE_KEY":"",
    "VAPID_ADMIN_EMAIL": ""
}

