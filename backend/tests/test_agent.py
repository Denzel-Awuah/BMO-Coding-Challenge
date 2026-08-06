from agent import AgentController


def test_select_tool_weather():
    a = AgentController()
    assert a.select_tool('What is the weather in Toronto?') == 'weather'


def test_select_tool_calc():
    a = AgentController()
    assert a.select_tool('Calculate 2 + 2') == 'calc'


def test_select_tool_text():
    a = AgentController()
    assert a.select_tool('Make "hello" uppercase') == 'text'


def test_handle_returns_structure():
    a = AgentController()
    res = a.handle('Calculate 1+1')
    assert 'id' in res and 'output' in res and 'steps' in res and 'timestamp' in res
    assert res['tools'] == ['CalculatorTool']
