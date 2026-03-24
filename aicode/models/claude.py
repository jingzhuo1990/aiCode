"""Claude (Anthropic) 模型集成"""

from typing import Dict, Any, List, Optional
from anthropic import AsyncAnthropic
from .base import AIModel


class ClaudeModel(AIModel):
    """Claude AI 模型"""

    def __init__(self, api_key: str, model_name: str = "claude-sonnet-4-6"):
        super().__init__(api_key, model_name)
        self.client = AsyncAnthropic(api_key=api_key)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """生成文本"""
        messages = [{"role": "user", "content": prompt}]

        request_params = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if system_prompt:
            request_params["system"] = system_prompt

        response = await self.client.messages.create(**request_params)

        return response.content[0].text

    async def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 4000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """对话式交互"""
        # 提取 system 消息
        system_prompt = None
        chat_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                chat_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        request_params = {
            "model": self.model_name,
            "messages": chat_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if system_prompt:
            request_params["system"] = system_prompt

        response = await self.client.messages.create(**request_params)

        return response.content[0].text

    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "provider": "anthropic",
            "model": self.model_name,
            "family": "claude",
            "supports_system_prompt": True,
            "supports_streaming": True,
        }
