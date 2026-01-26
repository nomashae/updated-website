import random
from io import BytesIO

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont

from .models import PressRelease, HomeCard, CitizenshipBadge, ORIGIN_CHOICES


def home(request):
    cards = HomeCard.objects.filter(is_active=True)
    return render(request, "core/home.html", {"home_cards": cards})


def culture(request):
    return render(request, "core/culture.html")


def executive_orders(request):
    releases = PressRelease.objects.filter(is_published=True)
    return render(request, "core/executive_orders.html", {"press_releases": releases})


# ---- Citizenship helpers ----

ORIGIN_COLOR_RANGES = {
    "Eastern Air Tample": (("#4A4A4A", "#6D6D6D"), ("#B0B0B0", "#D1D1D1")),
    "Western Air Tample": (("#3F3F3F", "#616161"), ("#A3A3A3", "#C4C4C4")),
    "Nortern Air Tample": (("#4A4A4A", "#6D6D6D"), ("#B0B0B0", "#D1D1D1")),
    "Soutern Air Tample": (("#3F3F3F", "#616161"), ("#A3A3A3", "#C4C4C4")),
    "Northern Water Tribe": (("#0B3D91", "#1A53B1"), ("#5DA0FF", "#8AC3FF")),
    "Southern Water Tribe": (("#054080", "#1B5BBF"), ("#4B9EFF", "#7EC2FF")),
    "Earth Kingdom": (("#2F4F2F", "#4B6B4B"), ("#91B491", "#BFD3BF")),
    "Fire Nation": (("#D94E1C", "#FF6A3C"), ("#FFD24B", "#FFE68A")),
}

SPECIAL_USER_RANGES = {
    "yipified": (("#054080", "#6D6D6D"), ("#5DA0FF", "#FFE68A")),
    "apparider": (("#054080", "#6D6D6D"), ("#5DA0FF", "#FFE68A")),
}


def _hex_to_rgb(hex_code: str):
    hex_code = hex_code.lstrip("#")
    return tuple(int(hex_code[i : i + 2], 16) for i in (0, 2, 4))


def _random_color_between(start_hex: str, end_hex: str) -> str:
    r1, g1, b1 = _hex_to_rgb(start_hex)
    r2, g2, b2 = _hex_to_rgb(end_hex)
    r = random.randint(min(r1, r2), max(r1, r2))
    g = random.randint(min(g1, g2), max(g1, g2))
    b = random.randint(min(b1, b2), max(b1, b2))
    return f"#{r:02X}{g:02X}{b:02X}"


def _pick_colors(username: str, origin: str) -> tuple[str, str]:
    key = username.lower()
    if key in SPECIAL_USER_RANGES:
        (c1_range, c2_range) = SPECIAL_USER_RANGES[key]
    else:
        (c1_range, c2_range) = ORIGIN_COLOR_RANGES[origin]
    color1 = _random_color_between(*c1_range)
    color2 = _random_color_between(*c2_range)
    return color1, color2


def _generate_badge_image(username: str, origin: str, color1_hex: str, color2_hex: str) -> Image.Image:
    width, height = 800, 400
    img = Image.new("RGB", (width, height), (18, 18, 18))
    draw = ImageDraw.Draw(img)

    # Gradient strip at the bottom
    bar_top = int(height * 0.6)
    c1 = _hex_to_rgb(color1_hex)
    c2 = _hex_to_rgb(color2_hex)
    for x in range(width):
        t = x / (width - 1)
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        draw.line([(x, bar_top), (x, height)], fill=(r, g, b))

    # Text (username, origin, HEX codes)
    font = ImageFont.load_default()
    username_text = username
    origin_text = origin
    color1_text = f"C1: {color1_hex}"
    color2_text = f"C2: {color2_hex}"

    u_bbox = draw.textbbox((0, 0), username_text, font=font)
    u_w, u_h = u_bbox[2] - u_bbox[0], u_bbox[3] - u_bbox[1]
    o_bbox = draw.textbbox((0, 0), origin_text, font=font)
    o_w, o_h = o_bbox[2] - o_bbox[0], o_bbox[3] - o_bbox[1]
    c1_bbox = draw.textbbox((0, 0), color1_text, font=font)
    c1_w, c1_h = c1_bbox[2] - c1_bbox[0], c1_bbox[3] - c1_bbox[1]
    c2_bbox = draw.textbbox((0, 0), color2_text, font=font)
    c2_w, c2_h = c2_bbox[2] - c2_bbox[0], c2_bbox[3] - c2_bbox[1]

    # Username and origin near top
    draw.text(((width - u_w) / 2, 70), username_text, fill=(255, 255, 255), font=font)
    draw.text(((width - o_w) / 2, 70 + u_h + 15), origin_text, fill=(200, 200, 200), font=font)

    # HEX codes just above the gradient bar
    hex_y = bar_top - c1_h - 10
    draw.text((width / 2 - c1_w - 10, hex_y), color1_text, fill=(220, 220, 220), font=font)
    draw.text((width / 2 + 10, hex_y), color2_text, fill=(220, 220, 220), font=font)

    return img


def citizenship(request):
    badge = None
    error = None
    username_value = ""
    origin_value = ""

    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        origin = request.POST.get("origin") or ""
        username_value = username
        origin_value = origin

        valid_origins = {value for value, _ in ORIGIN_CHOICES}
        if username and origin in valid_origins and origin in ORIGIN_COLOR_RANGES:
            existing = CitizenshipBadge.objects.filter(username__iexact=username).first()
            if existing:
                error = "Username taken! Please choose another username."
            else:
                color1, color2 = _pick_colors(username, origin)
                data = {
                    "username": username,
                    "origin": origin,
                    "color1": color1,
                    "color2": color2,
                    "created_at": timezone.now().isoformat(),
                }
                badge = CitizenshipBadge.objects.create(
                    username=username,
                    origin=origin,
                    color1_hex=color1,
                    color2_hex=color2,
                    data=data,
                )

    context = {
        "badge": badge,
        "origins": ORIGIN_CHOICES,
        "error": error,
        "username_value": username_value,
        "origin_value": origin_value,
    }
    return render(request, "core/citizenship.html", context)


def citizenship_badge_image(request, badge_id: int) -> HttpResponse:
    badge = get_object_or_404(CitizenshipBadge, pk=badge_id)
    img = _generate_badge_image(badge.username, badge.origin, badge.color1_hex, badge.color2_hex)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return HttpResponse(buffer.getvalue(), content_type="image/png")
