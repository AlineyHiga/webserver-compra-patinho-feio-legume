from django.conf import settings
from django.conf.urls.static import static
from pathlib import Path
from decouple import config, Csv
from django.core.management.utils import get_random_secret_key
import sys
import os

import paypalrestsdk


#paypal config
paypalrestsdk.configure({
    "mode": config('MODE_PAYPAL',default='sandbox'),  # Altere para "live" em produção
    "client_id": config('CLIENT_ID'),
    "client_secret": config('CLIENT_SECRET')
})

# Caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Segurança - Chave Secreta
SECRET_KEY = config('SECRET_KEY', default=get_random_secret_key())
ENCRYPTION_KEY = config('ENCRYPTION_KEY')
# Segurança - Modo de Depuração (Desativar em Produção)
DEBUG = config('DEBUG', default=True, cast=bool)

# Configuração dos Hosts Permitidos
ALLOWED_HOSTS = ['*']



# Aplicativos Instalados
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',          # Django REST Framework para APIs
    'corsheaders',             # Django CORS Headers para permitir CORS (opcional)
    'main',
    'storages',                    # Nosso aplicativo principal
    'CompraWebserver',  # Registra CompraWebserver para que o Django reconheça os modelos
]

# Middleware
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Middleware para CORS
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configuração das URLs
ROOT_URLCONF = 'CompraWebserver.urls'

# Configuração de Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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

# Configuração de WSGI
WSGI_APPLICATION = 'CompraWebserver.wsgi.application'

if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',  # Banco de dados em memória, rápido e isolado
        }
    }
# Configuração do Banco de Dados (Exemplo com PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DATABASE', default='nome_do_banco'),
        'USER': config('POSTGRES_USER', default='usuario'),
        'PASSWORD': config('POSTGRES_PASSWORD', default='senha'),
        'HOST': config('POSTGRES_HOST', default='localhost'),
        'PORT': config('POSTGRES_PORT', default='5432'),
        'TEST': {
            'NAME': 'tests_' + config('POSTGRES_DATABASE', default='nome_do_banco')  # Usa um banco temporário
        },

    }
}

# Configurações de Senhas
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

# Configurações de Internacionalização
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Configurações de Arquivos Estáticos
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_FILE_STORAGE ='main.storage.vercelStorage.VercelBlobStorage'
# Configurações de Arquivos de Mídia
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Configurações do Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
}

# Configurações de CORS (Cross-Origin Resource Sharing)
CORS_ALLOWED_ORIGINS = config('CORS_ORIGIN_ALLOW_ALL', cast=Csv(), default="http://localhost:3000")
# Configurações para o CORS se precisar permitir acesso de qualquer origem (não recomendado em produção)
CORS_ALLOW_ALL_ORIGINS = True

# Configurações de Logs (Opcional)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],  # Use console em vez de file
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
urlpatterns=[ ]
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)