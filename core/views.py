import random
from io import BytesIO

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from PIL import Image, ImageDraw, ImageFont

from .models import PressRelease, HomeCard, TabSettings, EditableElement


def _tab_context(slug: str, default_title: str) -> dict:
    """Return per-page tab metadata (title + computed favicon data URL)."""

    try:
        settings_obj = TabSettings.objects.get(slug=slug)
        title = settings_obj.tab_title or default_title
        icon_text = settings_obj.icon_text or "N"
        bg = settings_obj.icon_bg_color or "#2F2F2F"
        fg = settings_obj.icon_text_color or "#FFFFFF"
    except TabSettings.DoesNotExist:
        title = default_title
        icon_text = "N"
        bg = "#2F2F2F"
        fg = "#FFFFFF"

    # Build a tiny SVG favicon as a data URL. We keep it simple so it stays editable.
    from urllib.parse import quote

    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" rx="20" fill="{bg}"/><text x="50" y="50" dy=".35em" text-anchor="middle" font-family="sans-serif" font-weight="bold" font-size="70" fill="{fg}">{icon_text}</text></svg>'
    href = "data:image/svg+xml," + quote(svg)
    return {"tab_title": title, "tab_icon_href": href}


def home(request):
    cards = HomeCard.objects.filter(is_active=True)
    ctx = {"home_cards": cards}
    ctx.update(_tab_context("home", "Nomashae | Democratic Micronation"))
    return render(request, "core/home.html", ctx)


def culture(request):
    ctx = _tab_context("culture", "Culture | Nomashae")
    return render(request, "core/culture.html", ctx)


def executive_orders(request):
    releases = PressRelease.objects.filter(is_published=True)
    ctx = {"press_releases": releases}
    ctx.update(_tab_context("news", "Executive Orders | Nomashae"))
    return render(request, "core/executive_orders.html", ctx)




@csrf_exempt
@staff_member_required
@require_POST
def editable_element_update(request) -> JsonResponse:
    """AJAX endpoint used by the visual editor to save changes.

    Expects JSON body with {"key": "element-id", "content": "<p>...</p>"}.
    """

    import json

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    key = (payload.get("key") or "").strip()
    content = payload.get("content") or ""
    if not key:
        return JsonResponse({"ok": False, "error": "Missing key"}, status=400)

    obj, _created = EditableElement.objects.update_or_create(
        key=key,
        defaults={"content": content},
    )
    return JsonResponse({"ok": True, "key": obj.key})
