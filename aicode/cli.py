"""命令行接口"""

import asyncio
import click
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path

from .config import settings
from .models.claude import ClaudeModel
from .models.openai import OpenAIModel
from .models.qwen import QwenModel
from .models.local import LocalModel
from .agent.code_generator import CodeGenerator
from .agent.code_modifier import CodeModifier
from .agent.file_handler import FileHandler

console = Console()


def get_model(provider: str, model_name: str):
    """获取 AI 模型实例"""
    if provider == "claude":
        api_key = settings.anthropic_api_key
        if not api_key:
            console.print("[red]错误: 未设置 ANTHROPIC_API_KEY[/red]")
            raise click.Abort()
        return ClaudeModel(api_key=api_key, model_name=model_name)
    elif provider == "openai":
        api_key = settings.openai_api_key
        if not api_key:
            console.print("[red]错误: 未设置 OPENAI_API_KEY[/red]")
            raise click.Abort()
        return OpenAIModel(api_key=api_key, model_name=model_name)
    elif provider == "qwen":
        api_key = settings.qwen_api_key
        if not api_key:
            console.print("[red]错误: 未设置 QWEN_API_KEY[/red]")
            raise click.Abort()
        return QwenModel(api_key=api_key, model_name=model_name)
    elif provider == "local":
        # 本地模型不需要 API key
        return LocalModel(
            model_name=model_name or settings.local_model_name,
            base_url=settings.local_model_base_url
        )
    else:
        console.print(f"[red]错误: 不支持的提供商 '{provider}'[/red]")
        raise click.Abort()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """AI Coding Agent - 智能编码助手"""
    pass


# 导入 agent CLI 并注册
try:
    from .cli_agent import agent_cli
    cli.add_command(agent_cli, name="agent")
except ImportError:
    pass  # Agent CLI 可选


