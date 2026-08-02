import logging

from openai import OpenAI

from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a branding expert who writes concise, vivid prompts for a "
    "text-to-image AI model to generate a single company LOGO (not a "
    "poster, not a scene). Given a company name, slogan, industry, style "
    "preference and color preference, respond with ONE English prompt "
    "sentence (max 60 words) describing a clean, professional, vector-style "
    "logo. Always mention: it is a logo, flat/vector design, simple "
    "background, the company name as a wordmark or nearby symbol. Do not "
    "add quotes or extra commentary — output only the prompt text."
)


def _template_prompt(company_name: str, slogan: str, industry: str, style: str, colors: str) -> str:
    parts = [
        f'a clean, professional vector logo design for a company named "{company_name}"',
        f'with the slogan "{slogan}"' if slogan else "",
        f"in the {industry} industry" if industry else "",
        f"{style} style" if style else "modern minimal style",
        f"using {colors} color palette" if colors else "using a balanced color palette",
        "flat vector, simple plain background, centered composition, high contrast, no text artifacts, logo mark",
    ]
    return ", ".join(p for p in parts if p)


def refine_prompt(
    company_name: str,
    slogan: str,
    industry: str = "",
    style: str = "",
    colors: str = "",
) -> tuple[str, str]:
    if not settings.llm_enabled:
        return _template_prompt(company_name, slogan, industry, style, colors), "template"

    try:
        client = OpenAI(api_key=settings.openai_api_key)
        user_content = (
            f"Company name: {company_name}\n"
            f"Slogan: {slogan}\n"
            f"Industry: {industry or 'unspecified'}\n"
            f"Style preference: {style or 'unspecified'}\n"
            f"Color preference: {colors or 'unspecified'}"
        )
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0.7,
            max_tokens=150,
        )
        text = (response.choices[0].message.content or "").strip()
        if not text:
            raise ValueError("empty LLM response")
        return text, "llm"
    except Exception:
        logger.exception("OpenAI prompt refinement failed, falling back to template")
        return _template_prompt(company_name, slogan, industry, style, colors), "template"
