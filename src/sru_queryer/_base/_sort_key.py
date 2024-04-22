from __future__ import annotations

class SortKey:
    """ONLY FOR SRU VERSION 1.1
    
    Implements formatting and validation for SRU version 1.1 sort queries"""
    _valid_missing_values = ["abort", "highValue", "lowValue", "omit"]
    _boolean_map = {
        True: 1,
        False: 0
    }
    
    def __init__(self, xpath:str, schema:str | None = None, ascending:bool = None, case_sensitive:bool = None, missing_value: str = None):
        self._xpath = xpath
        self._schema = schema
        self._ascending = ascending
        self._case_sensitive = case_sensitive

        if missing_value:
            missing_value_starts_and_ends_with_double_quotes = (missing_value.startswith('"') and missing_value.endswith('"'))
            if missing_value not in self._valid_missing_values and not missing_value_starts_and_ends_with_double_quotes:
                raise ValueError(f"Value '{missing_value}' is not a valid option for 'missing value.'")    
        self._missing_value = missing_value

    def format(self) -> str:
        # Find the last comma-deliminated section we should format
        # (sort by's can't end in a comma)
        schema_section = 2
        ascending_section = 3
        case_sensitive_section = 4
        missing_value_section = 5

        last_section = 1
        if self._schema: last_section = schema_section
        if self._ascending != None: last_section = ascending_section
        if self._case_sensitive != None: last_section = case_sensitive_section
        if self._missing_value: last_section = missing_value_section

        formatted_sort:str = f"{self._xpath}"
    
        print_schema_section = schema_section <= last_section
        if print_schema_section:
            formatted_sort += ","
        if self._schema:
            formatted_sort += f"{self._schema}"

        print_ascending_section = ascending_section <= last_section
        if print_ascending_section:
            formatted_sort += ","
        if self._ascending != None:
            formatted_sort += f"{self._boolean_map[self._ascending]}"

        print_case_sensitive_section = case_sensitive_section <= last_section
        if print_case_sensitive_section:
            formatted_sort += ","
        if self._case_sensitive != None:
            formatted_sort += f"{self._boolean_map[self._case_sensitive]}"
        
        print_missing_value_section = missing_value_section <= last_section
        if print_missing_value_section:
             formatted_sort += ","
        if self._missing_value:
            formatted_sort += f"{self._missing_value}"

        return formatted_sort
    
    @staticmethod
    def format_array(sort_keys: list):
        formatted_sort_keys = ""
        for i, sort_key in enumerate(sort_keys):
            if i == 0:
                formatted_sort_keys += sort_key.format()
            else:
                formatted_sort_keys += f"%20{sort_key.format()}"

        return formatted_sort_keys