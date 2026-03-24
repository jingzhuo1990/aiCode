"""本地模型集成 - 支持 LM Studio、Ollama 等本地部署的模型"""

from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
from .base import AIModel


class LocalModel(AIModel):
    """
    本地模型 - 支持 OpenAI 兼容的本地 API

    支持的平台：
    - LM Studio (默认: http://localhost:1234/v1)
    - Ollama (http://localhost:11434/v1)
    - vLLM (自定义端口)
    - Text Generation WebUI (自定义端口)
    """

    def __init__(
        self,
        api_key: str = "not-needed",  # 本地模型通常不需要 API key
        model_name: str = "local-model",
        base_url: str = "http://localhost:1234/v1",  # LM Studio 默认地址
    ):
        super().__init__(api_key, model_name)
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.base_url = base_url

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """生成文本"""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        return response.choices[0].message.content

    async def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 4000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """对话式交互"""
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        return response.choices[0].message.content

    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "provider": "local",
            "model": self.model_name,
            "base_url": self.base_url,
            "family": "local",
            "supports_system_prompt": True,
            "supports_streaming": True,
        }


# 预设配置
LOCAL_CONFIGS = {
    "lm_studio": {
        "base_url": "http://localhost:1234/v1",
        "description": "LM Studio 默认配置",
    },
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "description": "Ollama 默认配置",
    },
    "vllm": {
        "base_url": "http://localhost:8000/v1",
        "description": "vLLM 默认配置",
    },
    "text_gen_webui": {
        "base_url": "http://localhost:5000/v1",
        "description": "Text Generation WebUI",
    },
}
