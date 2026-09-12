# tools/models.py
#
# Ported from the Djangify self-hosted eCommerce Site Builder so this project
# demonstrates the same generic "hosted tools" feature the self-hosted product
# ships with: an owner uploads a self-contained HTML artifact (e.g. a
# Claude-generated interactive tool), and it goes live at /tools/<slug>/,
# sandboxed in an iframe, with an optional "save your results to your
# dashboard" flow for logged-in visitors.
import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from tinymce.models import HTMLField

from todianedev.storage import PublicStorage, SecureStorage
from todianedev.utils import custom_slugify

# Card image limits (kept small since it's only ever shown as a thumbnail
# on the /tools/ index).
MAX_TOOL_IMAGE_BYTES = 1 * 1024 * 1024  # 1 MB
MAX_TOOL_IMAGE_DIMENSION = 1200  # px, longest side

# Maximum number of FREE hosted tools allowed on this site. Paid tools are
# unlimited, since each is gated behind its own linked product purchase.
MAX_HOSTED_TOOLS = 7

# Saved tool results: caps mirror the results-snapshot caps enforced below for
# the "email me my results" flow (same untrusted browser-supplied payload,
# same reason to cap it before it reaches the DB).
MAX_SAVED_RESULT_HTML_BYTES = 200_000
MAX_SAVED_RESULT_TEXT_BYTES = 100_000
MAX_SAVED_RESULT_DATA_BYTES = 20_000
# Per user, per tool. Prevents a runaway/buggy tool (or abuse) from filling
# the database with saves nobody will ever look at again.
MAX_SAVED_RESULTS_PER_TOOL = 50


def validate_html(value):
    """Only allow .html / .htm uploads (a Claude artifact is a single HTML file)."""
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in [".html", ".htm"]:
        raise ValidationError(
            "Only .html files are allowed. Upload the single HTML file Claude gives you."
        )


def validate_tool_image(value):
    """Keep card thumbnails small: cap file size and pixel dimensions.

    Only *newly uploaded* files are checked. This validator is attached to the
    model field, so Django runs it during full_clean() on every save — including
    re-saves where the image is unchanged. For an already-stored file we skip:
    it was validated when first uploaded, and if the underlying file has gone
    missing from storage, reading `value.size` would raise FileNotFoundError and
    500 the admin instead of validating.
    """
    if not value or getattr(value, "_committed", False):
        return
    if value.size > MAX_TOOL_IMAGE_BYTES:
        raise ValidationError(
            f"Image is too large ({value.size / 1024 / 1024:.1f}MB). "
            f"Please upload an image under {MAX_TOOL_IMAGE_BYTES // 1024 // 1024}MB."
        )
    try:
        width, height = value.image.size
    except Exception:
        return
    if width > MAX_TOOL_IMAGE_DIMENSION or height > MAX_TOOL_IMAGE_DIMENSION:
        raise ValidationError(
            f"Image is {width}x{height}px. Please upload an image no larger than "
            f"{MAX_TOOL_IMAGE_DIMENSION}x{MAX_TOOL_IMAGE_DIMENSION}px — it's only shown as a small thumbnail."
        )


