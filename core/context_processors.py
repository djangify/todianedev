from .models import DashboardAnnouncement


def dashboard_announcement(request):
    """
    Provides the single dashboard announcement (if it exists)
    to all templates.
    """
    announcement = DashboardAnnouncement.objects.order_by("-updated").first()

    return {"dashboard_announcement": announcement}
