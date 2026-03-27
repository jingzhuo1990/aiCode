"""CLI for Agent mode - 支持 ReAct 和 Plan-Execute"""

import asyncio
import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path

from .config import settings
from .models.claude import ClaudeModel
from .models.openai import OpenAIModel
from .models.qwen import QwenModel
from .models.local import LocalModel
from .architectures.unified_agent import UnifiedAgent
from .skills import create_default_skills, SkillExecutionContext
from .architectures.tools_enhanced import create_enhanced_tools

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
        return LocalModel(
            model_name=model_name or settings.local_model_name,
            base_url=settings.local_model_base_url
        )
    else:
        console.print(f"[red]错误: 不支持的提供商 '{provider}'[/red]")
        raise click.Abort()


@click.group(name="agent")
def agent_cli():
    """Agent 模式 - 支持 ReAct 和 Plan-Execute 架构"""
    pass


@agent_cli.command()
@click.argument("task")
@click.option("--mode", type=click.Choice(["react", "plan", "auto"]), default="auto", help="执行模式")
@click.option("--provider", default=None, help="AI 提供商")
@click.option("--model", default=None, help="模型名称")
@click.option("--context", "-c", help="额外上下文")
@click.option("--memory-dir", default=".aicode_memory", help="记忆存储目录")
def run(task, mode, provider, model, context, memory_dir):
    """使用 Agent 执行复杂任务"""
    async def execute():
        provider_name = provider or settings.default_provider

        # 根据 provider 选择正确的默认模型
        if model:
            model_name = model
        elif provider_name == "local":
            model_name = settings.local_model_name
        else:
            model_name = settings.default_model

        console.print(f"\n[cyan]Agent Mode:[/cyan] {mode.upper()}")
        console.print(f"[cyan]Using Model:[/cyan] {provider_name}/{model_name}")
        console.print(f"[cyan]Task:[/cyan] {task}\n")

        # 初始化 Agent
        model_instance = get_model(provider_name, model_name)
        agent = UnifiedAgent(
            model=model_instance,
            memory_dir=memory_dir,
            verbose=True,
        )

        # 执行任务
        result = await agent.run(task=task, mode=mode, context=context)

        # 显示结果
        if result.get("success"):
            console.print("\n[green]✓ Task completed successfully![/green]\n")
        else:
            console.print("\n[yellow]⚠ Task completed with issues[/yellow]\n")

        # 显示答案或摘要
        answer = result.get("answer") or result.get("summary")
        if answer:
            md = Markdown(answer)
            console.print(Panel(md, title="[green]Result[/green]", border_style="green"))

    asyncio.run(execute())


@agent_cli.command()
@click.option("--provider", default=None, help="AI 提供商")
@click.option("--model", default=None, help="模型名称")
@click.option("--memory-dir", default=".aicode_memory", help="记忆存储目录")
def interactive(provider, model, memory_dir):
    """交互式 Agent 会话"""
    async def session():
        provider_name = provider or settings.default_provider

        # 根据 provider 选择正确的默认模型
        if model:
            model_name = model
        elif provider_name == "local":
            model_name = settings.local_model_name
        else:
            model_name = settings.default_model

        console.print("[cyan]Starting Interactive Agent Session[/cyan]")
        console.print(f"[cyan]Model:[/cyan] {provider_name}/{model_name}")
        console.print("[yellow]Type 'exit' to quit, 'memory' to view memory stats[/yellow]\n")

        model_instance = get_model(provider_name, model_name)
        agent = UnifiedAgent(
            model=model_instance,
            memory_dir=memory_dir,
            verbose=True,
        )

        while True:
            try:
                task = console.input("[bold green]You:[/bold green] ")

                if task.lower() in ["exit", "quit", "q"]:
                    console.print("[yellow]Goodbye![/yellow]")
                    break

                if task.lower() == "memory":
                    stats = agent.get_memory_stats()
                    console.print("\n[cyan]Memory Statistics:[/cyan]")
                    console.print(stats)
                    continue

                if task.lower() == "clear":
                    agent.clear_short_term_memory()
                    console.print("[yellow]Short-term memory cleared[/yellow]")
                    continue

                if not task.strip():
                    continue

                # 执行任务
                console.print()
                result = await agent.run(task=task, mode="auto")

                # 显示结果
                answer = result.get("answer") or result.get("summary")
                if answer:
                    console.print(f"\n[bold blue]Agent:[/bold blue] {answer}\n")

            except KeyboardInterrupt:
                console.print("\n[yellow]Session interrupted. Goodbye![/yellow]")
                break
            except Exception as e:
                console.print(f"\n[red]Error: {e}[/red]\n")

    asyncio.run(session())


