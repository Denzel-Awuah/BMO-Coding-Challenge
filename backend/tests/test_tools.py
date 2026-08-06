import pytest
from tools import TextProcessorTool, CalculatorTool, WeatherMockTool


def test_textprocessor_uppercase():
    tool = TextProcessorTool()
    steps = []
    res = tool.execute('Convert "hello world" to uppercase', steps)
    assert 'HELLO WORLD' in res
    assert any('uppercase' in s.lower() or 'converting to uppercase' in s.lower() for s in steps)


def test_textprocessor_wordcount():
    tool = TextProcessorTool()
    steps = []
    res = tool.execute('Give me the word count for "one two three"', steps)
    assert '3' in res
    assert 'word count' in res.lower()


def test_calculator_simple():
    tool = CalculatorTool()
    steps = []
    res = tool.execute('Calculate 3+5', steps)
    assert '8' in res
    assert 'result' in res.lower()


def test_calculator_with_x_symbol():
    tool = CalculatorTool()
    steps = []
    res = tool.execute('What is 5 x 10 / 2', steps)
    assert '25' in res
    assert 'result' in res.lower()


def test_calculator_invalid():
    tool = CalculatorTool()
    steps = []
    with pytest.raises(ValueError):
        tool._safe_eval('import os; os.system("echo hi")')


def test_weather_extract_city():
    tool = WeatherMockTool()
    steps = []
    res = tool.execute('What is the weather in Brampton, Ontario?', steps)
    assert 'Brampton' in res or 'brampton' in res


def test_weather_unknown():
    tool = WeatherMockTool()
    steps = []
    res = tool.execute('', steps)
    assert 'not available' in res.lower() or 'unknown' in res.lower()
