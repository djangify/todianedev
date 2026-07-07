from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView, TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from todianedev.sitemaps import sitemaps
from core.views import service_worker

urlpatterns = [
    path("admin/", admin.site.urls),

    # Allauth — kept for admin login only (registration disabled via settings)
    path("accounts/", include("allauth.urls")),

    # ----------------------------------------------------------------
    # Redirects: shop → /projects/
    # ----------------------------------------------------------------
    path("shop/", RedirectView.as_view(url="/portfolio/", permanent=True)),
    path("shop/<path:rest>", RedirectView.as_view(url="/portfolio/", permanent=True)),

    # Redirects: studio → /projects/
    path("studio/", RedirectView.as_view(url="/portfolio/", permanent=True)),
    path("studio/<path:rest>", RedirectView.as_view(url="/portfolio/", permanent=True)),

    # Redirects: old accounts public pages → home
    path("accounts/dashboard/", RedirectView.as_view(url="/", permanent=True)),
    path("accounts/profile/", RedirectView.as_view(url="/", permanent=True)),
    path("accounts/support/", RedirectView.as_view(url="/", permanent=True)),
    path("accounts/delete-account/", RedirectView.as_view(url="/", permanent=True)),

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
