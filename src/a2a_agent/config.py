from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_model: str = "llama3"
    agent_name: str = "a2a-agent"
    agent_port: int = 8000
    langfuse_enabled: bool = False
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "http://localhost:3000"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
