import environ
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

env = environ.Env(
    DEBUG=(bool, False),
    EMAIL_USE_TLS=(bool, True),
    ALLOWED_HOSTS=(list, []),
    OPENAI_KEYS=(list, []),
)

environ.Env.read_env()

SECRET_KEY = env("SECRET_KEY")

IOS_KEY = env("IOS_KEY")

OPENAI_KEYS = env("OPENAI_KEYS")

SECRET_ADMIN_URL = env("SECRET_ADMIN_URL")

DEBUG = bool(env("DEBUG"))

SALT = env("SALT")

ALLOWED_HOSTS = env("ALLOWED_HOSTS")

DATABASES = {
    "default": env.db(),
}

SECURE_HSTS_SECONDS = 60

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SECURE_HSTS_PRELOAD = True

SESSION_COOKIE_SECURE = True

SECURE_SSL_REDIRECT = True

CSRF_COOKIE_SECURE = True

# SILKY_PYTHON_PROFILER = True
#
# SILKY_PYTHON_PROFILER_BINARY = True
#
# SILKY_ANALYZE_QUERIES = True

if not DEBUG:
    sentry_sdk.init(
        dsn=env("SENTRY_DSN"),
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=True,
    )

REST_FRAMEWORK = {
    "UPLOADED_FILES_USE_URL": False,
    "DATETIME_FORMAT": "%b %d at %I:%M %P",
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "gremlin.middleware.CustomPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_RATES": {
        "otp_in_min": "60/min",
        "otp_in_hour": "60/hour",
    },
    "EXCEPTION_HANDLER": "gremlin.middleware.custom_exception_handler",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication"
    ],
}

# Apple
APP_BUNDLE_ID = env("APP_BUNDLE_ID")
APP_TEAM_ID = env("APP_TEAM_ID")
APP_KEY_ID = env("APP_KEY_ID")
IAP_ENVIRONMENT = env("IAP_ENVIRONMENT")
IAP_PASSWORD = env("IAP_PASSWORD")
