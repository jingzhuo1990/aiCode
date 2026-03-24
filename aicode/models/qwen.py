"""Qwen (通义千问) 模型集成"""

from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
from .base import AIModel


class QwenModel(AIModel):
    """
    Qwen (通义千问) 模型

    使用 OpenAI 兼容的接口访问 Qwen 模型
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = "qwen-max",
        base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    ):
        super().__init__(api_key, model_name)
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )

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
            "provider": "qwen",
            "model": self.model_name,
            "family": "qwen",
            "supports_system_prompt": True,
            "supports_streaming": True,
        }


# Qwen 可用的模型列表
QWEN_MODELS = {
    "qwen-max": "通义千问最强模型，适合复杂任务",
    "qwen-plus": "性能和效果均衡的模型",
    "qwen-turbo": "快速响应，性价比高",
    "qwen-long": "支持长文本的模型",
    "qwen-coder-plus": "专门针对代码优化的模型（推荐用于编程）",
    "qwen-coder-turbo": "代码生成快速版本",
}
