from django.contrib import admin
from django.utils.html import format_html
from .models import Technology, Portfolio, PortfolioImage


class PortfolioImageInline(admin.TabularInline):
    model = PortfolioImage
    extra = 1
    fields = ("image", "image_url", "caption", "order", "preview")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.display_image:
            return format_html(
                '<img src="{}" style="max-height:50px;">', obj.display_image
            )
        return "No image"


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "category")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "is_featured", "order", "created_at")
    list_filter = ("status", "is_featured", "technologies")
    search_fields = ("title", "short_description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [PortfolioImageInline]
    list_editable = ("order", "is_featured", "status")

    fieldsets = (
        ("Basic Info", {"fields": ("title", "slug", "short_description", "status")}),
        ("Content", {"fields": ("overview", "technical_details", "results")}),
        (
            "Media & Links",
            {
                "fields": (
                    "featured_image",
                    "featured_image_url",
                    "live_site_url",
                    "github_url",
                    "for_sale_url",
                    "technologies",
                )
            },
        ),
        ("SEO", {"fields": ("meta_title", "meta_description", "meta_keywords")}),
    )
