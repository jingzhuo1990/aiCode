"""API 服务器"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Literal
import uvicorn

from .config import settings
from .models.claude import ClaudeModel
from .models.openai import OpenAIModel
from .agent.code_generator import CodeGenerator
from .agent.code_modifier import CodeModifier
from .agent.file_handler import FileHandler

# 创建 FastAPI 应用
app = FastAPI(
    title="AI Coding Agent API",
    description="智能编码助手 API 服务",
    version="0.1.0",
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic 模型定义
class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="代码生成需求描述")
    provider: Literal["claude", "openai"] = Field(
        default="claude",
        description="AI 提供商"
    )
    model: Optional[str] = Field(None, description="模型名称")
    language: str = Field(default="python", description="编程语言")
    context: Optional[str] = Field(None, description="额外上下文信息")
    max_tokens: int = Field(default=4000, ge=100, le=8000)
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)


class ModifyRequest(BaseModel):
    file_path: str = Field(..., description="要修改的文件路径")
    instruction: str = Field(..., description="修改指令")
    provider: Literal["claude", "openai"] = Field(default="claude")
    model: Optional[str] = Field(None)
    backup: bool = Field(default=True, description="是否备份原文件")
    dry_run: bool = Field(default=False, description="是否只预览")


class RefactorRequest(BaseModel):
    code: str = Field(..., description="要重构的代码")
    refactor_type: Literal[
        "general", "performance", "readability", "security", "simplify"
    ] = Field(default="general")
    provider: Literal["claude", "openai"] = Field(default="claude")
    model: Optional[str] = Field(None)
    language: str = Field(default="python")


class AnalyzeRequest(BaseModel):
    code: str = Field(..., description="要分析的代码")
    provider: Literal["claude", "openai"] = Field(default="claude")
    model: Optional[str] = Field(None)
    language: str = Field(default="python")


class CodeResponse(BaseModel):
    code: str
    model_used: str
    provider: str


class AnalysisResponse(BaseModel):
    explanation: str
    model_used: str
    provider: str


# 辅助函数
def get_model(provider: str, model_name: Optional[str] = None):
    """获取 AI 模型实例"""
    if model_name is None:
        model_name = settings.default_model

    if provider == "claude":
        if not settings.anthropic_api_key:
            raise HTTPException(
                status_code=500,
                detail="未设置 ANTHROPIC_API_KEY"
            )
        return ClaudeModel(api_key=settings.anthropic_api_key, model_name=model_name)
    elif provider == "openai":
        if not settings.openai_api_key:
            raise HTTPException(
                status_code=500,
                detail="未设置 OPENAI_API_KEY"
            )
        return OpenAIModel(api_key=settings.openai_api_key, model_name=model_name)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的提供商: {provider}"
        )


# API 路由
@app.get("/")
async def root():
    """健康检查"""
    return {
        "status": "ok",
        "service": "AI Coding Agent API",
        "version": "0.1.0",
    }


@app.post("/api/generate", response_model=CodeResponse)
async def generate_code(request: GenerateRequest):
    """生成代码"""
    try:
        model = get_model(request.provider, request.model)
        generator = CodeGenerator(model)

        code = await generator.generate_code(
            prompt=request.prompt,
            language=request.language,
            context=request.context,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )

        return CodeResponse(
            code=code,
            model_used=model.model_name,
            provider=request.provider,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/modify")
async def modify_code(request: ModifyRequest):
    """修改代码文件"""
    try:
        model = get_model(request.provider, request.model)
        file_handler = FileHandler()
        modifier = CodeModifier(model, file_handler)

        result = await modifier.modify_file(
            file_path=request.file_path,
            instruction=request.instruction,
            backup=request.backup,
            dry_run=request.dry_run,
        )

        result["model_used"] = model.model_name
        result["provider"] = request.provider

        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/refactor", response_model=CodeResponse)
async def refactor_code(request: RefactorRequest):
    """重构代码"""
    try:
        model = get_model(request.provider, request.model)
        file_handler = FileHandler()
        modifier = CodeModifier(model, file_handler)

        refactored_code = await modifier.refactor_code(
            code=request.code,
            refactor_type=request.refactor_type,
            language=request.language,
        )

        return CodeResponse(
            code=refactored_code,
            model_used=model.model_name,
            provider=request.provider,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_code(request: AnalyzeRequest):
    """分析代码"""
    try:
        model = get_model(request.provider, request.model)
        generator = CodeGenerator(model)

        explanation = await generator.explain_code(
            code=request.code,
            language=request.language,
        )

        return AnalysisResponse(
            explanation=explanation,
            model_used=model.model_name,
            provider=request.provider,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/config")
async def get_config():
    """获取配置信息"""
    return {
        "default_provider": settings.default_provider,
        "default_model": settings.default_model,
        "max_tokens": settings.max_tokens,
        "temperature": settings.temperature,
        "anthropic_configured": bool(settings.anthropic_api_key),
        "openai_configured": bool(settings.openai_api_key),
    }


@app.get("/api/models")
async def list_models():
    """列出支持的模型"""
    return {
        "claude": [
            "claude-opus-4-6",
            "claude-sonnet-4-6",
            "claude-haiku-4-5",
        ],
        "openai": [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
        ],
    }


def start_server(host: str = None, port: int = None):
    """启动服务器"""
    host = host or settings.api_host
    port = port or settings.api_port

    uvicorn.run(
        "aicode.server:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    start_server()
