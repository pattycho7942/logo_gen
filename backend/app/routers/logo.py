from fastapi import APIRouter

from app.graph import STEP_DEFS, compiled_graph
from app.schemas import (
    GenerateCardRequest,
    GenerateCardResponse,
    GenerateLogosRequest,
    GenerateLogosResponse,
)
from app.services.card_service import generate_business_card as render_business_card

router = APIRouter(prefix="/api", tags=["logo"])


@router.post("/logo/generate", response_model=GenerateLogosResponse)
def generate_logo_images(payload: GenerateLogosRequest) -> GenerateLogosResponse:
    result = compiled_graph.invoke(
        {
            "company_name": payload.company_name.strip(),
            "slogan": payload.slogan.strip(),
            "industry": (payload.industry or "").strip(),
            "style": (payload.style or "").strip(),
            "colors": (payload.colors or "").strip(),
        }
    )

    return GenerateLogosResponse(
        generated_prompt=result["generated_prompt"],
        prompt_source=result["prompt_source"],
        images=result["images"],
        image_source=result["image_source"],
        steps=result["steps"],
    )


@router.post("/card/generate", response_model=GenerateCardResponse)
def generate_business_card(payload: GenerateCardRequest) -> GenerateCardResponse:
    card_image = render_business_card(
        logo_data_url=payload.logo_data_url,
        company_name=payload.company_name.strip(),
        slogan=payload.slogan.strip(),
        contact_name=(payload.contact_name or "").strip(),
        title=(payload.title or "").strip(),
        phone=(payload.phone or "").strip(),
        email=(payload.email or "").strip(),
        address=(payload.address or "").strip(),
        layout=payload.layout,
    )
    steps = [{"id": step_id, "label": label, "status": "done"} for step_id, label in STEP_DEFS]

    return GenerateCardResponse(card_image=card_image, steps=steps)
