from __future__ import annotations

class RawCQL():

    def __init__(self, raw_cql_string: str = None, add_padding=False, from_dict: dict | None = None):
        if not from_dict and not raw_cql_string:
            raise ValueError("You must provide a raw CQL string or a dictionary when instantiating RawCQL")
        
        if from_dict:
            try:
                if from_dict["type"] != "rawCQL": 
                    raise KeyError()     
                self.raw_cql_string = from_dict["cql"]
            except KeyError:
                raise ValueError(f"Dict is not the correct format to instantiate RawCQL: {from_dict.__str__()}")
            # Always add padding for dicts
            self.add_padding = True
            return
        
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