import uuid

from fastapi import APIRouter, HTTPException

from app.graph import compiled_graph
from app.schemas import (
    GenerateLogosRequest,
    GenerateLogosResponse,
    GeneratePromptRequest,
    GeneratePromptResponse,
)

router = APIRouter(prefix="/api", tags=["logo"])


@router.post("/prompt/generate", response_model=GeneratePromptResponse)
def generate_prompt(payload: GeneratePromptRequest) -> GeneratePromptResponse:
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

    return GeneratePromptResponse(
        thread_id=thread_id,
        generated_prompt=result["generated_prompt"],
        prompt_source=result["prompt_source"],
        steps=result["steps"],
    )


@router.post("/logo/generate", response_model=GenerateLogosResponse)
def generate_logo_images(payload: GenerateLogosRequest) -> GenerateLogosResponse:
    config = {"configurable": {"thread_id": payload.thread_id}}

    state = compiled_graph.get_state(config)
    if not state.values:
        raise HTTPException(status_code=404, detail="알 수 없는 thread_id 입니다. 프롬프트를 먼저 생성해주세요.")

    result = compiled_graph.invoke(None, config=config)

    if "images" not in result:
        raise HTTPException(status_code=409, detail="프롬프트가 아직 생성되지 않았습니다.")

    return GenerateLogosResponse(
        images=result["images"],
        image_source=result["image_source"],
        steps=result["steps"],
    )
