"""Plan-Execute Agent - 先规划后执行模式"""

import json
from typing import Optional, Dict, Any, List
from ..models.base import AIModel
from ..memory.memory_manager import MemoryManager
from .tools import ToolRegistry


class Plan:
    """执行计划"""

    def __init__(self, steps: List[Dict[str, Any]], description: str = ""):
        self.steps = steps
        self.description = description
        self.current_step = 0

    def get_next_step(self) -> Optional[Dict[str, Any]]:
        """获取下一步"""
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            self.current_step += 1
            return step
        return None

    def is_complete(self) -> bool:
        """是否完成"""
        return self.current_step >= len(self.steps)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "description": self.description,
            "total_steps": len(self.steps),
            "current_step": self.current_step,
            "steps": self.steps,
        }


class PlanExecuteAgent:
    """
    Plan-Execute Agent

    执行流程：
    1. Planning: 根据任务制定完整执行计划
    2. Execution: 按步骤执行计划
    3. Replanning: 如果需要，根据执行结果调整计划
    """

    def __init__(
        self,
        model: AIModel,
        tool_registry: ToolRegistry,
        memory_manager: Optional[MemoryManager] = None,
        allow_replan: bool = True,
        max_replans: int = 2,
        verbose: bool = True,
    ):
        self.model = model
        self.tools = tool_registry
        self.memory = memory_manager or MemoryManager()
        self.allow_replan = allow_replan
        self.max_replans = max_replans
        self.verbose = verbose

    async def run(self, task: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        执行任务

        Args:
            task: 任务描述
            context: 额外上下文

        Returns:
            执行结果
        """
        # 添加任务到短期记忆
        self.memory.add_message("user", task)

        # 获取记忆上下文
        memory_context = self.memory.get_full_context(include_long_term=True)

        # Phase 1: Planning
        if self.verbose:
            print("\n=== Phase 1: Planning ===")

        plan = await self._create_plan(task, context, memory_context)

        if self.verbose:
            print(f"\nPlan created with {len(plan.steps)} steps:")
            for i, step in enumerate(plan.steps, 1):
                print(f"  {i}. {step.get('description', 'No description')}")

        # Phase 2: Execution
        if self.verbose:
            print("\n=== Phase 2: Execution ===")

        execution_results = []
        replan_count = 0

        while not plan.is_complete():
            step = plan.get_next_step()
            if not step:
                break

            if self.verbose:
                print(f"\n--- Executing Step {plan.current_step}/{len(plan.steps)} ---")
                print(f"Description: {step.get('description', 'N/A')}")

            # 执行步骤
            result = await self._execute_step(step)
            execution_results.append(result)

            if self.verbose:
                print(f"Result: {'Success' if result['success'] else 'Failed'}")
                if not result['success']:
                    print(f"Error: {result.get('error', 'Unknown error')}")

            # 检查是否需要重新规划
            if not result['success'] and self.allow_replan and replan_count < self.max_replans:
                if self.verbose:
                    print(f"\n=== Replanning (attempt {replan_count + 1}/{self.max_replans}) ===")

                # 重新规划
                remaining_task = self._get_remaining_task(task, execution_results)
                plan = await self._create_plan(
                    remaining_task,
                    context,
                    memory_context,
                    previous_results=execution_results
                )
                replan_count += 1

        # Phase 3: Summarize
        if self.verbose:
            print("\n=== Phase 3: Summarizing ===")

        summary = await self._summarize_results(task, execution_results)

        # 添加到记忆
        self.memory.add_message("assistant", summary, metadata={"mode": "plan-execute"})

        return {
            "success": all(r['success'] for r in execution_results),
            "summary": summary,
            "plan": plan.to_dict(),
            "execution_results": execution_results,
            "replan_count": replan_count,
        }

    async def _create_plan(
        self,
        task: str,
        context: Optional[str],
        memory_context: str,
        previous_results: Optional[List[Dict]] = None,
    ) -> Plan:
        """创建执行计划"""
        tools_desc = self.tools.get_tools_description()

        system_prompt = f"""You are a planning agent. Create a detailed step-by-step plan to accomplish the given task.

{tools_desc}

Return your plan in JSON format:
{{
  "description": "Brief description of the overall plan",
  "steps": [
    {{
      "step_number": 1,
      "description": "What this step does",
      "action": "tool_name",
      "action_input": {{"param": "value"}},
      "expected_output": "What we expect to get"
    }},
    ...
  ]
}}

Guidelines:
1. Break complex tasks into simple, sequential steps
2. Each step should use ONE tool
3. Consider dependencies between steps
4. Be specific about tool parameters
5. Plan for error handling
"""

        prompt_parts = []

        if memory_context:
            prompt_parts.append(f"=== Context from Memory ===\n{memory_context}\n")

        if context:
            prompt_parts.append(f"=== Additional Context ===\n{context}\n")

        prompt_parts.append(f"=== Task ===\n{task}\n")

        if previous_results:
            prompt_parts.append("\n=== Previous Execution Results ===")
            for i, result in enumerate(previous_results, 1):
                status = "✓" if result['success'] else "✗"
                prompt_parts.append(f"{i}. [{status}] {result.get('step_description', 'N/A')}")
                if not result['success']:
                    prompt_parts.append(f"   Error: {result.get('error', 'Unknown')}")
            prompt_parts.append("\nCreate a NEW plan considering these results.")

        prompt_parts.append("\n\nCreate a detailed execution plan:")

        prompt = "\n".join(prompt_parts)

        response = await self.model.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=2000,
            temperature=0.5,
        )

        # 解析计划
        plan_data = self._parse_plan(response)
        return Plan(
            steps=plan_data.get("steps", []),
            description=plan_data.get("description", "")
        )

    async def _execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个步骤"""
        result = {
            "step_number": step.get("step_number", 0),
            "step_description": step.get("description", ""),
            "action": step.get("action", ""),
            "success": False,
            "output": None,
            "error": None,
        }

        try:
            action = step.get("action")
            action_input = step.get("action_input", {})

            if not action:
                result["error"] = "No action specified"
                return result

            # 执行工具
            output = self.tools.execute_tool(action, **action_input)
            result["output"] = str(output)
            result["success"] = True

            # 添加到记忆
            self.memory.add_message(
                "tool",
                result["output"],
                metadata={"tool_name": action, "step": step.get("step_number")}
            )

        except Exception as e:
            result["error"] = str(e)

        return result

    async def _summarize_results(
        self,
        task: str,
        execution_results: List[Dict[str, Any]]
    ) -> str:
        """总结执行结果"""
        system_prompt = """You are a summarization agent. Summarize the execution results of a plan.

Provide:
1. Whether the task was completed successfully
2. What was accomplished
3. Any issues encountered
4. Key outputs or findings

Be concise but informative."""

        prompt_parts = [
            f"=== Original Task ===\n{task}\n",
            "\n=== Execution Results ===",
        ]

        for result in execution_results:
            status = "✓ Success" if result['success'] else "✗ Failed"
            prompt_parts.append(f"\nStep {result['step_number']}: {result['step_description']}")
            prompt_parts.append(f"Status: {status}")
            if result['success']:
                output_preview = str(result['output'])[:200]
                prompt_parts.append(f"Output: {output_preview}...")
            else:
                prompt_parts.append(f"Error: {result.get('error', 'Unknown')}")

        prompt_parts.append("\n\nProvide a comprehensive summary:")

        prompt = "\n".join(prompt_parts)

        summary = await self.model.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1000,
            temperature=0.5,
        )

        return summary

    def _parse_plan(self, response: str) -> Dict[str, Any]:
        """解析计划响应"""
        # 尝试提取 JSON
        import re

        # 查找 JSON 代码块
        json_match = re.search(r"```json\s*(\{.+?\})\s*```", response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass

        # 直接尝试解析
        try:
            return json.loads(response)
        except:
            pass

        # 查找任何 JSON 对象
        json_match = re.search(r"\{.+\}", response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass

        # 失败时返回空计划
        return {
            "description": "Failed to parse plan",
            "steps": []
        }

    def _get_remaining_task(
        self,
        original_task: str,
        execution_results: List[Dict[str, Any]]
    ) -> str:
        """根据执行结果确定剩余任务"""
        completed = [r for r in execution_results if r['success']]
        failed = [r for r in execution_results if not r['success']]

        parts = [f"Original task: {original_task}\n"]

        if completed:
            parts.append(f"\nCompleted steps ({len(completed)}):")
            for r in completed:
                parts.append(f"- {r['step_description']}")

        if failed:
            parts.append(f"\nFailed steps ({len(failed)}):")
            for r in failed:
                parts.append(f"- {r['step_description']}: {r.get('error', 'Unknown error')}")

        parts.append("\nComplete the remaining task, addressing any failed steps.")

        return "\n".join(parts)

    def get_execution_summary(self, result: Dict[str, Any]) -> str:
        """获取执行摘要"""
        lines = [
            "=== Plan-Execute Agent Execution Summary ===\n",
            f"Success: {result['success']}",
            f"Total Steps: {result['plan']['total_steps']}",
            f"Replanning Count: {result['replan_count']}\n",
            f"Summary:\n{result['summary']}\n",
        ]

        if result.get("execution_results"):
            lines.append("\n=== Step Results ===")
            for r in result["execution_results"]:
                status = "✓" if r['success'] else "✗"
                lines.append(f"{status} Step {r['step_number']}: {r['step_description']}")

        return "\n".join(lines)
