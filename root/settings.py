from pathlib import Path
import os
from datetime import timedelta
import environ 


BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# SECRET_KEY = "HELLOPERIzinwheere2340i3-45)(*)(*)(&()()dfjbgf4()&)()///"

SECRET_KEY = env("SECRET_KEY")
# CSRF_TRUSTED_ORIGINS = ["*"]


DEBUG = True

ALLOWED_HOSTS = ["*"]
CORS_ALLOW_ALL_ORIGINS = True


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'django.contrib.humanize',
]
CUSTOM_APPS = ["bill", "organization", "user", "product", "api", "discount", "purchase", "accounting"]
THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "import_export",
    "django_crontab",

]
INSTALLED_APPS += CUSTOM_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "root.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "organization.org_processor.org_renderer",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "libraries": {
                "get_list": "bill.templatetags.tags",
                "custom_template_filters": "root.custom_template_filters"
            },
        },
    },
]

WSGI_APPLICATION = "root.wsgi.application"


# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.mysql",
#         "NAME": "pos",
#         "USER": "pos",
#         "PASSWORD": "hiMi009@",
#         "HOST": "20.205.143.122",
#         "PORT": "3306",
#     }
# }
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]

AUTH_USER_MODEL = "user.User"


LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kathmandu"

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = "/staticfiles/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

MEDIA_ROOT = os.path.join(BASE_DIR, "uploads")
MEDIA_URL = "/uploads/"

LOGIN_REDIRECT_URL = "/organization"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 12,
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
}
SIMPLE_JWT = {"ACCESS_TOKEN_LIFETIME": timedelta(days=365)}


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_USE_TLS = env("EMAIL_USE_TLS")

# IMPORT_EXPORT_USE_TRANSACTIONS = True
import dj_database_url

DATABASE_URL = env("DATABASE_URL")
#DATABASES = {
#    "default": dj_database_url.config(default=DATABASE_URL, conn_max_age=1800),
#}


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env('DB_NAME'),
        "USER": env('DB_USERNAME'),
        "PASSWORD": env('DB_PASSWORD'),
        "HOST": "localhost",
        "PORT": "3306",
    }
}

CRONJOBS = [
    # ('* * * * *', 'organization.cron.end_day'),
    ('* * * * *', 'organization.cron.fetch_details'),

]

# CRONTAB_COMMAND_PREFIX='aamonepal'
