"""Unit tests for multi-step / multi-tool agent reasoning."""
import pytest
from agent import AgentController


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_agent():
    return AgentController()


# ---------------------------------------------------------------------------
# Planner: sentence splitting
# ---------------------------------------------------------------------------

class TestPlanner:
    def test_single_sentence_returns_one_subtask(self):
        a = make_agent()
        parts = a._plan_subtasks("What is the weather in Toronto?")
        assert len(parts) == 1

    def test_also_splits_into_two_subtasks(self):
        a = make_agent()
        parts = a._plan_subtasks(
            'What is the weather in Toronto? Also, calculate 2+2'
        )
        assert len(parts) == 2

    def test_question_mark_splits_into_two_subtasks(self):
        a = make_agent()
        parts = a._plan_subtasks(
            'Calculate 5*5. What is the weather in Vancouver?'
        )
        assert len(parts) == 2

    def test_additionally_splits_into_two_subtasks(self):
        a = make_agent()
        parts = a._plan_subtasks(
            'Reverse "hello". Additionally, convert "world" to uppercase'
        )
        assert len(parts) == 2

    def test_three_part_query_splits_into_three_subtasks(self):
        a = make_agent()
        parts = a._plan_subtasks(
            'Calculate 3+3. Also, what is the weather in London? '
            'Also, reverse "bmo"'
        )
        assert len(parts) == 3


# ---------------------------------------------------------------------------
# Multi-tool handle: two different tools invoked
# ---------------------------------------------------------------------------

class TestMultiToolHandle:

    def test_weather_and_word_count_uses_both_tools(self):
        a = make_agent()
        res = a.handle(
            'What is the weather in Toronto? Also, '
            'what is the word count of this sentence "hello world"'
        )
        assert 'WeatherMockTool' in res['tools']
        assert 'TextProcessorTool' in res['tools']
        assert len(res['tools']) == 2

    def test_calculator_and_weather_uses_both_tools(self):
        a = make_agent()
        res = a.handle(
            'Calculate 10 * 5. Also, what is the weather in Vancouver?'
        )
        assert 'CalculatorTool' in res['tools']
        assert 'WeatherMockTool' in res['tools']
        assert len(res['tools']) == 2

    def test_reverse_and_calculator_uses_both_tools(self):
        a = make_agent()
        res = a.handle(
            'Reverse "bmo". Also, calculate 4^2'
        )
        assert 'TextProcessorTool' in res['tools']
        assert 'CalculatorTool' in res['tools']
        assert len(res['tools']) == 2

    def test_output_contains_result_from_each_tool(self):
        a = make_agent()
        res = a.handle(
            'What is the weather in London? Also, calculate 3+3'
        )
        # Weather result somewhere in output
        assert 'London' in res['output']
        # Calculator result somewhere in output
        assert '6' in res['output']

    def test_multi_tool_output_is_newline_separated(self):
        a = make_agent()
        res = a.handle(
            'What is the weather in Toronto? Also, calculate 2+2'
        )
        # Two results should be separated by a blank line
        assert '\n\n' in res['output']

    def test_multi_tool_steps_reference_multiple_tools(self):
        a = make_agent()
        res = a.handle(
            'Calculate 5+5. Also, what is the weather in Hamilton?'
        )
        steps_text = ' '.join(res['steps'])
        assert 'CalculatorTool' in steps_text
        assert 'WeatherMockTool' in steps_text

    def test_tools_list_deduplicates_same_tool_used_twice(self):
        """Both subtasks route to TextProcessorTool — it should appear only once."""
        a = make_agent()
        res = a.handle(
            'Reverse "agent". Also, convert "bmo" to uppercase'
        )
        assert res['tools'].count('TextProcessorTool') == 1

    def test_result_structure_is_valid_for_multi_tool(self):
        a = make_agent()
        res = a.handle(
            'What is the weather in Vancouver? Also, calculate 7*6'
        )
        assert 'id' in res
        assert 'task' in res
        assert 'output' in res
        assert 'steps' in res
        assert 'tools' in res
        assert 'timestamp' in res
        assert isinstance(res['steps'], list)
        assert isinstance(res['tools'], list)


# ---------------------------------------------------------------------------
# Multi-tool streaming: both tool results appear in the event stream
# ---------------------------------------------------------------------------

class TestMultiToolStream:

    def _collect(self, query):
        a = make_agent()
        step_events = []
        result_event = None
        for evt in a.handle_stream(query):
            if evt['type'] == 'step':
                step_events.append(evt['data'])
            elif evt['type'] == 'result':
                result_event = evt['data']
        return step_events, result_event

    def test_stream_emits_steps_for_each_subtask(self):
        steps, _ = self._collect(
            'What is the weather in Toronto? Also, calculate 2+2'
        )
        combined = ' '.join(steps)
        assert 'subtask 1' in combined.lower()
        assert 'subtask 2' in combined.lower()

    def test_stream_result_contains_both_tool_outputs(self):
        _, result = self._collect(
            'What is the weather in Toronto? Also, calculate 2+2'
        )
        assert result is not None
        assert 'Toronto' in result['output']
        assert '4' in result['output']

    def test_stream_result_lists_both_tools(self):
        _, result = self._collect(
            'Reverse "hello". Also, what is the weather in London?'
        )
        assert 'TextProcessorTool' in result['tools']
        assert 'WeatherMockTool' in result['tools']

    def test_stream_emits_at_least_one_step_event_per_subtask(self):
        steps, _ = self._collect(
            'Calculate 1+1. Also, convert "bmo" to uppercase'
        )
        # Expect at minimum: received input + planner + 2× subtask processing steps
        assert len(steps) >= 4
