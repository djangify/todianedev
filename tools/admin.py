from django.contrib import admin
from django.utils.html import format_html

# Only Hosted Tools are surfaced in the admin. The ExperimentWeek /
# ExperimentGoal / MilestoneReflection / AliveListItem models came across with
# the Djangify port but are Inspirational-Guidance-specific, so they are not
# registered here.
from .models import HostedTool


@admin.register(HostedTool)
class HostedToolAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "access", "published", "for_sale", "view_link", "updated")
    list_filter = ("access", "published",)
    list_editable = ("access", "published",)
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created", "updated")

    fieldsets = (
        (
            None,
            {
                "fields": ("title", "slug", "html_file", "description", "link_text", "link_url", "access", "published"),
                "description": (
                    "Upload the single .html file Claude gives you, then save — "
                    "your tool goes live at /tools/&lt;slug&gt;/. "
                    "There is no limit on how many tools you can host. "
                    "Set Access to <b>Paid</b> to gate the tool: it is then only "
                    "reachable by buyers of the shop product you attach it to "
                    "(Shop → Product → Hosted Tool). "
                    "Note: tools run in an isolated sandbox, so they cannot use "
                    "browser localStorage or call your logged-in pages — keep all "
                    "state in memory inside the artifact."
                ),
            },
        ),
        (
            "Info",
            {
                "fields": ("created", "updated"),
                "classes": ("collapse",),
            },
        ),
    )

    def view_link(self, obj):
        if not obj.pk:
            return "—"
        url = obj.get_absolute_url()
        if not obj.published:
            url = f"{url}?preview=1"
        return format_html('<a href="{}" target="_blank">View</a>', url)

    view_link.short_description = "Live page"

    def for_sale(self, obj):
        """Show whether this tool is attached to a shop product (purchase-gated)."""
        product = obj.linked_product
        if product is None:
            return format_html('<span style="color:#999;">Free / public</span>')
        return format_html(
            '🔒 <a href="/admin/shop/product/{}/change/">{}</a>',
            product.pk, product.title,
        )

    for_sale.short_description = "Sold as"