@agent_cli.command()
@click.option("--memory-dir", default=".aicode_memory", help="记忆存储目录")
def memory_stats(memory_dir):
    """查看记忆统计"""
    from .memory.memory_manager import MemoryManager

    memory = MemoryManager(storage_dir=memory_dir)
    stats = memory.get_statistics()

    console.print("\n[bold cyan]Memory Statistics[/bold cyan]\n")

    # 短期记忆
    console.print("[cyan]Short-term Memory:[/cyan]")
    st = stats["short_term"]
    console.print(f"  Session: {st.get('session_id', 'N/A')}")
    console.print(f"  Total messages: {st.get('total_messages', 0)}")
    console.print(f"  Estimated tokens: {st.get('estimated_tokens', 0)}")

    # 长期记忆
    console.print("\n[cyan]Long-term Memory:[/cyan]")
    lt = stats["long_term"]
    console.print(f"  Total memories: {lt.get('total_memories', 0)}")
    console.print(f"  Categories: {lt.get('categories', {})}")
    console.print(f"  Total tags: {lt.get('total_tags', 0)}")

    console.print()


@agent_cli.command()
@click.argument("key")
@click.argument("value")
@click.option("--category", default="user_preferences", help="记忆分类")
@click.option("--importance", default=5, type=int, help="重要程度 (1-10)")
@click.option("--memory-dir", default=".aicode_memory", help="记忆存储目录")
def remember(key, value, category, importance, memory_dir):
    """保存信息到长期记忆"""
    from .memory.memory_manager import MemoryManager

    memory = MemoryManager(storage_dir=memory_dir)
    memory.remember(key, value, category=category, importance=importance)

    console.print(f"[green]✓ Remembered:[/green] {key} = {value}")
    console.print(f"[cyan]Category:[/cyan] {category}, [cyan]Importance:[/cyan] {importance}")


@agent_cli.command()
@click.argument("query")
@click.option("--category", help="搜索分类")
@click.option("--memory-dir", default=".aicode_memory", help="记忆存储目录")
def search(query, category, memory_dir):
    """搜索长期记忆"""
    from .memory.memory_manager import MemoryManager

    memory = MemoryManager(storage_dir=memory_dir)
    results = memory.search_memories(query=query, category=category)

    console.print(f"\n[cyan]Search results for:[/cyan] {query}\n")

    if not results:
        console.print("[yellow]No results found[/yellow]")
        return

    for i, result in enumerate(results[:10], 1):
        console.print(f"{i}. [bold]{result['key']}[/bold]")
        console.print(f"   Value: {result['value']}")
        console.print(f"   Category: {result['category']}, Importance: {result['importance']}")
        console.print()


@agent_cli.command()
@click.option("--memory-dir", default=".aicode_memory", help="记忆存储目录")
def list_tools(memory_dir):
    """列出所有可用工具"""
    # 创建临时 agent 实例
    from .models.claude import ClaudeModel
    from .architectures.unified_agent import UnifiedAgent

    if not settings.anthropic_api_key:
        console.print("[red]需要配置 API key 才能初始化 Agent[/red]")
        return

    model = ClaudeModel(api_key=settings.anthropic_api_key, model_name="claude-sonnet-4-6")
    agent = UnifiedAgent(model=model, memory_dir=memory_dir, verbose=False)

    tools = agent.list_tools()

    console.print("\n[bold cyan]Available Tools[/bold cyan]\n")

    for tool_name in tools:
        tool_info = agent.get_tool_info(tool_name)
        if tool_info:
            console.print(f"[green]•[/green] [bold]{tool_name}[/bold]")
            console.print(f"  {tool_info['description']}")
            console.print()


