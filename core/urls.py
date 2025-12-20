from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    # cluster pages
    path(
        "ai-search-readiness/",
        TemplateView.as_view(template_name="core/ai-search-readiness.html"),
        name="ai_search",
    ),
    path(
        "independent-software/",
        TemplateView.as_view(template_name="core/independent-software.html"),
        name="independent_software",
    ),
    path("robots.txt", views.robots_txt, name="robots_txt"),
]