@cli.command()
@click.argument("prompt")
@click.option("--provider", default=None, help="AI 提供商 (claude/openai/qwen/local)")
@click.option("--model", default=None, help="模型名称")
@click.option("--language", default="python", help="编程语言")
@click.option("--output", "-o", type=click.Path(), help="输出文件路径")
@click.option("--temperature", default=0.7, type=float, help="温度参数 (0.0-1.0)")
def generate(prompt, provider, model, language, output, temperature):
    """生成新代码"""
    async def run():
        provider_name = provider or settings.default_provider
        model_name = model or settings.default_model

        console.print(f"\n[cyan]使用模型:[/cyan] {provider_name}/{model_name}")
        console.print(f"[cyan]编程语言:[/cyan] {language}")
        console.print(f"[cyan]生成需求:[/cyan] {prompt}\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description="正在生成代码...", total=None)

            model_instance = get_model(provider_name, model_name)
            generator = CodeGenerator(model_instance)

            code = await generator.generate_code(
                prompt=prompt,
                language=language,
                temperature=temperature,
            )

        # 显示生成的代码
        syntax = Syntax(code, language, theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="[green]生成的代码[/green]", border_style="green"))

        # 保存到文件
        if output:
            file_handler = FileHandler()
            await file_handler.write_file(output, code)
            console.print(f"\n[green]✓ 代码已保存到:[/green] {output}")

    asyncio.run(run())


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.argument("instruction")
@click.option("--provider", default=None, help="AI 提供商 (claude/openai)")
@click.option("--model", default=None, help="模型名称")
@click.option("--backup/--no-backup", default=True, help="是否备份原文件")
@click.option("--dry-run", is_flag=True, help="预览修改，不实际写入")
@click.option("--temperature", default=0.7, type=float, help="温度参数")
def modify(file_path, instruction, provider, model, backup, dry_run, temperature):
    """修改现有代码"""
    async def run():
        provider_name = provider or settings.default_provider
        model_name = model or settings.default_model

        console.print(f"\n[cyan]使用模型:[/cyan] {provider_name}/{model_name}")
        console.print(f"[cyan]目标文件:[/cyan] {file_path}")
        console.print(f"[cyan]修改指令:[/cyan] {instruction}")
        if dry_run:
            console.print("[yellow]预览模式: 不会修改文件[/yellow]")
        console.print()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description="正在修改代码...", total=None)

            model_instance = get_model(provider_name, model_name)
            file_handler = FileHandler()
            modifier = CodeModifier(model_instance, file_handler)

            result = await modifier.modify_file(
                file_path=file_path,
                instruction=instruction,
                backup=backup,
                dry_run=dry_run,
            )

        # 显示结果
        console.print(Panel.fit(
            f"""[green]修改完成[/green]

原始行数: {result['original_lines']}
修改后行数: {result['modified_lines']}
编程语言: {result['language']}
{'[yellow]预览模式（未实际修改）[/yellow]' if dry_run else '[green]已保存修改[/green]'}
{f"备份文件: {result.get('backup_path', 'N/A')}" if result.get('backup_created') else ''}""",
            title="修改结果",
            border_style="green",
        ))

        if dry_run and "preview" in result:
            console.print("\n[cyan]预览（前500字符）:[/cyan]")
            console.print(result["preview"])

    asyncio.run(run())


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--provider", default=None, help="AI 提供商")
@click.option("--model", default=None, help="模型名称")
def analyze(file_path, provider, model):
    """分析代码并给出解释"""
    async def run():
        provider_name = provider or settings.default_provider
        model_name = model or settings.default_model

        console.print(f"\n[cyan]分析文件:[/cyan] {file_path}\n")

        file_handler = FileHandler()

        # 读取文件
        code = await file_handler.read_file(file_path)

        # 获取文件信息
        file_info = file_handler.get_file_info(file_path)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description="正在分析代码...", total=None)

            model_instance = get_model(provider_name, model_name)
            generator = CodeGenerator(model_instance)

            # 推断语言
            extension = file_info["extension"]
            language = CodeModifier._get_language_from_extension(extension)

            explanation = await generator.explain_code(code, language=language)

        # 显示分析结果
        console.print(Panel(
            explanation,
            title=f"[green]代码分析结果 - {file_info['name']}[/green]",
            border_style="green",
        ))

    asyncio.run(run())


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--provider", default=None, help="AI 提供商")
@click.option("--model", default=None, help="模型名称")
@click.option(
    "--type",
    "refactor_type",
    default="general",
    type=click.Choice(["general", "performance", "readability", "security", "simplify"]),
    help="重构类型",
)
@click.option("--output", "-o", type=click.Path(), help="输出文件路径")
def refactor(file_path, provider, model, refactor_type, output):
    """重构代码"""
    async def run():
        provider_name = provider or settings.default_provider
        model_name = model or settings.default_model

        console.print(f"\n[cyan]重构文件:[/cyan] {file_path}")
        console.print(f"[cyan]重构类型:[/cyan] {refactor_type}\n")

        file_handler = FileHandler()
        code = await file_handler.read_file(file_path)
        file_info = file_handler.get_file_info(file_path)
        language = CodeModifier._get_language_from_extension(file_info["extension"])

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description="正在重构代码...", total=None)

            model_instance = get_model(provider_name, model_name)
            modifier = CodeModifier(model_instance, file_handler)

            refactored_code = await modifier.refactor_code(
                code=code,
                refactor_type=refactor_type,
                language=language,
            )

        # 显示重构后的代码
        syntax = Syntax(refactored_code, language, theme="monokai", line_numbers=True)
        console.print(Panel(
            syntax,
            title="[green]重构后的代码[/green]",
            border_style="green",
        ))

        # 保存
        output_path = output or file_path
        await file_handler.write_file(output_path, refactored_code)
        console.print(f"\n[green]✓ 重构后的代码已保存到:[/green] {output_path}")

    asyncio.run(run())


@cli.command()
def info():
    """显示配置信息"""
    console.print("\n[bold cyan]AI Coding Agent 配置信息[/bold cyan]\n")

    config_info = f"""
[cyan]默认提供商:[/cyan] {settings.default_provider}
[cyan]默认模型:[/cyan] {settings.default_model}
[cyan]最大 Tokens:[/cyan] {settings.max_tokens}
[cyan]温度参数:[/cyan] {settings.temperature}
[cyan]API 服务地址:[/cyan] {settings.api_host}:{settings.api_port}

[cyan]Claude API Key:[/cyan] {'已设置 ✓' if settings.anthropic_api_key else '未设置 ✗'}
[cyan]OpenAI API Key:[/cyan] {'已设置 ✓' if settings.openai_api_key else '未设置 ✗'}
[cyan]Qwen API Key:[/cyan] {'已设置 ✓' if settings.qwen_api_key else '未设置 ✗'}
[cyan]Local Model:[/cyan] {settings.local_model_base_url} ({settings.local_model_name})
"""

    console.print(Panel(config_info, border_style="cyan"))


if __name__ == "__main__":
    cli()
