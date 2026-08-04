import base64
import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

_FONT_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"
_REGULAR_FONT_PATH = _FONT_DIR / "NanumGothic.ttf"
_BOLD_FONT_PATH = _FONT_DIR / "NanumGothicBold.ttf"

CARD_WIDTH = 1050
CARD_HEIGHT = 600
_PADDING = 64
_LOGO_SIZE = 220


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


def generate_business_card(
    logo_data_url: str,
    company_name: str,
    slogan: str,
    contact_name: str = "",
    title: str = "",
    phone: str = "",
    email: str = "",
    address: str = "",
) -> str:
    logo = _data_url_to_image(logo_data_url)
    accent = _accent_color(logo)

    card = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(card)

    card.paste(logo.resize((_LOGO_SIZE, _LOGO_SIZE)), (_PADDING, _PADDING))

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

    name_line = " · ".join(part for part in (contact_name, title) if part)
    if name_line:
        draw.text((text_x, y), name_line, font=_font(_BOLD_FONT_PATH, 26), fill=(30, 30, 30))
        y += 40

    for label, value in (("Tel", phone), ("Email", email), ("Add", address)):
        if not value:
            continue
        draw.text((text_x, y), f"{label}  {value}", font=_font(_REGULAR_FONT_PATH, 21), fill=(80, 80, 80))
        y += 35

    return _to_data_url(card)
