"""配置管理模块"""

from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """应用配置"""

    # AI Provider API Keys
    anthropic_api_key: str = "sk-9220a3c554c4465fbffcf0fb3faf3e4c"
    openai_api_key: str = ""
    qwen_api_key: str = ""

    # Local Model Settings
    local_model_base_url: str = "http://localhost:1234/v1"  # LM Studio 默认
    local_model_name: str = "local-model"

    # Default settings
    default_provider: Literal["claude", "openai", "qwen", "local"] = "claude"
    default_model: str = "claude-sonnet-4-6"
    max_tokens: int = 8000
    temperature: float = 0.7

    # API Server settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings()
