import random
from io import BytesIO

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from PIL import Image, ImageDraw, ImageFont

from .models import PressRelease, HomeCard, TabSettings, EditableElement, DynamicPage, EditorMedia


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


def blog_feed(request):
    posts = PressRelease.objects.filter(is_published=True)
    ctx = {"posts": posts}
    ctx.update(_tab_context("blog", "Blog | Nomashae"))
    return render(request, "core/blog.html", ctx)




def dynamic_page(request, slug):
    """Renders a dynamically created page."""
    page = get_object_or_404(DynamicPage, slug=slug)
    
    # We use a standard default context for these catch-all pages.
    ctx = {"page": page}
    ctx.update(_tab_context(f"page_{slug}", f"{page.title} | Nomashae"))
    return render(request, "core/dynamic_page.html", ctx)


@csrf_exempt
@staff_member_required
@require_POST
def create_dynamic_page(request) -> JsonResponse:
    """AJAX endpoint to create a new dynamic page."""
    import json
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    title = (payload.get("title") or "").strip()
    slug = (payload.get("slug") or "").strip().lower()

    if not title or not slug:
        return JsonResponse({"ok": False, "error": "Missing title or slug"}, status=400)

    if DynamicPage.objects.filter(slug=slug).exists():
        return JsonResponse({"ok": False, "error": "Slug already exists"}, status=400)

    try:
        DynamicPage.objects.create(title=title, slug=slug)
        return JsonResponse({"ok": True, "url": f"/{slug}/"})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)


@csrf_exempt
@staff_member_required
def get_media_library(request) -> JsonResponse:
    """Returns a JSON list of all uploaded images for the Editor Media Library."""
    media_list = EditorMedia.objects.all().order_by("-uploaded_at")
    files = [
        {
            "id": m.id,
            "url": m.file.url,
            "name": m.file.name.split("/")[-1],
            "date": m.uploaded_at.strftime("%Y-%m-%d")
        }
        for m in media_list
    ]
    return JsonResponse({"ok": True, "files": files})


@csrf_exempt
@staff_member_required
@require_POST
def editor_file_upload(request) -> JsonResponse:
    """Endpoint for TinyMCE to upload inline images."""
    if 'file' not in request.FILES:
        return JsonResponse({"error": "No file uploaded"}, status=400)
    
    upload = request.FILES['file']
    try:
        media = EditorMedia.objects.create(file=upload)
        # TinyMCE expects a JSON response with a "location" key pointing to the image URL
        return JsonResponse({"location": media.file.url})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@staff_member_required
@require_POST
def api_blog_create(request) -> JsonResponse:
    """AJAX endpoint to create a new empty blog post (PressRelease)."""
    import json
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    title = (payload.get("title") or "Untitled Post").strip()
    
    try:
        PressRelease.objects.create(title=title, is_published=True)
        return JsonResponse({"ok": True})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)


@csrf_exempt
@staff_member_required
@require_POST
def api_blog_delete(request) -> JsonResponse:
    """AJAX endpoint to delete a blog post."""
    import json
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    post_id = payload.get("id")
    if not post_id:
        return JsonResponse({"ok": False, "error": "Missing ID"}, status=400)
    
    try:
        post = PressRelease.objects.get(pk=post_id)
        post.delete()
        return JsonResponse({"ok": True})
    except PressRelease.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Post not found"}, status=404)
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)


@csrf_exempt
@staff_member_required
@require_POST
def editable_element_update(request) -> JsonResponse:
    """AJAX endpoint used by the visual editor to save changes.

    Expects JSON body with either:
      {"key": "element-id", "content": "<p>...</p>"}
    OR for direct model updates:
      {"model": "PressRelease", "model_id": 12, "field": "body", "content": "..."}
    """
    import json
    from django.apps import apps

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    content = payload.get("content") or ""

    # Direct model update path
    model_name = payload.get("model")
    model_id = payload.get("model_id")
    field_name = payload.get("field")

    if model_name and model_id and field_name:
        try:
            # We assume models are in the 'core' app for simplicity
            ModelClass = apps.get_model('core', model_name)
            obj = ModelClass.objects.get(pk=model_id)
            
            # Basic security check to ensure the field exists and is updatable
            if not hasattr(obj, field_name):
                return JsonResponse({"ok": False, "error": f"Field '{field_name}' not found on {model_name}"}, status=400)
            
            setattr(obj, field_name, content)
            obj.save()
            return JsonResponse({"ok": True, "type": "model_update"})
        
        except LookupError:
            return JsonResponse({"ok": False, "error": f"Model '{model_name}' not found"}, status=400)
        except Exception as e:
            return JsonResponse({"ok": False, "error": str(e)}, status=500)

    # Standard EditableElement path
    key = (payload.get("key") or "").strip()
    if not key:
        return JsonResponse({"ok": False, "error": "Missing key or model details"}, status=400)

    obj, _created = EditableElement.objects.update_or_create(
        key=key,
        defaults={"content": content},
    )
    return JsonResponse({"ok": True, "key": obj.key})
