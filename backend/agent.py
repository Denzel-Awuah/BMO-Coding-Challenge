import re
import uuid
from datetime import datetime

try:
    from .tools import TextProcessorTool, CalculatorTool, WeatherMockTool
except Exception:
    from tools import TextProcessorTool, CalculatorTool, WeatherMockTool


# Sentence-boundary and coordination patterns that separate independent requests
_SPLIT_PATTERN = re.compile(
    r'(?<=[.?!])\s+'                   # after sentence-ending punctuation + whitespace
    r'|(?:\s*\?\s+)'                   # standalone question mark + whitespace
    r'|\b(?:also|additionally|furthermore|next|and also)\b\s*[,]?\s*',
    re.IGNORECASE
)


class AgentController:
    def __init__(self):
        self.tools = {
            "text":    TextProcessorTool(),
            "calc":    CalculatorTool(),
            "weather": WeatherMockTool(),
        }
        self.max_retries = 2

    # ------------------------------------------------------------------
    # Planner
    # ------------------------------------------------------------------

    def _plan_subtasks(self, task_text: str):
        """Split a user message into independent sub-requests.

        Strategy:
        1. Split on sentence boundaries (. ? !) and coordination phrases
           (Also, Additionally, …).
        2. Keep only non-empty fragments.
        3. Each fragment is treated as an independent sub-request with its
           own tool selection and its own input — outputs are never piped
           from one subtask into the next.
        """
        parts = _SPLIT_PATTERN.split(task_text)
        parts = [p.strip().rstrip('?.! ') for p in parts if p.strip()]
        return parts if parts else [task_text]

    # ------------------------------------------------------------------
    # Tool execution with retry
    # ------------------------------------------------------------------

    def _execute_with_retries(self, tool, input_text, tool_steps):
        """Run tool.execute with up to max_retries retries on exception."""
        last_exc = None
        for attempt in range(self.max_retries + 1):
            try:
                tool_steps.append(
                    f"Tool {tool.name}: attempt {attempt + 1} — executing on: \"{input_text}\""
                )
                output = tool.execute(input_text, tool_steps)
                tool_steps.append(f"Tool {tool.name}: succeeded on attempt {attempt + 1}")
                return output
            except Exception as exc:
                last_exc = exc
                tool_steps.append(
                    f"Tool {tool.name}: failed on attempt {attempt + 1} — {exc}"
                )
        raise last_exc

    # ------------------------------------------------------------------
    # Non-streaming handle
    # ------------------------------------------------------------------

    def handle(self, task_text: str) -> dict:
        steps = []
        step = 1
        steps.append(f"Step {step}: Received input \"{task_text}\"")

        subtasks = self._plan_subtasks(task_text)
        step += 1
        steps.append(
            f"Step {step}: Planner identified {len(subtasks)} subtask(s): "
            + " | ".join(f'"{s}"' for s in subtasks)
        )

        tools_used = []
        outputs = []

        for idx, sub in enumerate(subtasks, start=1):
            step += 1
            steps.append(f"Step {step}: Processing subtask {idx}: \"{sub}\"")

            tool_key = self.select_tool(sub)
            if not tool_key:
                step += 1
                steps.append(f"Step {step}: No tool matched for subtask {idx} — echoing input.")
                outputs.append(sub)
                continue

            tool = self.tools[tool_key]
            if tool.name not in tools_used:
                tools_used.append(tool.name)
            step += 1
            steps.append(f"Step {step}: Selected tool {tool.name} for subtask {idx}")

            tool_steps = []
            try:
                output = self._execute_with_retries(tool, sub, tool_steps)
                for s in tool_steps:
                    step += 1
                    steps.append(f"Step {step}: {s}")
                outputs.append(output)
            except Exception as exc:
                step += 1
                steps.append(
                    f"Step {step}: Tool {tool.name} failed after {self.max_retries + 1} "
                    f"attempts: {exc}"
                )
                outputs.append(f"[Error in {tool.name}: {exc}]")

        final_output = "  ".join(outputs) if outputs else ""
        step += 1
        steps.append(f"Step {step}: Composed final answer from {len(outputs)} result(s)")
        step += 1
        steps.append(f"Step {step}: Returning result to user")

        return {
            "id":        str(uuid.uuid4()),
            "task":      task_text,
            "output":    final_output,
            "steps":     steps,
            "tools":     tools_used,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    # ------------------------------------------------------------------
    # Streaming handle
    # ------------------------------------------------------------------

    def handle_stream(self, task_text: str):
        """Yield step/result events for real-time streaming."""
        yield {"type": "step", "data": f"Received input: \"{task_text}\""}

        subtasks = self._plan_subtasks(task_text)
        yield {
            "type": "step",
            "data": (
                f"Planner identified {len(subtasks)} subtask(s): "
                + " | ".join(f'"{s}"' for s in subtasks)
            ),
        }

        tools_used = []
        outputs = []

        for idx, sub in enumerate(subtasks, start=1):
            yield {"type": "step", "data": f"Processing subtask {idx}: \"{sub}\""}

            tool_key = self.select_tool(sub)
            if not tool_key:
                yield {"type": "step", "data": f"No tool matched for subtask {idx} — echoing input."}
                outputs.append(sub)
                continue

            tool = self.tools[tool_key]
            if tool.name not in tools_used:
                tools_used.append(tool.name)
            yield {"type": "step", "data": f"Selected tool {tool.name} for subtask {idx}"}

            tool_steps = []
            try:
                output = self._execute_with_retries(tool, sub, tool_steps)
                for s in tool_steps:
                    yield {"type": "step", "data": s}
                outputs.append(output)
                yield {"type": "step", "data": f"Tool {tool.name} result: \"{output}\""}
            except Exception as exc:
                yield {"type": "step", "data": f"Tool {tool.name} failed after {self.max_retries + 1} attempts: {exc}"}
                outputs.append(f"[Error in {tool.name}: {exc}]")

        final_output = "  ".join(outputs) if outputs else ""
        yield {"type": "step", "data": f"Composed final answer from {len(outputs)} result(s)"}
        yield {
            "type": "result",
            "data": {
                "id":        str(uuid.uuid4()),
                "task":      task_text,
                "output":    final_output,
                "steps":     [],
                "tools":     tools_used,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
        }

    # ------------------------------------------------------------------
    # Tool selector
    # ------------------------------------------------------------------

    def select_tool(self, task_text: str):
        text = task_text.lower()
        if any(k in text for k in ["weather", "forecast", "temperature"]):
            return "weather"
        if (
            re.search(r"\b(calculate|evaluate)\b", text)
            or re.search(r"\bwhat(?:'s| is)\s+[-+]?\d", text)
            or re.search(r"[0-9]+\s*[-+/*^%()]", text)
        ):
            return "calc"
        if any(k in text for k in [
            "uppercase", "lowercase", "word count", "count words",
            "reverse", "title case", "capitalize",
        ]):
            return "text"
        if len(task_text.strip()) > 0:
            return "text"
        return None