class HostedTool(models.Model):
    """
    A self-contained HTML 'artifact' (e.g. a Claude-generated interactive tool)
    uploaded by the site owner and served live at /tools/<slug>/.

    The file is stored with SecureStorage so it is NOT reachable directly on
    the web. It is only ever served through the sandboxed iframe view
    (see tools/views.py tool_raw), which keeps the artifact's JavaScript
    isolated from the site's own origin (cookies, session, DOM).

    Note: the sandbox uses an opaque origin (no allow-same-origin), so an
    uploaded tool CANNOT call back to this site's logged-in endpoints. Keep
    all state in memory inside the artifact.
    """

    title = models.CharField(max_length=200)
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        help_text="Used in the public URL: /tools/<slug>/ . Leave blank to auto-fill from the title.",
    )
    description = HTMLField(
        blank=True,
        help_text="Optional short caption shown above the tool on its public page.",
    )
    link_text = models.CharField(
        "URL name",
        max_length=120,
        blank=True,
        help_text=(
            "Optional. The clickable label for a link button shown at the top "
            "AND bottom of the tool's page (e.g. 'Back to the shop', "
            "'Get the full guide'). Leave blank to hide the link."
        ),
    )
    link_url = models.URLField(
        "URL link",
        max_length=500,
        blank=True,
        help_text="Where the link button points. Only shown if both fields are filled.",
    )
    LINK_POSITION_CHOICES = [
        ("both", "Top and bottom (default)"),
        ("top", "Top only"),
        ("bottom", "Bottom only"),
    ]
    link_position = models.CharField(
        "URL link position",
        max_length=10,
        choices=LINK_POSITION_CHOICES,
        default="both",
        help_text="Where the link button appears on the page, if it's set.",
    )
    more_info_title = models.CharField(
        "Extra title",
        max_length=200,
        blank=True,
        help_text=(
            "Optional heading for an extra block of text shown at the end of "
            "the page, below the tool. Handy for background, instructions, or "
            "context you don't want cluttering the top of the page — and the "
            "extra real text also helps this page get found in search."
        ),
    )
    more_info_description = HTMLField(
        "Extra description",
        blank=True,
        help_text="Optional. Shown under the extra title, at the end of the page.",
    )
    html_file = models.FileField(
        upload_to="tools/",
        storage=SecureStorage(),
        validators=[validate_html],
        help_text="Upload the single .html file. Hit save and it goes live at the URL above.",
    )
    image = models.ImageField(
        upload_to="tools/cards/",
        storage=PublicStorage(),
        blank=True,
        null=True,
        validators=[validate_tool_image],
        help_text=(
            "Optional small thumbnail shown on the /tools/ list page. "
            f"Max {MAX_TOOL_IMAGE_BYTES // 1024 // 1024}MB, "
            f"{MAX_TOOL_IMAGE_DIMENSION}x{MAX_TOOL_IMAGE_DIMENSION}px or smaller. "
            "Leave blank to show a plain card with no image."
        ),
    )
    published = models.BooleanField(
        default=True,
        help_text="Untick to take the tool offline without deleting it.",
    )
    allow_saving = models.BooleanField(
        "Let visitors save their results",
        default=True,
        help_text=(
            "When ticked, a logged-in visitor can save what they typed in this "
            "tool to their own dashboard, and come back to it later. Turning "
            "this off is not recommended for a tool that produces something "
            "worth keeping (a list, a plan, a compass statement) — most "
            "visitors expect to be able to find it again."
        ),
    )

    ACCESS_FREE = "free"
    ACCESS_PAID = "paid"
    ACCESS_CHOICES = [
        (ACCESS_FREE, "Free — anyone can use it"),
        (ACCESS_PAID, "Paid — only buyers can use it"),
    ]
    access = models.CharField(
        max_length=10,
        choices=ACCESS_CHOICES,
        default=ACCESS_FREE,
        help_text=(
            "Free tools count toward your hosted-tool limit. Paid tools do not "
            "count, and are unlocked only by buying a linked shop product."
        ),
    )

    order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        help_text="Lower numbers appear first on the /tools/ list. Tools with the same number fall back to alphabetical order.",
    )

    marketing_list_id = models.CharField(
        "Marketing list ID",
        max_length=100,
        blank=True,
        help_text=(
            "Optional. Reserved for a connected email marketing platform: when "
            "someone signs up from THIS tool's newsletter box, they would be "
            "added to this list/group ID instead of the store's default list. "
            "Leave blank to use the default."
        ),
    )
    marketing_tag = models.CharField(
        "Marketing tag",
        max_length=100,
        blank=True,
        help_text=(
            "Optional. Reserved for a connected email marketing platform: a tag "
            "applied to people who sign up from THIS tool, so you can segment "
            "them later. Leave blank for no extra tag."
        ),
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "title"]
        verbose_name = "Hosted Tool"
        verbose_name_plural = "Hosted Tools"

    def __str__(self):
        return self.title

    def clean(self):
        # The per-site limit applies to FREE tools only. Paid tools are
        # unlimited — each is gated behind its own linked product purchase.
        if self._state.adding and self.access == self.ACCESS_FREE:
            if HostedTool.objects.filter(access=self.ACCESS_FREE).count() >= MAX_HOSTED_TOOLS:
                raise ValidationError(
                    f"You have reached the limit of {MAX_HOSTED_TOOLS} free hosted tools. "
                    f"Delete one to add another, or mark this tool as paid."
                )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = custom_slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("tools:detail", kwargs={"slug": self.slug})

    def get_raw_url(self):
        return reverse("tools:raw", kwargs={"slug": self.slug})

    @property
    def has_link(self):
        """True when both the link name and link URL are set (show the button)."""
        return bool(self.link_text and self.link_url)

    @property
    def show_link_top(self):
        return self.has_link and self.link_position in ("both", "top")

    @property
    def show_link_bottom(self):
        return self.has_link and self.link_position in ("both", "bottom")

    @property
    def has_more_info(self):
        """True when there's extra title/description text to show at the end of the page."""
        return bool(self.more_info_title or self.more_info_description)

    # -- Selling a tool ------------------------------------------------------
    # access == "paid" gates the tool: its public page is only reachable by
    # someone who has purchased a linked shop product (or by staff). The link
    # itself is made on the shop side (Product.hosted_tool). Free tools stay
    # public for everyone.

    @property
    def linked_product(self):
        """The first shop Product selling this tool, or None if none is linked."""
        return self.get_sale_product()

    @property
    def requires_purchase(self):
        """True if this tool is marked Paid and must be unlocked by a purchase."""
        return self.access == self.ACCESS_PAID

    def is_unlocked_for(self, user):
        """
        Can `user` view this tool? Free tools: always. Sold tools: only the
        buyer (a completed order for a linked product) or staff.
        """
        if self.access == self.ACCESS_FREE:
            return True
        if not user or not getattr(user, "is_authenticated", False):
            return False
        if user.is_staff or user.is_superuser:
            return True
        # Local import avoids a circular import at module load time.
        from shop.models import OrderItem

        return OrderItem.objects.filter(
            order__user=user,
            order__status="completed",
            product__hosted_tool=self,
        ).exists()

    # Kept as an alias: some call sites (admin, older code) read this name.
    user_has_access = is_unlocked_for

    def get_sale_product(self):
        """The product a visitor should buy to unlock this tool (if any)."""
        return (
            self.products.filter(is_active=True, status="publish")
            .order_by("id")
            .first()
            or self.products.order_by("id").first()
        )

    @property
    def is_visible_on_list(self):
        """
        Whether this tool should appear on the public /tools/ index.
        Free tools always qualify. Paid tools only qualify once they're
        linked to a sellable product — otherwise there'd be no way for a
        visitor to buy access, so we keep it off the list until it's linked.
        """
        if self.access == self.ACCESS_FREE:
            return True
        return self.get_sale_product() is not None


