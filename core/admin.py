# core/admin.py
from django.contrib import admin
from .models import DashboardAnnouncement


@admin.register(DashboardAnnouncement)
class DashboardAnnouncementAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Dashboard Announcement Bar",
            {
                "fields": ("announcement_bar_text",),
                "description": "Optional message shown at the top of the dashboard for logged-in users.",
            },
        ),
    )

    list_display = ("__str__", "announcement_bar_text", "updated")
