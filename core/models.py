from django.db import models


class DashboardAnnouncement(models.Model):
    announcement_bar_text = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Optional announcement message shown at the top of the dashboard.",
    )
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.announcement_bar_text or "Dashboard Announcement"
