"""AI 模型基础接口"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class AIModel(ABC):
    """AI 模型基类"""

    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        生成文本

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            max_tokens: 最大生成token数
            temperature: 温度参数
            **kwargs: 其他模型特定参数

        Returns:
            生成的文本内容
        """
        pass

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 4000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        对话式交互

        Args:
            messages: 消息列表，格式 [{"role": "user/assistant", "content": "..."}]
            max_tokens: 最大生成token数
            temperature: 温度参数
            **kwargs: 其他模型特定参数

        Returns:
            AI 响应内容
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息

        Returns:
            包含模型名称、提供商等信息的字典
        """
        pass
