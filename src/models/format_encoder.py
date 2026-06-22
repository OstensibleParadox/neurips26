"""Format encoders: map semantic content → token surface form."""
from typing import Callable

FORMATS = ["direct", "clinical", "data", "fiction", "code"]


class FormatEncoder:
    def __init__(self, format_name: str):
        assert format_name in FORMATS, f"Unknown format: {format_name}"
        self.format_name = format_name

    def encode(self, content: str) -> str:
        """Transform semantic content into the target format surface."""
        encoders: dict[str, Callable] = {
            "direct":   lambda c: c,
            "clinical": lambda c: f"Clinical note: {c}",
            "data":     lambda c: f'{{"content": "{c}"}}',
            "fiction":  lambda c: f"In the story, the character said: '{c}'",
            "code":     lambda c: f'# {c}\nprint("{c}")',
        }
        return encoders[self.format_name](content)