# ── Saved tool results ───────────────────────────────────────────────────

class SavedToolResult(models.Model):
    """
    A snapshot of what a logged-in visitor produced inside a hosted tool,
    saved to their own dashboard so they can find it again later.

    This is served entirely through postMessage from the sandboxed iframe —
    see tools/views.py save_result() and the tool_detail.html "Save to my
    dashboard" button. The iframe itself never talks to this model directly
    (it has no allow-same-origin, so it couldn't call our API even if it
    tried); the parent page is what captures a snapshot and posts it here.

    Two payload shapes are kept side by side:
      - `data`: structured JSON, only present when the uploaded tool
        cooperates (posts a __toolSave message with a data payload).
      - `results_html` / `results_text`: an HTML/plain-text snapshot of the
        tool's output area, always available because it's captured the same
        way the "download PDF" / results-capture script already captures it.
    Keeping both means saving works for every tool already uploaded, with no
    changes required on the tool author's side, while still giving
    cooperating tools a cleaner, structured option.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_tool_results",
    )
    # SET_NULL (not CASCADE): deleting a tool from the admin should not wipe
    # out a visitor's own saved data. tool_title/tool_slug are copied below
    # at save time so the dashboard still has something legible to show even
    # after the tool itself is gone.
    tool = models.ForeignKey(
        "tools.HostedTool",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="saved_results",
    )
    tool_title = models.CharField(max_length=200, blank=True)
    tool_slug = models.SlugField(max_length=200, blank=True)

    label = models.CharField(
        max_length=300,
        help_text="Short name the visitor sees on their dashboard, e.g. 'My top 3 values'.",
    )
    data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured payload from a cooperating tool, if any.",
    )
    results_html = models.TextField(
        blank=True,
        help_text="Sanitised HTML snapshot of the tool's output at save time.",
    )
    results_text = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "Saved tool result"
        indexes = [
            models.Index(fields=["user", "tool", "-created"]),
        ]

    def __str__(self):
        return f"{self.user} — {self.tool_title or self.tool_slug} — {self.label[:60]}"
