from typing import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from app.services.image_service import generate_logos
from app.services.llm_service import refine_prompt

STEP_DEFS = [
    ("collect_input", "입력 확인"),
    ("generate_prompt", "AI 프롬프트 생성 (ChatGPT)"),
    ("generate_logos", "로고 이미지 생성 (HuggingFace)"),
    ("generate_business_card", "명함 생성 (Pillow)"),
    ("done", "완료"),
]


class LogoState(TypedDict, total=False):
    company_name: str
    slogan: str
    industry: str
    style: str
    colors: str
    generated_prompt: str
    prompt_source: str
    images: list[str]
    image_source: str
    logo_index: int
    contact_name: str
    title: str
    phone: str
    email: str
    address: str
    layout: str
    card_image: str
    steps: list[dict]


def _initial_steps() -> list[dict]:
    return [{"id": step_id, "label": label, "status": "pending"} for step_id, label in STEP_DEFS]


def _mark_done(steps: list[dict], *step_ids: str) -> list[dict]:
    ids = set(step_ids)
    return [
        {**step, "status": "done" if step["id"] in ids else step["status"]}
        for step in steps
    ]


def collect_input_node(state: LogoState) -> dict:
    steps = state.get("steps") or _initial_steps()
    return {"steps": _mark_done(steps, "collect_input")}


def generate_prompt_node(state: LogoState) -> dict:
    prompt, source = refine_prompt(
        company_name=state["company_name"],
        slogan=state["slogan"],
        industry=state.get("industry", ""),
        style=state.get("style", ""),
        colors=state.get("colors", ""),
    )
    steps = _mark_done(state.get("steps") or _initial_steps(), "generate_prompt")
    return {"generated_prompt": prompt, "prompt_source": source, "steps": steps}


def generate_logos_node(state: LogoState) -> dict:
    images, source = generate_logos(
        prompt=state["generated_prompt"],
        company_name=state["company_name"],
        count=3,
    )
    steps = _mark_done(state.get("steps") or _initial_steps(), "generate_logos")
    return {"images": images, "image_source": source, "steps": steps}


def build_graph():
    builder = StateGraph(LogoState)
    builder.add_node("collect_input", collect_input_node)
    builder.add_node("generate_prompt", generate_prompt_node)
    builder.add_node("generate_logos", generate_logos_node)

    builder.set_entry_point("collect_input")
    builder.add_edge("collect_input", "generate_prompt")
    builder.add_edge("generate_prompt", "generate_logos")
    builder.add_edge("generate_logos", END)

    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)


compiled_graph = build_graph()
