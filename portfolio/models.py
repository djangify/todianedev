from django.db import models
from django.urls import reverse
from django.core.validators import FileExtensionValidator
from tinymce.models import HTMLField


class Technology(models.Model):
    """Technologies used in each project (e.g., Django, React, PostgreSQL)."""

    CATEGORY_CHOICES = [
        ("frontend", "Frontend"),
        ("backend", "Backend"),
        ("database", "Database"),
        ("devops", "DevOps"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default="other"
    )

    class Meta:
        verbose_name_plural = "Technologies"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Portfolio(models.Model):
    """Main project model."""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    short_description = models.CharField(max_length=200, blank=True)

    overview = HTMLField(blank=True, null=True)
    technical_details = HTMLField(blank=True, null=True)
    results = HTMLField(blank=True, null=True)

    featured_image = models.ImageField(
        upload_to="portfolio/featured/",
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])],
        blank=True,
        null=True,
    )
    featured_image_url = models.URLField(blank=True, null=True)

    # External links
    live_site_url = models.URLField(
        blank=True, null=True, help_text="Link to live deployed site"
    )
    github_url = models.URLField(
        blank=True, null=True, help_text="Link to GitHub repository"
    )
    for_sale_url = models.URLField(
        blank=True,
        null=True,
        help_text="Link to purchase or contact page if this project is for sale",
    )

    technologies = models.ManyToManyField(
        "Technology", related_name="projects", blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # SEO fields
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name_plural = "Portfolio Projects"

    def __str__(self):
        return self.title

    @property
    def display_image(self):
        """Return either the uploaded image or the external URL safely."""
        if self.featured_image_url:
            return self.featured_image_url
        if self.featured_image and hasattr(self.featured_image, "url"):
            try:
                return self.featured_image.url
            except ValueError:
                return None
        return None

    def get_absolute_url(self):
        return reverse("portfolio:detail", kwargs={"slug": self.slug})


class PortfolioImage(models.Model):
    """Additional images for each project."""

    portfolio = models.ForeignKey(
        Portfolio, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(
        upload_to="portfolio/gallery/",
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])],
        blank=True,
        null=True,
    )
    image_url = models.URLField(blank=True, null=True)
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.portfolio.title} – Image {self.order}"

    @property
    def display_image(self):
        if self.image_url:
            return self.image_url
        if self.image and hasattr(self.image, "url"):
            try:
                return self.image.url
            except ValueError:
                return None
        return None
