"""ReAct Agent - Reasoning and Acting 循环模式"""

import re
import json
from typing import Optional, Dict, Any, List
from ..models.base import AIModel
from ..memory.memory_manager import MemoryManager
from .tools import ToolRegistry


class ReActAgent:
    """
    ReAct (Reasoning + Acting) Agent

    循环执行：
    1. Thought: 思考当前状态和下一步行动
    2. Action: 选择并执行一个工具
    3. Observation: 观察工具执行结果
    4. 重复直到达成目标
    """

    def __init__(
        self,
        model: AIModel,
        tool_registry: ToolRegistry,
        memory_manager: Optional[MemoryManager] = None,
        max_iterations: int = 10,
        verbose: bool = True,
    ):
        self.model = model
        self.tools = tool_registry
        self.memory = memory_manager or MemoryManager()
        self.max_iterations = max_iterations
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

        # 构建初始提示词
        system_prompt = self._build_system_prompt()

        # 获取记忆上下文
        memory_context = self.memory.get_full_context(include_long_term=True)

        trajectory = []  # 记录执行轨迹
        final_answer = None

        for iteration in range(self.max_iterations):
            if self.verbose:
                print(f"\n=== Iteration {iteration + 1}/{self.max_iterations} ===")

            # 构建当前提示词
            prompt = self._build_prompt(task, trajectory, context, memory_context)

            # 调用模型
            response = await self.model.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=2000,
                temperature=0.7,
            )

            if self.verbose:
                print(f"\nAgent Response:\n{response}")

            # 解析响应
            parsed = self._parse_response(response)

            # 记录轨迹
            step = {
                "iteration": iteration + 1,
                "thought": parsed.get("thought", ""),
                "action": parsed.get("action", ""),
                "action_input": parsed.get("action_input", {}),
                "observation": "",
            }

            # 检查是否完成
            if parsed.get("final_answer"):
                final_answer = parsed["final_answer"]
                step["final_answer"] = final_answer
                trajectory.append(step)
                break

            # 执行动作
            if parsed.get("action"):
                try:
                    result = self.tools.execute_tool(
                        parsed["action"],
                        **parsed.get("action_input", {})
                    )
                    observation = str(result)
                except Exception as e:
                    observation = f"Error: {str(e)}"

                step["observation"] = observation
                trajectory.append(step)

                if self.verbose:
                    print(f"\nObservation:\n{observation[:500]}...")

                # 添加到记忆
                self.memory.add_message(
                    "tool",
                    observation,
                    metadata={"tool_name": parsed["action"]}
                )
            else:
                # 没有动作，可能需要更多思考
                trajectory.append(step)

        # 如果没有最终答案，使用最后的观察
        if not final_answer and trajectory:
            last_step = trajectory[-1]
            final_answer = last_step.get("observation", "Task completed but no final answer provided.")

        # 添加最终答案到记忆
        self.memory.add_message("assistant", final_answer or "No answer", metadata={"mode": "react"})

        return {
            "success": final_answer is not None,
            "answer": final_answer,
            "trajectory": trajectory,
            "iterations": len(trajectory),
        }

    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        tools_desc = self.tools.get_tools_description()

        return f"""You are a ReAct (Reasoning + Acting) coding agent. You solve coding tasks by iteratively thinking and using tools.

{tools_desc}

Use this format for EVERY response:

Thought: [Your reasoning about what to do next]
Action: [tool_name]
Action Input: {{"param1": "value1", "param2": "value2"}}

After receiving the observation, continue thinking and acting until you can provide a final answer:

Thought: [Your final reasoning]
Final Answer: [Your complete answer to the task]

Guidelines:
1. Think step-by-step before each action
2. Use tools to gather information and perform operations
3. Break complex tasks into smaller steps
4. If a tool fails, try an alternative approach
5. Always provide a clear Final Answer when done
6. Be specific and precise in your actions
"""

    def _build_prompt(
        self,
        task: str,
        trajectory: List[Dict],
        context: Optional[str],
        memory_context: str,
    ) -> str:
        """构建当前提示词"""
        parts = []

        # 记忆上下文
        if memory_context:
            parts.append(f"=== Context from Memory ===\n{memory_context}\n")

        # 额外上下文
        if context:
            parts.append(f"=== Additional Context ===\n{context}\n")

        # 任务
        parts.append(f"=== Task ===\n{task}\n")

        # 执行轨迹
        if trajectory:
            parts.append("\n=== Previous Steps ===")
            for step in trajectory:
                if step.get("thought"):
                    parts.append(f"\nThought: {step['thought']}")
                if step.get("action"):
                    parts.append(f"Action: {step['action']}")
                    parts.append(f"Action Input: {json.dumps(step['action_input'])}")
                if step.get("observation"):
                    parts.append(f"Observation: {step['observation'][:500]}")

        parts.append("\n\nNow continue with your next Thought and Action:")

        return "\n".join(parts)

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        解析模型响应

        期望格式:
        Thought: ...
        Action: tool_name
        Action Input: {"param": "value"}

        或:
        Thought: ...
        Final Answer: ...
        """
        result = {}

        # 提取 Thought
        thought_match = re.search(r"Thought:\s*(.+?)(?=\n(?:Action|Final Answer)|\Z)", response, re.DOTALL)
        if thought_match:
            result["thought"] = thought_match.group(1).strip()

        # 检查是否有 Final Answer
        final_match = re.search(r"Final Answer:\s*(.+)", response, re.DOTALL)
        if final_match:
            result["final_answer"] = final_match.group(1).strip()
            return result

        # 提取 Action
        action_match = re.search(r"Action:\s*(\w+)", response)
        if action_match:
            result["action"] = action_match.group(1).strip()

        # 提取 Action Input
        action_input_match = re.search(r"Action Input:\s*(\{.+?\})", response, re.DOTALL)
        if action_input_match:
            try:
                result["action_input"] = json.loads(action_input_match.group(1))
            except json.JSONDecodeError:
                # 尝试修复常见的 JSON 错误
                input_str = action_input_match.group(1)
                input_str = input_str.replace("'", '"')
                try:
                    result["action_input"] = json.loads(input_str)
                except:
                    result["action_input"] = {}

        return result

    def get_execution_summary(self, result: Dict[str, Any]) -> str:
        """获取执行摘要"""
        lines = [
            "=== ReAct Agent Execution Summary ===\n",
            f"Success: {result['success']}",
            f"Iterations: {result['iterations']}/{self.max_iterations}",
            f"\nFinal Answer:\n{result['answer']}\n",
        ]

        if result.get("trajectory"):
            lines.append("\n=== Execution Trajectory ===")
            for step in result["trajectory"]:
                lines.append(f"\nStep {step['iteration']}:")
                if step.get("thought"):
                    lines.append(f"  Thought: {step['thought'][:100]}...")
                if step.get("action"):
                    lines.append(f"  Action: {step['action']}")
                if step.get("observation"):
                    lines.append(f"  Observation: {step['observation'][:100]}...")

        return "\n".join(lines)
