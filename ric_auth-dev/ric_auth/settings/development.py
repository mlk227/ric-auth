import os
import urllib
from ric_auth.settings.default import *

DEBUG = True
SECRET_KEY = "Not secret really"
ALLOWED_HOSTS = ['*']
ADMINS = [('admin', 'admin@rewardz.sg'), ]

INSTALLED_APPS += (
    'django_extensions',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': "ric_auth",
        'USER': 'postgres',
        'HOST': "auth-db",
        'PASSWORD': 'postgres',
        'SERIALIZE': False
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://:sOmE_sEcUrE_pAsS@ric_auth_redis:6379/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    },
    'email_reset': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://:sOmE_sEcUrE_pAsS@ric_auth_redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler'
        },
        'log_file': {
            'level': 'INFO',
            'formatter': 'default',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'django_logs.log',
            'maxBytes': 16777216,  # 16megabytes
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'log_file'],
            'level': 'DEBUG'
        },
    },
    'formatters': {
        'default': {
            'format': '[%(name)s] %(asctime)s : %(message)s'
        }
    },
}

if os.getenv("PRINT_SQL", None):
    LOGGING['loggers'].update({
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    })

SPECTACULAR_SETTINGS.update({
    'SERVERS': [{
        'url': os.getenv("API_BASE_URL") if os.getenv("API_BASE_URL") else "http://127.0.0.1:10082/",
    },
    ]})

SIMPLE_JWT.update({
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),


    'SIGNING_KEY': "-----BEGIN RSA PRIVATE KEY-----\n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\n-----END RSA PRIVATE KEY-----",
    'VERIFYING_KEY': "-----BEGIN PUBLIC KEY-----\nMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAxnVWjPgOW5RrTpOMvvxV\nQZRDu3EsiB3ZiLnO5Tq2qxflaV1fJg4UDW7w22M7RsrAIyVCWIm//JyA6Sw9v7Om\nB/oAle2wcTYsSV7znEqdEd4J/KgVOFXbXJS4eUrvD0XY/+IyXFgzqORNDCCO7V3g\no8i17RQBzl9RGxTNwFbEo8UMwLbw/T+lKMs7/sulxZnGt6+SKsjEUbMBYqYa0TVJ\n9Z4OS8PWwnGUpn5JBOEQmHo+3I9tGmC12uCnpT7Jtw4VnYKrG2jK8tzWB6BW0fy/\nIs5nKdNJtCdoG/sgJ08KB2jM00Il33OAfdG8ucn/2ZGACZtyOZw98TwPd3JfMgCY\nj+ELue7/bEQbdXkPlMNsWJXdEUYWh5IMuO1yVWHiCW68jJSYa/m8uya21sTW8V39\nPMGQJtpT+o9T45MH3Yf9wLqtx1etZp7ufmhrYsGho5OFzTIqivptNqHLhMpnXo/w\nkTeE1VcoRwwTgY8eqALBLe649OIkB1iXV/xpu+RKmXg7kzIYDlUuUPrNVimKlrS2\nqsHwWKoswqJ3E5fwGP45d0MsrA8XPovWrkS7H65BgC9Ab8v6UTrE5huxoISPeko0\no+a08ah9lxiRBnHo+qreZGccezRm9UKUv9T8LUeso1A/t/QH+ddYdT703SLiQceM\nw36H7SFOmgc4s70/dx+DrzkCAwEAAQ==\n-----END PUBLIC KEY-----",
})

STATIC_ROOT = "/mnt/shared_volumes/static"
MEDIA_ROOT = "/mnt/shared_volumes/media"
MEDIA_URL = urllib.parse.urljoin(os.getenv("API_BASE_URL"), 'media/') if os.getenv("API_BASE_URL") else '/media/'