@agent_cli.command(name="skill-list")
@click.option("--category", help="按分类过滤技能")
def list_skills(category):
    """列出所有可用的技能"""
    skill_registry = create_default_skills()
    skills = skill_registry.list_skills(category=category)

    if not skills:
        console.print("[yellow]No skills found[/yellow]")
        return

    console.print(f"\n[bold cyan]Available Skills[/bold cyan] ({len(skills)})\n")

    # 按分类分组
    by_category = {}
    for skill in skills:
        if skill.category not in by_category:
            by_category[skill.category] = []
        by_category[skill.category].append(skill)

    # 显示技能
    for cat, cat_skills in sorted(by_category.items()):
        console.print(f"[bold yellow]{cat.upper()}[/bold yellow]")
        for skill in cat_skills:
            console.print(f"  [green]•[/green] [bold]{skill.name}[/bold]")
            console.print(f"    {skill.description}")
            console.print(f"    [dim]Required tools: {', '.join(skill.required_tools)}[/dim]")
            console.print()


@agent_cli.command(name="skill-run")
@click.argument("skill_name")
@click.option("--param", "-p", multiple=True, help="技能参数 (key=value)")
@click.option("--working-dir", default=".", help="工作目录")
def run_skill(skill_name, param, working_dir):
    """执行指定的技能"""
    async def execute():
        # 创建技能注册表和工具
        skill_registry = create_default_skills()
        tool_registry = create_enhanced_tools()

        # 解析参数
        params = {}
        for p in param:
            if "=" in p:
                key, value = p.split("=", 1)
                params[key] = value

        # 创建执行上下文
        context = SkillExecutionContext(
            tools={tool.name: tool.func for tool in tool_registry.tools.values()},
            working_dir=working_dir
        )

        console.print(f"\n[cyan]Executing skill:[/cyan] {skill_name}")
        console.print(f"[cyan]Parameters:[/cyan] {params}\n")

        # 执行技能
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Running {skill_name}...", total=None)

            result = await skill_registry.execute_skill(
                skill_name, context, **params
            )

            progress.stop()

        # 显示结果
        if result["success"]:
            console.print("[green]✓ Skill executed successfully![/green]\n")
        else:
            console.print("[red]✗ Skill execution failed[/red]\n")

        console.print(f"[bold]Message:[/bold] {result['message']}\n")

        if result["steps"]:
            console.print("[bold]Execution Steps:[/bold]")
            for step in result["steps"]:
                console.print(f"  • {step}")
            console.print()

        if result["data"]:
            console.print("[bold]Result Data:[/bold]")
            import json
            console.print(json.dumps(result["data"], indent=2))

    asyncio.run(execute())


@agent_cli.command(name="skill-stats")
def skill_stats():
    """显示技能使用统计"""
    skill_registry = create_default_skills()
    stats = skill_registry.get_all_stats()

    console.print(f"\n[bold cyan]Skill Statistics[/bold cyan]\n")
    console.print(f"Total skills: {stats['total_skills']}")
    console.print(f"Categories: {', '.join(stats['categories'])}\n")

    console.print("[bold]Individual Skill Stats:[/bold]\n")
    for skill_stat in stats['skills']:
        console.print(f"[bold]{skill_stat['name']}[/bold] ({skill_stat['category']})")
        console.print(f"  Executions: {skill_stat['execution_count']}")
        console.print(f"  Success rate: {skill_stat['success_rate']:.1%}")
        if skill_stat['last_executed_at']:
            console.print(f"  Last run: {skill_stat['last_executed_at']}")
        console.print()


if __name__ == "__main__":
    agent_cli()
