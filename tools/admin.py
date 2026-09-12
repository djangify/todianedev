# tools/admin.py
import os

from django import forms
from django.contrib import admin, messages
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.urls import path, reverse
from django.utils.html import format_html
from tinymce.widgets import TinyMCE

from .models import MAX_HOSTED_TOOLS, HostedTool, SavedToolResult


class HostedToolAdminForm(forms.ModelForm):
    class Meta:
        model = HostedTool
        fields = "__all__"
        widgets = {
            "description": TinyMCE(),
            "more_info_description": TinyMCE(),
        }


@admin.register(HostedTool)
class HostedToolAdmin(admin.ModelAdmin):
    form = HostedToolAdminForm
    list_display = ("title", "order", "slug", "access", "published", "sold_as", "saved_count", "view_link", "updated")
    list_editable = ("order", "published")
    list_filter = ("access", "published")
    ordering = ("order",)
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("download_link", "created", "updated")

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "order" and formfield is not None:
            formfield.widget.attrs.update({"style": "width: 3.5em;", "min": 0})
        return formfield

    fieldsets = (
        (
            None,
            {
                "fields": ("title", "slug", "html_file", "download_link", "image", "description", "link_text", "link_url", "link_position", "access", "published", "allow_saving", "order"),
                "description": (
                    "Upload the single .html file Claude gives you, then save — "
                    "your tool goes live at /tools/&lt;slug&gt;/. "
                    f"You can host up to {MAX_HOSTED_TOOLS} free tools; paid tools are unlimited. "
                    "To sell a paid tool, set Access to ‘Paid’ and link it from a shop "
                    "product (Shop → Products → Hosted tool) — a paid tool only "
                    "appears on the public /tools/ list once it's linked to a product. "
                    "Note: tools run in an isolated sandbox, so they cannot use "
                    "browser localStorage — keep all state in memory."
                ),
            },
        ),
        (
            "More info (optional, shown at the end of the page)",
            {
                "fields": ("more_info_title", "more_info_description"),
                "description": (
                    "An extra title and block of text shown below the tool, at the "
                    "very end of the page. Use it for background, instructions, or "
                    "anything else worth writing — real text here also improves this "
                    "page's chances of being indexed by Google."
                ),
            },
        ),
        (
            "Newsletter sign-up (this tool)",
            {
                "fields": ("marketing_list_id", "marketing_tag"),
                "description": (
                    "Reserved for a connected email marketing platform. Not wired up "
                    "yet on this site — safe to leave blank."
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

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "<int:object_id>/download-file/",
                self.admin_site.admin_view(self.download_file_view),
                name="tools_hostedtool_download",
            ),
        ]
        return custom + urls

    def download_file_view(self, request, object_id):
        """Stream the tool's HTML file to a logged-in admin.

        The file lives in SecureStorage (not directly web-served), so this
        staff-only view — wrapped in admin_view — is the one way to download
        the exact HTML that's live, straight from the change form.
        """
        tool = get_object_or_404(HostedTool, pk=object_id)
        if not tool.html_file:
            raise Http404("No file attached to this tool.")
        try:
            fh = tool.html_file.open("rb")
        except (FileNotFoundError, ValueError):
            raise Http404("Tool file missing on server.")
        return FileResponse(
            fh, as_attachment=True, filename=os.path.basename(tool.html_file.name)
        )

    def download_link(self, obj):
        if not obj or not obj.pk or not obj.html_file:
            return "—"
        url = reverse("admin:tools_hostedtool_download", args=[obj.pk])
        return format_html(
            '<a href="{}" style="font-size:11px;">⬇ Download current file</a>', url
        )

    download_link.short_description = "Download"

    def view_link(self, obj):
        if not obj.pk:
            return "—"
        url = obj.get_absolute_url()
        if not obj.published:
            url = f"{url}?preview=1"
        return format_html('<a href="{}" target="_blank">View</a>', url)

    view_link.short_description = "Live page"

    def sold_as(self, obj):
        if not obj.pk:
            return "—"
        if obj.access != HostedTool.ACCESS_PAID:
            return format_html('<span style="color:#6b7280;">Free / public</span>')

        product = obj.get_sale_product()
        if not product:
            return format_html(
                '<span style="color:#b45309;" title="A paid tool needs a linked product '
                'before it can appear on the public /tools/ list.">'
                "⚠️ No product linked</span>"
            )

        product_url = reverse("admin:shop_product_change", args=[product.pk])
        return format_html(
            '\U0001f512 <a href="{}" style="white-space:normal;">{}</a>',
            product_url,
            product.title,
        )

    sold_as.short_description = "Sold as"

    def saved_count(self, obj):
        if not obj.pk:
            return "—"
        count = obj.saved_results.count()
        if not count:
            return "—"
        url = reverse("admin:tools_savedtoolresult_changelist") + f"?tool__id__exact={obj.pk}"
        return format_html('<a href="{}">{}</a>', url, count)

    saved_count.short_description = "Saved by visitors"

    def changelist_view(self, request, extra_context=None):
        count = HostedTool.objects.filter(access=HostedTool.ACCESS_FREE).count()
        limit = MAX_HOSTED_TOOLS
        if count >= limit:
            messages.warning(
                request,
                f"You are using all {limit} of your {limit} free hosted tools. "
                f"Delete one to add another. Paid tools don't count toward this limit.",
            )
        else:
            messages.info(
                request,
                f"You are using {count} of {limit} free hosted tools "
                f"({limit - count} remaining). Paid tools are unlimited.",
            )
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(SavedToolResult)
class SavedToolResultAdmin(admin.ModelAdmin):
    """
    Read-only. This exists so an owner can look up "I saved something and
    can't find it" support requests without shell access — not as a tool for
    browsing or exporting what visitors saved.
    """

    list_display = ("user", "tool_title", "label", "created")
    list_filter = ("tool",)
    search_fields = ("user__email", "label", "tool_title", "tool_slug")
    readonly_fields = [f.name for f in SavedToolResult._meta.fields]
    ordering = ("-created",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
