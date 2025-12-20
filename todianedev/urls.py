from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from todianedev.sitemaps import sitemaps

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("accounts/", include("accounts.urls")),
    path("blog/", include("blog.urls")),
    path("infopages/", include("infopages.urls")),
    path("portfolio/", include("portfolio.urls")),
    path("shop/", include("shop.urls")),
    path("studio/", include("studio.urls")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("", include("core.urls")),
]

# ---- STATIC/MEDIA ----
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# ---- ADMINITA DJANGO DASHBOARD ----
admin.site.site_header = "@TODIANEDEV"
admin.site.site_title = "Portfolio Site of Diane Corriette"
admin.site.index_title = "Welcome to Your Site"
