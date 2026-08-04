import uuid

from fastapi import APIRouter, HTTPException

from app.graph import compiled_graph
from app.schemas import (
    GenerateCardRequest,
    GenerateCardResponse,
    GenerateLogosRequest,
    GenerateLogosResponse,
)

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
    images = state.values.get("images") if state.values else None
    if not images:
        raise HTTPException(status_code=404, detail="로고를 먼저 생성해주세요.")
    if not 0 <= payload.logo_index < len(images):
        raise HTTPException(status_code=400, detail="유효하지 않은 로고 번호입니다.")

    compiled_graph.update_state(
        config,
        {
            "logo_index": payload.logo_index,
            "contact_name": (payload.contact_name or "").strip(),
            "title": (payload.title or "").strip(),
            "phone": (payload.phone or "").strip(),
            "email": (payload.email or "").strip(),
            "address": (payload.address or "").strip(),
        },
    )
    result = compiled_graph.invoke(None, config=config)

    if "card_image" not in result:
        raise HTTPException(status_code=409, detail="명함을 아직 생성할 수 없습니다.")

    return GenerateCardResponse(
        card_image=result["card_image"],
        steps=result["steps"],
    )
