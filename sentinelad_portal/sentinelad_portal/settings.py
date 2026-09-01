"""
Django settings for SentinelAD Enterprise Portal
Domain: khai.local | Domain Controller: DC-01 (192.168.101.10)
Web Server: WEB01 (192.168.101.20)
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'sentinel-ad-dev-secret-key-change-in-production-2024'

DEBUG = True

ALLOWED_HOSTS = ['*', 'intranet.khai.local', '192.168.101.20', 'localhost', '127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'apps.authentication',
    'apps.core',
    'apps.employees',
    'apps.assets',
    'apps.tickets',
    'apps.announcements',
    'apps.audit',
    'apps.meetings',
    'apps.payroll',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.audit.middleware.AuditMiddleware',
]

ROOT_URLCONF = 'sentinelad_portal.urls'

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
                'apps.core.context_processors.site_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'sentinelad_portal.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ─── LDAP Authentication (Active Directory khai.local) ────────────────────────
# Uncomment and configure when deploying to WEB01 with access to DC-01
# from apps.authentication.ldap_backend import LDAPBackend
AUTHENTICATION_BACKENDS = [
    'apps.authentication.backends.SentinelADBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# AD / LDAP Configuration
AD_CONFIG = {
    'SERVER': '192.168.101.10',
    'PORT': 389,
    'DOMAIN': 'khai.local',
    'DOMAIN_NETBIOS': 'khai',
    'BASE_DN': 'DC=khai,DC=local',
    'BIND_DN': 'CN=Administrator,CN=Users,DC=khai,DC=local',
    'BIND_PASSWORD': 'Vietkhai1108.',  # Administrator@khai.local
    'USE_SSL': False,
    'SEARCH_BASE': 'OU=Company,DC=khai,DC=local',
    # Group to Role mapping
    'GROUP_ROLES': {
        'IT_Admin': 'administrator',
        'Helpdesk': 'helpdesk',
        'HR_Manager': 'hr_manager',
        'Finance_Manager': 'finance_manager',
        'Sales_Manager': 'sales_manager',
        'Department_User': 'employee',
    },
}

# ─── LDAP Mock Mode ──────────────────────────────────────────────────────────
# True  = Dùng tài khoản giả lập (khai.it, an.hr...) - chạy độc lập không cần DC-01
# False = Kết nối LDAP live tới DC-01 (192.168.101.10) - cần điền BIND_PASSWORD ở trên
LDAP_MOCK_MODE = False  # Dang ket noi LDAP live toi DC-01 (192.168.101.10)

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/auth/login/'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

SESSION_COOKIE_AGE = 3600  # 1 hour timeout
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# ─── Structured JSON Logging (for Loki & Promtail) ───────────────────────────
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'format': '{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": %(message)s}',
        },
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'audit_file': {
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'sentinelad_audit.log',
            'formatter': 'json',
        },
        'app_file': {
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'sentinelad_app.log',
            'formatter': 'json',
        },
    },
    'loggers': {
        'sentinelad.audit': {
            'handlers': ['audit_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'sentinelad.app': {
            'handlers': ['app_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

import os

GROQ_API_KEY = os.getenv('GROQ_API_KEY', 'your-groq-api-key-here')

# ─── Grafana API Configuration (for AI Analyzer integration) ──────────────────
GRAFANA_URL = os.getenv('GRAFANA_URL', 'http://127.0.0.1:3000')
GRAFANA_SERVICE_ACCOUNT_TOKEN = os.getenv('GRAFANA_SERVICE_ACCOUNT_TOKEN', 'your-grafana-token-here')
PROMETHEUS_DATASOURCE_UID = os.getenv('PROMETHEUS_DATASOURCE_UID', 'PBFA97CFB590B2093')
LOKI_DATASOURCE_UID = os.getenv('LOKI_DATASOURCE_UID', 'P8E80F9AEF21F6940')

# ─── Telegram Real-Time Alerts Configuration ──────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'your-telegram-bot-token-here')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', 'your-telegram-chat-id-here')
