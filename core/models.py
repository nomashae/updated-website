from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower


ORIGIN_CHOICES = [
    ("Eastern Air Tample", "Eastern Air Tample"),
    ("Western Air Tample", "Western Air Tample"),
    ("Nortern Air Tample", "Nortern Air Tample"),
    ("Soutern Air Tample", "Soutern Air Tample"),
    ("Northern Water Tribe", "Northern Water Tribe"),
    ("Southern Water Tribe", "Southern Water Tribe"),
    ("Earth Kingdom", "Earth Kingdom"),
    ("Fire Nation", "Fire Nation"),
]


class PressRelease(models.Model):
    title = models.CharField(max_length=200)
    intro = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    signed_by = models.CharField(max_length=200, blank=True)
    published_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)
    highlight = models.BooleanField(default=False)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return self.title


class HomeCard(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    button_text = models.CharField(max_length=50, blank=True)
    button_url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:  # pragma: no cover
        return self.title


class TabSettings(models.Model):
    """Per-page tab metadata (title and icon text/colors) editable via admin."""

    slug = models.SlugField(unique=True)
    tab_title = models.CharField(max_length=100)
    icon_text = models.CharField(max_length=2, default="N")
    icon_bg_color = models.CharField(max_length=7, default="#2F2F2F")
    icon_text_color = models.CharField(max_length=7, default="#FFFFFF")

    class Meta:
        ordering = ["slug"]

    def __str__(self) -> str:  # pragma: no cover
        return f"Tab settings for {self.slug}"


class CitizenshipBadge(models.Model):
    username = models.CharField(max_length=50)
    origin = models.CharField(max_length=50, choices=ORIGIN_CHOICES)
    color1_hex = models.CharField(max_length=7)
    color2_hex = models.CharField(max_length=7)
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            UniqueConstraint(Lower("username"), name="unique_citizenship_username_ci"),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.username} ({self.origin})"


class EditableElement(models.Model):
    """Stores editable HTML snippets keyed by an element ID.

    This backs the lightweight visual editor: staff users can toggle edit mode
    and change any element that has a matching data-edit-id in the templates.
    """

    key = models.CharField(max_length=100, unique=True)
    content = models.TextField(blank=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["key"]

    def __str__(self) -> str:  # pragma: no cover
        return self.key
