import base64
import io
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

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


def _background_mask(rgb: Image.Image, tolerance: int, global_cap: int, work_size: int) -> Image.Image:
    # Flood-fills from the image border inward, comparing each candidate pixel
    # only to its already-confirmed-background neighbor (not one fixed color).
    # That lets it follow soft gradients/vignettes in generated logos while
    # still stopping at the mark's sharp-contrast edge, regardless of how
    # large a solid-color area the mark itself covers.
    #
    # A per-step-only check is fooled by anti-aliased mark edges: the smooth
    # ramp from background into the mark's color looks like just another
    # gradient one pixel at a time, so the fill can leak straight through and
    # swallow the whole mark. global_cap bounds how far a pixel's color is
    # allowed to drift from the border's own average before it can still be
    # called "background", which a real gradient background stays within but
    # a leak into a saturated mark color does not.
    small = rgb.resize((work_size, work_size), Image.BILINEAR)
    px = small.load()
    w = h = work_size

    border_samples = []
    for x in range(w):
        border_samples.append(px[x, 0])
        border_samples.append(px[x, h - 1])
    for y in range(h):
        border_samples.append(px[0, y])
        border_samples.append(px[w - 1, y])
    ref = tuple(sum(c[i] for c in border_samples) // len(border_samples) for i in range(3))

    def within_cap(r: int, g: int, b: int) -> bool:
        return max(abs(r - ref[0]), abs(g - ref[1]), abs(b - ref[2])) <= global_cap

    visited = [[False] * w for _ in range(h)]
    is_background = [[False] * w for _ in range(h)]
    queue: deque[tuple[int, int]] = deque()

    for x in range(w):
        for y in (0, h - 1):
            if within_cap(*px[x, y]):
                visited[y][x] = True
                queue.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if not visited[y][x] and within_cap(*px[x, y]):
                visited[y][x] = True
                queue.append((x, y))

    while queue:
        x, y = queue.popleft()
        is_background[y][x] = True
        r0, g0, b0 = px[x, y]
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and not visited[ny][nx]:
                r1, g1, b1 = px[nx, ny]
                if max(abs(r1 - r0), abs(g1 - g0), abs(b1 - b0)) <= tolerance and within_cap(r1, g1, b1):
                    visited[ny][nx] = True
                    queue.append((nx, ny))

    mask = Image.new("L", (w, h))
    mask.putdata([0 if is_background[y][x] else 255 for y in range(h) for x in range(w)])
    return mask.resize(rgb.size, Image.BILINEAR)


def _strip_background(logo: Image.Image, tolerance: int = 18, global_cap: int = 90, work_size: int = 256) -> Image.Image:
    rgb = logo.convert("RGB")
    alpha = _background_mask(rgb, tolerance, global_cap, work_size)

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
