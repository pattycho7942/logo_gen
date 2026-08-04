import base64
import io
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

_FONT_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"
_REGULAR_FONT_PATH = _FONT_DIR / "NanumGothic.ttf"
_BOLD_FONT_PATH = _FONT_DIR / "NanumGothicBold.ttf"

CARD_WIDTH = 1050
CARD_HEIGHT = 600
_PADDING = 64
_LOGO_SIZE = 220

LAYOUTS = ("classic", "centered", "side_panel")
DEFAULT_LAYOUT = "classic"


def _font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def _data_url_to_image(data_url: str) -> Image.Image:
    _, encoded = data_url.split(",", 1)
    return Image.open(io.BytesIO(base64.b64decode(encoded))).convert("RGB")


def _to_data_url(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.convert("RGB").save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _accent_color(logo: Image.Image) -> tuple[int, int, int]:
    return logo.resize((1, 1)).getpixel((0, 0))


def _strip_background(logo: Image.Image, tolerance: int = 36) -> Image.Image:
    rgb = logo.convert("RGB")
    corners = [
        rgb.getpixel((0, 0)),
        rgb.getpixel((rgb.width - 1, 0)),
        rgb.getpixel((0, rgb.height - 1)),
        rgb.getpixel((rgb.width - 1, rgb.height - 1)),
    ]
    bg_color = tuple(sum(c[i] for c in corners) // len(corners) for i in range(3))

    bg_plate = Image.new("RGB", rgb.size, bg_color)
    diff_r, diff_g, diff_b = ImageChops.difference(rgb, bg_plate).split()
    distance = ImageChops.lighter(ImageChops.lighter(diff_r, diff_g), diff_b)
    alpha = distance.point(lambda p: 255 if p > tolerance else 0)

    result = rgb.convert("RGBA")
    result.putalpha(alpha)
    return result


def _contact_lines(contact_name: str, title: str, phone: str, email: str, address: str):
    lines = []
    name_line = " · ".join(part for part in (contact_name, title) if part)
    if name_line:
        lines.append((name_line, _BOLD_FONT_PATH, 26, (30, 30, 30)))
    for label, value in (("Tel", phone), ("Email", email), ("Add", address)):
        if value:
            lines.append((f"{label}  {value}", _REGULAR_FONT_PATH, 21, (80, 80, 80)))
    return lines


def _text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def _render_classic(card, draw, logo, accent, company_name, slogan, contact_lines):
    logo_cutout = _strip_background(logo).resize((_LOGO_SIZE, _LOGO_SIZE))
    card.paste(logo_cutout, (_PADDING, _PADDING), logo_cutout)

    bar_x = _PADDING + _LOGO_SIZE + 48
    draw.rectangle([bar_x, _PADDING, bar_x + 6, CARD_HEIGHT - _PADDING], fill=accent)

    text_x = bar_x + 40
    y = _PADDING + 8

    draw.text((text_x, y), company_name, font=_font(_BOLD_FONT_PATH, 46), fill=(20, 20, 20))
    y += 64

    if slogan:
        draw.text((text_x, y), slogan, font=_font(_REGULAR_FONT_PATH, 24), fill=(110, 110, 110))
        y += 44

    y += 16
    draw.line([(text_x, y), (CARD_WIDTH - _PADDING, y)], fill=(230, 230, 230), width=2)
    y += 32

    for text, font_path, size, color in contact_lines:
        draw.text((text_x, y), text, font=_font(font_path, size), fill=color)
        y += size + 14


def _render_centered(card, draw, logo, accent, company_name, slogan, contact_lines):
    logo_size = 180
    logo_cutout = _strip_background(logo).resize((logo_size, logo_size))
    logo_x = (CARD_WIDTH - logo_size) // 2
    logo_y = 48
    card.paste(logo_cutout, (logo_x, logo_y), logo_cutout)

    y = logo_y + logo_size + 28

    name_font = _font(_BOLD_FONT_PATH, 40)
    draw.text(((CARD_WIDTH - _text_width(draw, company_name, name_font)) / 2, y), company_name, font=name_font, fill=(20, 20, 20))
    y += 56

    if slogan:
        slogan_font = _font(_REGULAR_FONT_PATH, 22)
        draw.text(((CARD_WIDTH - _text_width(draw, slogan, slogan_font)) / 2, y), slogan, font=slogan_font, fill=(110, 110, 110))
        y += 38

    y += 14
    divider_width = 220
    draw.line(
        [((CARD_WIDTH - divider_width) / 2, y), ((CARD_WIDTH + divider_width) / 2, y)],
        fill=accent,
        width=3,
    )
    y += 28

    for text, font_path, size, color in contact_lines:
        font = _font(font_path, size)
        draw.text(((CARD_WIDTH - _text_width(draw, text, font)) / 2, y), text, font=font, fill=color)
        y += size + 14


def _render_side_panel(card, draw, logo, accent, company_name, slogan, contact_lines):
    panel_width = 350
    draw.rectangle([0, 0, panel_width, CARD_HEIGHT], fill=accent)

    logo_size = 160
    logo_cutout = _strip_background(logo).resize((logo_size, logo_size))
    card.paste(
        logo_cutout,
        ((panel_width - logo_size) // 2, (CARD_HEIGHT - logo_size) // 2),
        logo_cutout,
    )

    text_x = panel_width + 56
    y = _PADDING + 8

    draw.text((text_x, y), company_name, font=_font(_BOLD_FONT_PATH, 42), fill=(20, 20, 20))
    y += 60

    if slogan:
        draw.text((text_x, y), slogan, font=_font(_REGULAR_FONT_PATH, 22), fill=(110, 110, 110))
        y += 40

    y += 16
    draw.line([(text_x, y), (CARD_WIDTH - _PADDING, y)], fill=(230, 230, 230), width=2)
    y += 32

    for text, font_path, size, color in contact_lines:
        draw.text((text_x, y), text, font=_font(font_path, size), fill=color)
        y += size + 14


_RENDERERS = {
    "classic": _render_classic,
    "centered": _render_centered,
    "side_panel": _render_side_panel,
}


def generate_business_card(
    logo_data_url: str,
    company_name: str,
    slogan: str,
    contact_name: str = "",
    title: str = "",
    phone: str = "",
    email: str = "",
    address: str = "",
    layout: str = DEFAULT_LAYOUT,
) -> str:
    logo = _data_url_to_image(logo_data_url)
    accent = _accent_color(logo)
    contact_lines = _contact_lines(contact_name, title, phone, email, address)

    card = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(card)

    renderer = _RENDERERS.get(layout, _render_classic)
    renderer(card, draw, logo, accent, company_name, slogan, contact_lines)

    return _to_data_url(card)
