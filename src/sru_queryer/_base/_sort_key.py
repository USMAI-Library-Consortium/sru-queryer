from __future__ import annotations

class SortKey:
    """ONLY FOR SRU VERSION 1.1
    
    Implements formatting and validation for SRU version 1.1 sort queries"""
    _valid_missing_values = ["abort", "highValue", "lowValue", "omit"]
    _boolean_map = {
        True: 1,
        False: 0
    }
    
    def __init__(self, xpath:str | None = None, schema:str | None = None, ascending:bool = None, case_sensitive:bool = None, missing_value: str = None, from_dict: dict | None = None):
        self._xpath = xpath if not from_dict else None
        self._schema = schema if not from_dict else None
        self._ascending = ascending if not from_dict else None
        self._case_sensitive = case_sensitive if not from_dict else None

        if not xpath and not from_dict:
            raise ValueError("You must include an xpath or a dictionary when instantiating SortKeys.")
        
        if from_dict:
            try:
                self._xpath = from_dict["xpath"]

                if "schema" in from_dict.keys():
                    self._schema = from_dict["schema"]

                if "missing_value" in from_dict.keys():
                    missing_value = from_dict["missing_value"]

                if "ascending" in from_dict.keys():
                    ascending_value = None
                    if from_dict["ascending"] == "true" or from_dict["ascending"] == True:
                        ascending_value = True
                    elif from_dict["ascending"] == "false" or from_dict["ascending"] == False:
                        ascending_value = False
                    self._ascending = ascending_value

                if "case_sensitive" in from_dict.keys():
                    case_sensitive_value = None
                    if from_dict["case_sensitive"] == "true" or from_dict["case_sensitive"] == True:
                        case_sensitive_value = True
                    elif from_dict["case_sensitive"] == "false" or from_dict["case_sensitive"] == False:
                        case_sensitive_value = False
                    self._case_sensitive = case_sensitive_value
            except KeyError as ke:
                raise ValueError(f"Invalid dictionary for creating a sort key: {from_dict.__str__()}. You're missing {ke.__str__()}.")

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