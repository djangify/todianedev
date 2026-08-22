# todiane/storage.py

from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os


class SecureStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(
            location=os.path.join(settings.MEDIA_ROOT, "secure"),
            base_url=settings.MEDIA_URL + "secure/",
        )


class PublicStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(
            location=os.path.join(settings.MEDIA_ROOT, "public"),
            base_url=settings.MEDIA_URL + "public/",
        )


# ---------------------------------------------------------------------------
# Djangify shop/tools storage backends (ported from the Djangify eCommerce
# Site Builder). The shop and tools apps import ``secure_storage`` /
# ``public_storage`` and reference the ``SecureFileStorage`` /
# ``PublicMediaStorage`` classes from their migrations, so both the classes and
# the singleton instances must live here.
# ---------------------------------------------------------------------------
class SecureFileStorage(FileSystemStorage):
    """Private files (digital products, hosted tool HTML) served only via
    access-checked views. Never exposed under a public MEDIA URL."""

    def __init__(self):
        secure_root = os.path.join(settings.MEDIA_ROOT, "secure_downloads")
        super().__init__(location=secure_root)

    def get_valid_name(self, name):
        name = super().get_valid_name(name)
        return name.replace("public/", "")


class PublicMediaStorage(FileSystemStorage):
    """Public shop media (product images, previews, videos)."""

    def __init__(self):
        public_root = os.path.join(settings.MEDIA_ROOT, "public")
        super().__init__(location=public_root, base_url=settings.MEDIA_URL + "public/")

    def get_valid_name(self, name):
        name = super().get_valid_name(name)
        return name.replace("public/", "")

    def url(self, name):
        url = super().url(name)
        if not url.startswith(settings.MEDIA_URL):
            url = settings.MEDIA_URL.rstrip("/") + "/public/" + name.lstrip("/")
        return url


# Singleton instances imported by shop/tools models.
secure_storage = SecureFileStorage()
public_storage = PublicMediaStorage()
