from __future__ import annotations

class LITERAL():

    def __init__(self, literal_string: str, add_padding=False):
        self.literal_string = literal_string
        self.add_padding = add_padding

    def format(self):
        return self._format()

    def _format(self, **kwargs):
        if self.add_padding:
            return f"%20{self.literal_string}%20"
        else:
            return self.literal_string

    def validate(self, _):
        return