from __future__ import annotations

class RawCQL():

    def __init__(self, raw_cql_string: str, add_padding=False):
        self.raw_cql_string = raw_cql_string
        self.add_padding = add_padding

    def format(self):
        return self._format()

    def _format(self, **kwargs):
        if self.add_padding:
            return f"%20{self.raw_cql_string}%20"
        else:
            return self.raw_cql_string

    def validate(self, _):
        return