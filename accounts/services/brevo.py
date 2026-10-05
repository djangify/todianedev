import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

BREVO_CONTACTS_URL = "https://api.brevo.com/v3/contacts"
_TIMEOUT = 10


def add_subscriber(user):
    """
    Add a user to the Djangify list in Brevo. Called once their email address is
    confirmed and they ticked "keep me updated", so the signup email plus the
    verification click is the double opt-in. Never raises: a Brevo problem must
    not break signing in or email verification.
    """
    api_key = (getattr(settings, "BREVO_API_KEY", "") or "").strip()
    list_id = getattr(settings, "BREVO_LIST_ID", None)
    if not api_key or not list_id:
        logger.warning("Brevo is not configured; skipped %s", user.email)
        return False

    payload = {
        "email": user.email,
        "attributes": {"FIRSTNAME": user.first_name or ""},
        "listIds": [int(list_id)],
        "updateEnabled": True,
    }
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    try:
        response = requests.post(
            BREVO_CONTACTS_URL, json=payload, headers=headers, timeout=_TIMEOUT
        )
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        logger.error("Brevo sync failed for %s: %s", user.email, e)
        return False
