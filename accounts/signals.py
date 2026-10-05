# accounts/signals.py
import logging

from allauth.account.signals import email_confirmed
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(email_confirmed)
def add_confirmed_user_to_list(sender, request, email_address, **kwargs):
    """When someone confirms their email, add them to the Djangify list in Brevo,
    but only if they ticked "keep me updated" when they signed up."""
    user = email_address.user
    profile = getattr(user, "profile", None)
    if not profile or not profile.is_subscribed:
        return
    try:
        from accounts.services.brevo import add_subscriber

        add_subscriber(user)
    except Exception as e:  # noqa: BLE001 - never break email confirmation
        logger.error("Could not add %s to the list: %s", user.email, e)
