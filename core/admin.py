from django.contrib import admin

from .models import PressRelease, HomeCard, CitizenshipBadge, TabSettings, EditableElement


@admin.register(PressRelease)
class PressReleaseAdmin(admin.ModelAdmin):
    list_display = ("title", "published_at", "is_published", "highlight")
    list_filter = ("is_published", "highlight", "published_at")
    search_fields = ("title", "body")
    ordering = ("-published_at",)


@admin.register(HomeCard)
class HomeCardAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("title", "subtitle", "body")
    ordering = ("order",)


@admin.register(TabSettings)
class TabSettingsAdmin(admin.ModelAdmin):
    list_display = ("slug", "tab_title", "icon_text")
    search_fields = ("slug", "tab_title")
    ordering = ("slug",)


@admin.register(EditableElement)
class EditableElementAdmin(admin.ModelAdmin):
    list_display = ("key", "description")
    search_fields = ("key", "description")
    ordering = ("key",)


@admin.register(CitizenshipBadge)
class CitizenshipBadgeAdmin(admin.ModelAdmin):
    list_display = ("username", "origin", "created_at")
    list_filter = ("origin",)
    search_fields = ("username",)
    ordering = ("-created_at",)
