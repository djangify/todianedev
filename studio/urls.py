from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = "studio"

urlpatterns = [
    # Main studio page
    path("", TemplateView.as_view(template_name="studio/index.html"), name="index"),
    # Products
    path(
        "products/",
        TemplateView.as_view(template_name="studio/products/index.html"),
        name="products_index",
    ),
    path(
        "products/bookkeeping/",
        TemplateView.as_view(template_name="studio/products/bookkeeping/index.html"),
        name="bookkeeping",
    ),
    path(
        "products/ecommerce_builder/",
        TemplateView.as_view(
            template_name="studio/products/ecommerce_builder/index.html"
        ),
        name="ecommerce_builder",
    ),
    path(
        "products/invoice_generator/",
        TemplateView.as_view(
            template_name="studio/products/invoice_generator/index.html"
        ),
        name="invoice_generator",
    ),
    path(
        "products/pdf_products/",
        TemplateView.as_view(template_name="studio/products/pdf_products/index.html"),
        name="pdf_products",
    ),
    # Tools
    path(
        "creative-coding/",
        TemplateView.as_view(template_name="studio/creative-coding/index.html"),
        name="creative_coding",
    ),
    # Sites
    path(
        "sites/",
        TemplateView.as_view(template_name="studio/sites/index.html"),
        name="sites_index",
    ),
    # gallery modal
    path(
        "modal/<int:pk>/",
        views.gallery_image_modal,
        name="gallery_image_modal",
    ),
    # ⛔ MUST BE LAST
    path("gallery/<slug:slug>/", views.gallery_view, name="gallery"),
]
