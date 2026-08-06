import pytest
from tools import TextProcessorTool, CalculatorTool, WeatherMockTool


def test_textprocessor_uppercase():
    tool = TextProcessorTool()
    steps = []
    res = tool.execute('Convert "hello world" to uppercase', steps)
    assert res == 'HELLO WORLD'
    assert any('uppercase' in s.lower() or 'converting to uppercase' in s.lower() for s in steps)


def test_textprocessor_wordcount():
    tool = TextProcessorTool()
    steps = []
    res = tool.execute('Give me the word count for "one two three"', steps)
    assert res == '3'


def test_calculator_simple():
    tool = CalculatorTool()
    steps = []
    res = tool.execute('Calculate 3+5', steps)
    assert res == '8'


def test_calculator_with_x_symbol():
    tool = CalculatorTool()
    steps = []
    res = tool.execute('What is 5 x 10 / 2', steps)
    # result may be float string or int string depending on eval
    assert float(res) == 25.0


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
