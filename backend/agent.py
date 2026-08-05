import re
import uuid
from datetime import datetime
from tools import TextProcessorTool, CalculatorTool, WeatherMockTool


class AgentController:
    def __init__(self):
        # register tools in order of preference
        self.tools = {
            "text": TextProcessorTool(),
            "calc": CalculatorTool(),
            "weather": WeatherMockTool(),
        }

    def handle(self, task_text: str) -> dict:
        steps = []
        steps.append(f"Step 1: Received input \"{task_text}\"")

        tool_key = self.select_tool(task_text)
        if not tool_key:
            steps.append("Step 2: No suitable tool found. Returning echo.")
            output = task_text
            tools_used = []
        else:
            tool = self.tools[tool_key]
            steps.append(f"Step 2: Selected tool: {tool.name}")
            # tool execution can itself append sub-steps
            tool_steps = []
            try:
                output = tool.execute(task_text, tool_steps)
                steps.extend([f"Step {len(steps)+i}: {s}" for i, s in enumerate(tool_steps, start=1)])
                tools_used = [tool.name]
            except Exception as e:
                steps.append(f"Step {len(steps)+1}: Tool execution failed: {str(e)}")
                output = f"Error during tool execution: {str(e)}"
                tools_used = [tool.name]

        steps.append(f"Step {len(steps)+1}: Returning result to user")

        return {
            "id": str(uuid.uuid4()),
            "task": task_text,
            "output": output,
            "steps": steps,
            "tools": tools_used,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    def select_tool(self, task_text: str):
        text = task_text.lower()
        # Weather detection first: explicit keywords that indicate weather intent
        if any(k in text for k in ["weather", "forecast", "temperature"]):
            return "weather"
        # Calculator detection: require explicit calculate/evaluate keywords or numeric expressions/operators
        if re.search(r"\b(calculate|evaluate)\b", text) or re.search(r"\bwhat(?:'s| is)\s+[-+]?\d", text) or re.search(r"[0-9]+\s*[-+/*^%()]", text):
            return "calc"
        # text processing detection
        if any(k in text for k in ["uppercase", "lowercase", "word count", "count words", "reverse", "title case", "capitalize"]):
            return "text"
        # fallback: try text tool for general text processing commands
        if len(task_text.strip()) > 0:
            return "text"
        return None
