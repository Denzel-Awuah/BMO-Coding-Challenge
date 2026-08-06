import re
import uuid
from datetime import datetime
from .tools import TextProcessorTool, CalculatorTool, WeatherMockTool


class AgentController:
    def __init__(self):
        # register tools in order of preference
        self.tools = {
            "text": TextProcessorTool(),
            "calc": CalculatorTool(),
            "weather": WeatherMockTool(),
        }
        # retry policy configuration
        self.max_retries = 2

    def _execute_with_retries(self, tool, input_text, tool_steps):
        """Execute a tool with retry logic. Appends messages to tool_steps and returns output."""
        attempt = 0
        last_exc = None
        while attempt <= self.max_retries:
            try:
                tool_steps.append(f"Tool {tool.name}: attempt {attempt+1} executing on input: {input_text}")
                output = tool.execute(input_text, tool_steps)
                tool_steps.append(f"Tool {tool.name}: succeeded on attempt {attempt+1}")
                return output
            except Exception as e:
                last_exc = e
                tool_steps.append(f"Tool {tool.name}: failed on attempt {attempt+1} with error: {str(e)}")
                attempt += 1
        # exhausted retries
        raise last_exc

    def _plan_subtasks(self, task_text: str):
        """Very small planner: split on ' and then ', ' then ', or ' and ' to produce subtasks.
        This enables simple multi-step reasoning where users chain instructions.
        """
        parts = re.split(r"\band then\b|\bthen\b|\band\b", task_text, flags=re.IGNORECASE)
        parts = [p.strip() for p in parts if p.strip()]
        return parts if parts else [task_text]

    def handle(self, task_text: str) -> dict:
        steps = []
        steps.append(f"Step 1: Received input \"{task_text}\"")

        subtasks = self._plan_subtasks(task_text)
        tools_used = []
        overall_output = None

        step_counter = 1
        for idx, sub in enumerate(subtasks, start=1):
            step_counter += 1
            # Choose tool for this subtask
            tool_key = self.select_tool(sub)
            if not tool_key:
                steps.append(f"Step {step_counter}: No tool identified for subtask '{sub}'. Echoing.")
                overall_output = sub
                continue

            tool = self.tools[tool_key]
            tools_used.append(tool.name)
            steps.append(f"Step {step_counter}: Selected tool {tool.name} for subtask: '{sub}'")

            # Determine input for the tool: if subtask contains quoted text or numbers, pass it; otherwise, if previous output exists, pass that
            input_for_tool = sub
            if overall_output is not None and not re.search(r"\".*\"|\d+", sub):
                input_for_tool = overall_output
                steps.append(f"Step {step_counter+1}: Using previous output as input to next tool: '{input_for_tool}'")

            tool_steps = []
            try:
                output = self._execute_with_retries(tool, input_for_tool, tool_steps)
                # append tool steps into overall steps with numbering
                for s in tool_steps:
                    step_counter += 1
                    steps.append(f"Step {step_counter}: {s}")
                overall_output = output
            except Exception as e:
                step_counter += 1
                steps.append(f"Step {step_counter}: Tool {tool.name} failed after {self.max_retries+1} attempts: {str(e)}")
                overall_output = f"Error during tool execution: {str(e)}"
                # continue to next subtask (best-effort)

        step_counter += 1
        steps.append(f"Step {step_counter}: Returning final result to user")

        return {
            "id": str(uuid.uuid4()),
            "task": task_text,
            "output": overall_output,
            "steps": steps,
            "tools": tools_used,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    def handle_stream(self, task_text: str):
        """Generator that yields step events for streaming to clients.
        Each yielded value is a dict with keys: type ('step'|'result'), data.
        """
        # Start
        yield {"type": "step", "data": f"Received input: '{task_text}'"}
        subtasks = self._plan_subtasks(task_text)
        tools_used = []
        overall_output = None

        for idx, sub in enumerate(subtasks, start=1):
            yield {"type": "step", "data": f"Planning subtask {idx}: '{sub}'"}
            tool_key = self.select_tool(sub)
            if not tool_key:
                yield {"type": "step", "data": f"No tool identified for '{sub}', echoing."}
                overall_output = sub
                continue

            tool = self.tools[tool_key]
            tools_used.append(tool.name)
            yield {"type": "step", "data": f"Selected tool {tool.name} for subtask '{sub}'"}

            input_for_tool = sub
            if overall_output is not None and not re.search(r"\".*\"|\d+", sub):
                input_for_tool = overall_output
                yield {"type": "step", "data": f"Using previous output as input to next tool: '{input_for_tool}'"}

            tool_steps = []
            try:
                output = self._execute_with_retries(tool, input_for_tool, tool_steps)
                for s in tool_steps:
                    yield {"type": "step", "data": s}
                overall_output = output
                yield {"type": "step", "data": f"Tool {tool.name} returned: {repr(output)}"}
            except Exception as e:
                yield {"type": "step", "data": f"Tool {tool.name} failed: {str(e)}"}
                overall_output = f"Error during tool execution: {str(e)}"
                # continue

        yield {"type": "result", "data": {"id": str(uuid.uuid4()), "task": task_text, "output": overall_output, "steps": [], "tools": tools_used, "timestamp": datetime.utcnow().isoformat() + "Z"}}

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
