from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.utils import timezone




class PressRelease(models.Model):
    title = models.CharField(max_length=200)
    header = models.TextField(blank=True)
    body = models.TextField()
    footer = models.TextField(blank=True)
    image = models.ImageField(upload_to="decrees/", blank=True, null=True)
    published_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)
    is_pinned = models.BooleanField(default=False)
    highlight = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_pinned", "-published_at"]

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



class DynamicPage(models.Model):
    """Dynamically generated web pages editable from the frontend."""
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.title} (/{self.slug}/)"


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
