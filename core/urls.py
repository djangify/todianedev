from django.urls import path, reverse_lazy
from . import views
from django.views.generic import TemplateView, RedirectView

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path(
        "deskledger/",
        TemplateView.as_view(template_name="core/deskledger.html"),
        name="deskledger",
    ),
    path(
        "mtdify/",
        RedirectView.as_view(url=reverse_lazy("core:deskledger"), permanent=True),
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
