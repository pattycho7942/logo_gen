import base64
import io
import logging
import random

from huggingface_hub import InferenceClient
from PIL import Image, ImageDraw, ImageFont

from app.config import settings

logger = logging.getLogger(__name__)

_PALETTES = [
    {"bg": (238, 233, 254), "accent": (109, 40, 217), "text": (255, 255, 255)},
    {"bg": (224, 242, 254), "accent": (14, 116, 144), "text": (255, 255, 255)},
    {"bg": (254, 242, 232), "accent": (194, 65, 12), "text": (255, 255, 255)},
]


def _to_data_url(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.convert("RGB").save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _initials(company_name: str) -> str:
    words = [w for w in company_name.strip().split() if w]
    if not words:
        return "?"
    if len(words) == 1:
        return words[0][:2].upper()
    return (words[0][0] + words[1][0]).upper()


def _is_renderable_ascii(text: str) -> bool:
    # PIL's built-in bitmap font only has glyphs for ASCII — Korean/CJK/etc.
    # would render as tofu boxes, so fall back to an abstract mark for those.
    return bool(text) and all(ch.isascii() and not ch.isspace() for ch in text)


def _draw_abstract_mark(draw: ImageDraw.ImageDraw, size: int, variant_index: int, accent: tuple, bg: tuple) -> None:
    margin = 96
    box = [margin, margin, size - margin, size - margin]
    shape = variant_index % 3
    if shape == 0:
        draw.ellipse(box, fill=accent)
        inset = 56
        draw.ellipse(
            [margin + inset, margin + inset, size - margin - inset, size - margin - inset],
            fill=bg,
        )
    elif shape == 1:
        cx = size / 2
        draw.polygon(
            [(cx, margin), (size - margin, size - margin), (margin, size - margin)],
            fill=accent,
        )
    else:
        r = (size - 2 * margin) * 0.62
        draw.ellipse([margin, size / 2 - r / 2, margin + r, size / 2 + r / 2], fill=accent)
        draw.ellipse(
            [size - margin - r, size / 2 - r / 2, size - margin, size / 2 + r / 2],
            fill=accent,
        )


def _placeholder_logo(company_name: str, variant_index: int) -> Image.Image:
    palette = _PALETTES[variant_index % len(_PALETTES)]
    size = 512
    image = Image.new("RGB", (size, size), palette["bg"])
    draw = ImageDraw.Draw(image)

    initials = _initials(company_name)
    if _is_renderable_ascii(initials):
        margin = 96
        draw.rounded_rectangle(
            [margin, margin, size - margin, size - margin],
            radius=48,
            fill=palette["accent"],
        )
        font = ImageFont.load_default(size=140)
        bbox = draw.textbbox((0, 0), initials, font=font)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(
            ((size - text_w) / 2 - bbox[0], (size - text_h) / 2 - bbox[1]),
            initials,
            fill=palette["text"],
            font=font,
        )
    else:
        _draw_abstract_mark(draw, size, variant_index, palette["accent"], palette["bg"])

    return image


def _placeholder_logos(company_name: str, count: int) -> list[str]:
    return [_to_data_url(_placeholder_logo(company_name, i)) for i in range(count)]


def generate_logos(prompt: str, company_name: str, count: int = 3) -> tuple[list[str], str]:
    if not settings.image_gen_enabled:
        return _placeholder_logos(company_name, count), "placeholder"

    try:
        # huggingface_hub >=0.26 routes through the newer Inference Providers
        # system instead of the retired api-inference.huggingface.co host;
        # "hf-inference" keeps this on HuggingFace's own free-tier serverless
        # inference rather than a paid third-party provider.
        client = InferenceClient(model=settings.hf_t2i_model, token=settings.hf_token, provider="hf-inference")
        images: list[str] = []
        for _ in range(count):
            seed = random.randint(0, 2**31 - 1)
            pil_image = client.text_to_image(prompt, seed=seed)
            images.append(_to_data_url(pil_image))
        if len(images) != count:
            raise ValueError("incomplete image generation result")
        return images, "huggingface"
    except Exception:
        logger.exception("HuggingFace text_to_image call failed, falling back to placeholder")
        return _placeholder_logos(company_name, count), "placeholder"
