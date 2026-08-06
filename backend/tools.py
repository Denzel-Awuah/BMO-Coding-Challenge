import re
import ast


class TextProcessorTool:
    name = "TextProcessorTool"

    def execute(self, task_text: str, steps: list):
        steps.append(f"Parsing for text operation in: \"{task_text}\"")
        text = task_text.strip()
        lowered = text.lower()

        # determine operation
        if "uppercase" in lowered or "to upper" in lowered:
            target = self._extract_between_quotes(text) or self._extract_after_keyword(text, "uppercase") or text
            result = target.upper()
            steps.append(f"TextProcessor: converting to uppercase -> {result}")
            return result

        if "lowercase" in lowered or "to lower" in lowered:
            target = self._extract_between_quotes(text) or self._extract_after_keyword(text, "lowercase") or text
            result = target.lower()
            steps.append(f"TextProcessor: converting to lowercase -> {result}")
            return result

        if "word count" in lowered or "count words" in lowered or "wordcount" in lowered:
            target = self._extract_between_quotes(text) or self._extract_after_keyword(text, "word count") or text
            wc = len(re.findall(r"\w+", target))
            steps.append(f"TextProcessor: word count -> {wc}")
            return str(wc)

        if "reverse" in lowered:
            target = self._extract_between_quotes(text) or self._extract_after_keyword(text, "reverse") or text
            result = target[::-1]
            steps.append(f"TextProcessor: reverse -> {result}")
            return result

        if "title case" in lowered or "titlecase" in lowered:
            target = self._extract_between_quotes(text) or self._extract_after_keyword(text, "title case") or text
            result = target.title()
            steps.append(f"TextProcessor: title case -> {result}")
            return result

        # default: echo back trimmed text
        steps.append("TextProcessor: no specific operation detected, echoing input")
        return text

    def _extract_between_quotes(self, text):
        m = re.search(r'"([^"]+)"', text)
        if m:
            return m.group(1)
        m2 = re.search(r"'([^']+)'", text)
        if m2:
            return m2.group(1)
        return None

    def _extract_after_keyword(self, text, keyword):
        idx = text.lower().find(keyword)
        if idx >= 0:
            return text[idx + len(keyword):].strip()
        return None


class CalculatorTool:
    name = "CalculatorTool"

    # Allow ast.Constant for newer Python versions
    ALLOWED_NODES = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Constant, ast.Load,
                     ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod,
                     ast.USub, ast.UAdd, ast.FloorDiv, ast.LShift, ast.RShift, ast.BitXor, ast.BitAnd, ast.BitOr, ast.Tuple)

    def execute(self, task_text: str, steps: list):
        steps.append(f"Calculator: parsing expression from \"{task_text}\"")
        expr = self._extract_expression(task_text)
        steps.append(f"Calculator: expression detected -> {expr}")
        value = self._safe_eval(expr)
        steps.append(f"Calculator: result -> {value}")
        return str(value)

    def _extract_expression(self, text):
        # try to extract after keywords
        lowered = text.lower()
        for kw in ["calculate", "what is", "what's", "evaluate", "compute"]:
            if kw in lowered:
                # find the keyword position in the lowercase string and slice the original text
                idx = lowered.find(kw)
                return text[idx + len(kw):].strip()
        # fallback: return whole text
        return text.strip()

    def _safe_eval(self, expr):
        # Pre-process common human operators:
        # - 'x' or '×' between numbers -> '*'
        # - allow '^' for power
        e = expr
        # replace multiplication using 'x' or '×' when it's between digits (with optional spaces)
        e = re.sub(r'(?<=\d)\s*[xX×]\s*(?=\d)', '*', e)
        # also replace patterns like '5 x 10' where x may be separated by spaces
        e = re.sub(r'(?<=\d)\s+[xX×]\s+(?=\d)', '*', e)
        # Replace caret with python power
        e = e.replace('^', '**')
        # Remove any characters except digits, operators, parentheses, dot, percent, and whitespace
        cleaned = re.sub(r"[^0-9\.\+\-\*\/\(\)\%\s\*\*]", "", e)
        # cleaned may have '**' already; ensure it's valid
        try:
            node = ast.parse(cleaned, mode='eval')
            for n in ast.walk(node):
                if not isinstance(n, self.ALLOWED_NODES):
                    raise ValueError("Disallowed expression")
            return eval(compile(node, '<string>', 'eval'))
        except Exception:
            raise ValueError(f"Invalid expression: {expr}")


class WeatherMockTool:
    name = "WeatherMockTool"

    def execute(self, task_text: str, steps: list):
        steps.append(f"WeatherMock: parsing city from \"{task_text}\"")
        city_raw = self._extract_city(task_text)
        city = city_raw or "Unknown"
        # create a deterministic mock based on city name
        temp = 20 + (sum(ord(c) for c in city) % 15)
        cond = "Sunny" if sum(ord(c) for c in city) % 2 == 0 else "Cloudy"
        # Build a clear, human-friendly sentence description
        if city == "Unknown":
            sentence = "Weather information not available for the specified location."
        else:
            # Display city in title case for readability
            display_city = city.title()
            sentence = f"The weather in {display_city} is {cond} with a temperature of {temp}\u00B0C."
        steps.append(f"WeatherMock: returning mock for {city}: {temp}C, {cond}")
        return sentence

    def _extract_city(self, text):
        # Normalize whitespace and strip trailing punctuation
        t = text.strip()
        # Try to find patterns like 'in <city>' or 'for <city>' capturing up to punctuation or end
        m = re.search(r"(?:in|for)\s+(.+?)(?:[\?\.!]|$)", t, re.IGNORECASE)
        stopword_pattern = re.compile(r"\b(?:what(?:'s)?|whats|weather|forecast|is|please|tell|show|give|help)\b", re.IGNORECASE)
        if m:
            raw = m.group(1).strip()
            # If the captured raw text contains a stopword like 'what' or 'weather', split before it
            sw = stopword_pattern.search(raw)
            if sw:
                raw = raw[:sw.start()].strip()
            # normalize commas and spaces, remove any trailing punctuation
            raw = re.sub(r"\s*,\s*", ", ", raw).strip(" ,.!?")
            # if after cleaning there's still content, return it
            if raw:
                return re.sub(r"[^A-Za-z, ]", "", raw).strip()
        # If not found, try to take the last up to three words as a heuristic (clean punctuation)
        cleaned = re.sub(r"[\?\.!]$", "", t)
        parts = cleaned.split()
        if not parts:
            return None
        # try last three, then two, then one
        for n in (3, 2, 1):
            if len(parts) >= n:
                candidate = " ".join(parts[-n:])
                # remove any leading/trailing punctuation from candidate
                candidate_clean = re.sub(r"^[^A-Za-z]+|[^A-Za-z]+$", "", candidate)
                if re.search(r"[A-Za-z]", candidate_clean):
                    return re.sub(r"[^A-Za-z, ]", "", candidate_clean).strip()
        return None
