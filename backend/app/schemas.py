from typing import Literal, Optional

from pydantic import BaseModel, Field


class LogoStep(BaseModel):
    id: str
    label: str
    status: str  # "pending" | "active" | "done"


class GenerateLogosRequest(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=60)
    slogan: str = Field(..., min_length=1, max_length=120)
    industry: Optional[str] = None
    style: Optional[str] = None
    colors: Optional[str] = None


class GenerateLogosResponse(BaseModel):
    generated_prompt: str
    prompt_source: str  # "llm" | "template"
    images: list[str]  # base64 data URLs
    image_source: str  # "huggingface" | "openai" | "placeholder"
    steps: list[LogoStep]


class GenerateCardRequest(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=60)
    slogan: str = Field(..., min_length=1, max_length=120)
    logo_data_url: str
    contact_name: Optional[str] = None
    title: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    layout: Literal["classic", "centered", "side_panel"] = "classic"


class GenerateCardResponse(BaseModel):
    card_image: str  # base64 data URL
    steps: list[LogoStep]
