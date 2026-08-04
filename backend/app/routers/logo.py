import uuid

from fastapi import APIRouter, HTTPException

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
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    result = compiled_graph.invoke(
        {
            "company_name": payload.company_name.strip(),
            "slogan": payload.slogan.strip(),
            "industry": (payload.industry or "").strip(),
            "style": (payload.style or "").strip(),
            "colors": (payload.colors or "").strip(),
        },
        config=config,
    )

    return GenerateLogosResponse(
        thread_id=thread_id,
        generated_prompt=result["generated_prompt"],
        prompt_source=result["prompt_source"],
        images=result["images"],
        image_source=result["image_source"],
        steps=result["steps"],
    )


@router.post("/card/generate", response_model=GenerateCardResponse)
def generate_business_card(payload: GenerateCardRequest) -> GenerateCardResponse:
    config = {"configurable": {"thread_id": payload.thread_id}}

    state = compiled_graph.get_state(config)
    if not state.values or "images" not in state.values:
        raise HTTPException(status_code=404, detail="로고를 먼저 생성해주세요.")

    images = state.values["images"]
    if not 0 <= payload.logo_index < len(images):
        raise HTTPException(status_code=400, detail="유효하지 않은 로고 번호입니다.")

    contact_name = (payload.contact_name or "").strip()
    title = (payload.title or "").strip()
    phone = (payload.phone or "").strip()
    email = (payload.email or "").strip()
    address = (payload.address or "").strip()

    card_image = render_business_card(
        logo_data_url=images[payload.logo_index],
        company_name=state.values["company_name"],
        slogan=state.values["slogan"],
        contact_name=contact_name,
        title=title,
        phone=phone,
        email=email,
        address=address,
    )
    steps = [{"id": step_id, "label": label, "status": "done"} for step_id, label in STEP_DEFS]

    compiled_graph.update_state(
        config,
        {
            "logo_index": payload.logo_index,
            "contact_name": contact_name,
            "title": title,
            "phone": phone,
            "email": email,
            "address": address,
            "card_image": card_image,
            "steps": steps,
        },
    )

    return GenerateCardResponse(card_image=card_image, steps=steps)
