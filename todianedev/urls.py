from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView, TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from todianedev.sitemaps import sitemaps
from core.views import service_worker, oauth_authorization_server_metadata
from mcp_server import views as mcp_views
from mcp_server.sidebar import install_sidebar_link

urlpatterns = [
    # OAuth Authorization Server metadata (RFC 8414) for the Claude MCP connector.
    path(
        ".well-known/oauth-authorization-server",
        oauth_authorization_server_metadata,
        name="oauth_as_metadata",
    ),
    # Owner-only Connect-to-Claude pages. Mounted BEFORE the admin include so
    # these admin/-prefixed paths resolve ahead of the admin catch-all.
    path("admin/connect-claude/", mcp_views.connect_claude, name="admin_connect_claude"),
    path(
        "admin/claude-connections/",
        mcp_views.claude_connections,
        name="admin_claude_connections",
    ),
    path("admin/", admin.site.urls),

    # OAuth 2.1 Authorization Server for the MCP connector: /o/authorize,
    # /o/token, /o/introspect, /o/revoke_token.
    path("o/", include("oauth2_provider.urls", namespace="oauth2_provider")),

    # Allauth — the auth engine (login, signup, email verification, password).
    path("accounts/", include("allauth.urls")),
    # Customer account area (dashboard, wishlist) + shop-facing auth aliases.
    path("accounts/", include("accounts.urls")),

    # ----------------------------------------------------------------
    # Djangify eCommerce Site Builder: shop + hosted tools
    # ----------------------------------------------------------------
    path("shop/", include("shop.urls", namespace="shop")),
    path("tools/", include("tools.urls", namespace="tools")),
    # AI coach bots (attached to purchased products) — same /guides/ mount as IG.
    path("guides/", include("bots.urls", namespace="bots")),

    # Redirects: studio → /projects/
    path("studio/", RedirectView.as_view(url="/portfolio/", permanent=True)),
    path("studio/<path:rest>", RedirectView.as_view(url="/portfolio/", permanent=True)),

    # ----------------------------------------------------------------
    # Apps
    # ----------------------------------------------------------------
    path("blog/", include("blog.urls")),
    path("infopages/", include("infopages.urls")),
    path("portfolio/", include("portfolio.urls")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    # ----------------------------------------------------------------
    # PWA: manifest, service worker (must be at site root for full scope), offline fallback
    # ----------------------------------------------------------------
    path(
        "manifest.webmanifest",
        TemplateView.as_view(
            template_name="pwa/manifest.webmanifest",
            content_type="application/manifest+json",
        ),
        name="manifest",
    ),
    path("sw.js", service_worker, name="service_worker"),
    path(
        "offline/",
        TemplateView.as_view(template_name="pwa/offline.html"),
        name="offline",
    ),

    path("", include("core.urls")),
]

# ---- STATIC/MEDIA ----
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# ---- ADMIN BRANDING ----
admin.site.site_header = "@TODIANEDEV"
admin.site.site_title = "Portfolio Site of Diane Corriette"
admin.site.index_title = "Welcome to Your Site"

# Add the superuser-only "Claude connector" links to the admin sidebar.
install_sidebar_link()
