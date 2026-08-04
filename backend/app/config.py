from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    hf_token: str = ""
    hf_t2i_model: str = "black-forest-labs/FLUX.1-schnell"

    frontend_origins: str = (
        "http://localhost:5173,https://logo-gen-ten.vercel.app,"
        "https://logo-1wkqusnzm-patty1103.vercel.app"
    )

    @property
    def frontend_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]

    @property
    def llm_enabled(self) -> bool:
        return bool(self.openai_api_key)

    @property
    def image_gen_enabled(self) -> bool:
        return bool(self.hf_token)


settings = Settings()
