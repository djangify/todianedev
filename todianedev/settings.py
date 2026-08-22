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
    "rest_framework",
    # OAuth 2.1 Authorization Server for the Claude MCP connector. Listed before
    # mcp_server so its admin is registered by the time mcp_server hides it.
    "oauth2_provider",
    "accounts",
    "blog",
    "core",
    "infopages",
    "portfolio",
    # Djangify eCommerce Site Builder apps
    "shop",
    "tools",
    # AI mentor / coach bots (sold as products)
    "bots",
    # MCP connector app — call-log model + owner "Connect to Claude" admin pages.
    # The MCP endpoint itself is served by a separate sidecar (mcp_server.app).
    "mcp_server",
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
                # Djangify shop context processors (cart, site settings, sidebar)
                "shop.context_processors.cart",
                "shop.context_processors.site_settings",
                "shop.context_processors.sidebar_products",
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
ACCOUNT_ALLOW_REGISTRATION = True

# Honeypot spam trap on the signup form. allauth adds a hidden "website" field;
# real users never see it, but bots fill every field they find. When it's filled
# allauth silently returns a fake "verification sent" response and creates NO
# user — the bot is told nothing went wrong. The field is rendered (off-screen)
# in templates/account/signup.html so bots actually see it.
ACCOUNT_SIGNUP_FORM_HONEYPOT_FIELD = "website"


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

# ================================================================
# DJANGIFY eCOMMERCE SITE BUILDER — shop / tools / MCP
# ================================================================

SITE_NAME = env("SITE_NAME", default="todiane.com")

# --- Shop / cart ---
CART_SESSION_ID = "cart"

# --- Author / EEAT (used by shop templates via getattr fallbacks) ---
AUTHOR_NAME = "Diane Corriette"
AUTHOR_SHORT_BIO = (
    "Diane Corriette is a Django indie developer and personal growth coach — "
    "The Coach Who Codes — and the creator of the Djangify eCommerce Site Builder."
)
AUTHOR_URL = "/about"

# --- Stripe ---
# The shop code reads STRIPE_PUBLISHABLE_KEY; this project's .env historically
# names it STRIPE_PUBLIC_KEY, so accept either (PUBLISHABLE wins if both set).
STRIPE_PUBLISHABLE_KEY = env(
    "STRIPE_PUBLISHABLE_KEY",
    default=env("STRIPE_PUBLIC_KEY", default="pk_test_placeholder"),
)
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", default="sk_test_placeholder")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET", default="whsec_placeholder")

# --- Claude (optional; used by AI features / MCP tooling) ---
ANTHROPIC_API_KEY = env("ANTHROPIC_API_KEY", default="")

# --- Protected media root (secure digital downloads) ---
PROTECTED_MEDIA_ROOT = env(
    "PROTECTED_MEDIA_ROOT",
    default=os.path.join(MEDIA_ROOT, "secure_downloads"),
)

# -----------------------------------------------------------------------------
# REST framework (browsable API for shop/tools endpoints + MCP)
# -----------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly"
    ],
}

# ================================================================
# OAUTH 2.1 — Authorization Server for the Claude MCP connector
# Django (this app) issues tokens; the MCP sidecar (mcp_server.app) is a
# separate Resource Server that only verifies them. PKCE (S256) required.
# Only the single "mcp" scope exists.
# ================================================================
OAUTH2_PROVIDER = {
    "PKCE_REQUIRED": True,
    "SCOPES": {"mcp": "Read and manage this site's content via MCP"},
    "DEFAULT_SCOPES": ["mcp"],
    "ACCESS_TOKEN_EXPIRE_SECONDS": env.int(
        "MCP_ACCESS_TOKEN_EXPIRE_SECONDS", default=36000
    ),
    "REFRESH_TOKEN_EXPIRE_SECONDS": env.int(
        "MCP_REFRESH_TOKEN_EXPIRE_SECONDS", default=5184000  # 60 days
    ),
    "ALLOWED_REDIRECT_URI_SCHEMES": env.list(
        "MCP_ALLOWED_REDIRECT_URI_SCHEMES",
        default=(["http", "https"] if DEBUG else ["https"]),
    ),
}