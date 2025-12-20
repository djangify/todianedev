from django.db import models
from django.utils.html import format_html


# Create your models here.
class Gallery(models.Model):
    title = models.CharField(max_length=200, blank=True)
    subtitle = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional short description shown under the gallery title.",
    )
    slug = models.SlugField(unique=True)
    published = models.BooleanField(default=True)


class GalleryImage(models.Model):
    gallery = models.ForeignKey(
        Gallery,
        related_name="images",
        on_delete=models.CASCADE,
    )
    image = models.ImageField(upload_to="gallery/")
    title = models.CharField(max_length=200, blank=True)
    caption = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title or f"Image {self.pk}"

    def admin_thumbnail(self):
        if self.image:
            return format_html(
                '<img src="{}" style="height: 80px; width: auto; border-radius: 4px;" />',
                self.image.url,
            )
        return "—"

    admin_thumbnail.short_description = "Preview"
