from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path(
        "mtdify/",
        TemplateView.as_view(template_name="core/mtdify.html"),
        name="mtdify",
    ),
    path(
        "djangify/",
        TemplateView.as_view(template_name="core/djangify.html"),
        name="djangify",
    ),
    path(
        "invoice-generator/",
        TemplateView.as_view(template_name="core/invoice-generator.html"),
        name="invoice_generator",
    ),
    path(
        "diane-corriette/",
        TemplateView.as_view(template_name="core/diane-corriette.html"),
        name="diane-corriette",
    ),
    path(
        "independent-software/",
        TemplateView.as_view(template_name="core/independent-software.html"),
        name="independent_software",
    ),
    path(
        "owning-your-platform/",
        TemplateView.as_view(template_name="core/owning-your-platform.html"),
        name="owning_your_platform",
    ),
    path("robots.txt", views.robots_txt, name="robots_txt"),
]
