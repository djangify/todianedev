from pathlib import Path
import os
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Environment setup
env = environ.Env()
env.read_env(os.path.join(BASE_DIR, ".env"))

SITE_URL = env("SITE_URL", default="http://localhost:8000")
SECRET_KEY = env("SECRET_KEY", default="unsafe-secret-key")


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])


CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]


# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Application definition

INSTALLED_APPS = [
    "adminita",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.redirects",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "accounts",
    "blog",
    "core",
    "infopages",
    "portfolio",
    "widget_tweaks",
    "tinymce",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.redirects.middleware.RedirectFallbackMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "todianedev.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
"core.context_processors.dashboard_announcement",
            ],
        },
    },
]

WSGI_APPLICATION = "todianedev.wsgi.application"


AUTH_USER_MODEL = "accounts.User"
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = [
    "email*",
    "first_name*",
    "password1*",
    "password2*",
]
ACCOUNT_ADAPTER = "accounts.adapters.CustomAccountAdapter"

LOGIN_REDIRECT_URL = "/admin/"
LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = "/accounts/login/"


ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_ALLOW_REGISTRATION = False


SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


ADMIN_EMAIL = "hello@todiane.com"
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Email settings for production
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="mail.privateemail.com")  # noqa: F405
EMAIL_PORT = env("EMAIL_PORT", default=587)  # noqa: F405
EMAIL_HOST_USER = env("EMAIL_HOST_USER")  # noqa: F405
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")  # noqa: F405
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="hello@todiane.com")


# ================================================================
# TINYMCE CONFIGURATION (Self-hosted, FREE plugins only)
# ==================================================================

TINYMCE_DEFAULT_CONFIG = {
    # Core
    "height": 500,
    "menubar": "file edit view insert format tools table help",
    "branding": False,
    "promotion": False,
    # FREE plugins only (image plugin removed)
    "plugins": [
        "advlist",
        "autolink",
        "lists",
        "link",
        "charmap",
        "preview",
        "anchor",
        "searchreplace",
        "visualblocks",
        "code",
        "fullscreen",
        "insertdatetime",
        "media",
        "table",
        "wordcount",
        "help",
    ],
    # Toolbar (image removed)
    "toolbar": (
        "undo redo | blocks | bold italic underline strikethrough | "
        "alignleft aligncenter alignright alignjustify | "
        "bullist numlist outdent indent | link media table | "
        "code fullscreen preview | removeformat help"
    ),
    # Block formats
    "block_formats": (
        "Paragraph=p; "
        "Heading 2=h2; "
        "Heading 3=h3; "
        "Heading 4=h4; "
        "Blockquote=blockquote; "
        "Code=pre"
    ),
    # Link behaviour
    "link_default_target": "_blank",
    "link_assume_external_targets": True,
    # Use site CSS
    "content_css": "/static/css/tinymce-content.css",
    # Paste handling
    "paste_as_text": False,
    # Allow required HTML (style added for image alignment)
    "valid_elements": (
        "p,br,b,strong,i,em,u,s,strike,sub,sup,"
        "h1,h2,h3,h4,h5,h6,"
        "ul,ol,li,"
        "a[href|target|title],"
        "img[src|alt|title|width|height|class|style],"
        "table[border|cellspacing|cellpadding],thead,tbody,tr,"
        "th[colspan|rowspan],td[colspan|rowspan],"
        "blockquote,pre,code,"
        "div[class|style],span[class|style],"
        "hr"
    ),
    # URL handling
    "relative_urls": False,
    "remove_script_host": True,
    "document_base_url": "/",
}