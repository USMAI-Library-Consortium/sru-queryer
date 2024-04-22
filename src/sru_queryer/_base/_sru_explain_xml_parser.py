from __future__ import annotations

from abc import ABC, abstractmethod
import sys

from ._sru_configuration import SRUConfiguration

class SRUExplainXMLParserAbstract(ABC):

    def __init__(self, sru_explain_dict: dict, driver: dict):
        self.sru_explain_dict = sru_explain_dict
        self.driver = driver

    @abstractmethod
    def get_sru_configuration_from_explain_response(self) -> SRUConfiguration:
        pass

class SRUExplainXMLParser(SRUExplainXMLParserAbstract):

    def __init__(self, sru_explain_dict: dict, driver: dict):
        self.sru_explain_dict = sru_explain_dict
        self.driver = driver
    
    def get_sru_configuration_from_explain_response(self) -> SRUConfiguration:
        sru_configuration = SRUConfiguration()

        raw_index_info = self._parse_raw_index_info_from_xml()
        sru_configuration.available_context_sets_and_indexes = self._parse_available_context_sets_and_index_info(raw_index_info)
        
        raw_schema_info = self._parse_raw_schema_info_from_xml()
        sru_configuration.available_record_schemas = self._parse_schema_info(raw_schema_info)

        raw_config_info = self._parse_raw_config_info_from_xml()
        config_info = self._parse_config_info(raw_config_info)

        if config_info:
            sru_configuration.supported_relation_modifiers = config_info["supported_relation_modifiers"]
            sru_configuration.default_context_set = config_info["default_context_set"]
            sru_configuration.default_index = config_info["default_index"]
            sru_configuration.default_relation = config_info["default_relation"]
            sru_configuration.default_record_schema = config_info["default_record_schema"]
            sru_configuration.default_sort_schema = config_info["default_sort_schema"]
            sru_configuration.default_records_returned = config_info["default_records_returned"]
            sru_configuration.max_records_supported = config_info["max_records_supported"]

        return sru_configuration

    def _parse_raw_index_info_from_xml(self) -> list[dict] | None:
        path_to_index_info = self.driver["indexInfo"]["indexInfoLocation"]
        
        return self._pull_data_from_dict(self.sru_explain_dict, path_to_index_info)
    
    def _parse_raw_schema_info_from_xml(self) -> list[dict] | None:
        path_to_schema_info = self.driver["schemaInfo"]["schemaInfoLocation"]
        
        return self._pull_data_from_dict(self.sru_explain_dict, path_to_schema_info)

    def _parse_raw_config_info_from_xml(self) -> dict | None:
        path_to_config_info = self.driver["configInfo"]["configInfoLocation"]

        return self._pull_data_from_dict(self.sru_explain_dict, path_to_config_info)
    
    def _parse_available_context_sets_and_index_info(self, raw_index_info) -> dict | None:
        if raw_index_info is None:
            return None

        available_context_sets_and_indexes = {}
        driver_base = self.driver["indexInfo"]

        try:
            path_to_sort = driver_base["sortLocation"]
            path_to_id = driver_base["idLocation"]
            path_to_title = driver_base["titleLocation"]
            path_to_supported_operations = driver_base["supportedOperationsLocation"]
            path_to_name = driver_base["nameLocation"]
            path_to_set = driver_base["setLocation"]
        except KeyError:
            sys.exit(f"One or more indexInfo paths for driver '{self.driver}' are not specified.\nPlease add them to config.py.")

        # Checks if sort info is included in the index info.
        sort_information_included_in_index_info = self._evaluate_if_sort_info_included_in_index_info(raw_index_info, path_to_sort)

        for raw_index in raw_index_info:
            id = self._pull_data_from_dict(raw_index, path_to_id)
            title = self._pull_data_from_dict(raw_index, path_to_title)
            
            raw_supported_operations: list = self._pull_data_from_dict(raw_index, path_to_supported_operations, throw_error_if_not_found=False)
            empty_term_supported, supported_operations = self._parse_raw_supported_operations(raw_supported_operations)

            sort = self._parse_sort_info(raw_index, path_to_sort, sort_information_included_in_index_info)

            maps = raw_index["map"]
            if isinstance(maps, dict):
                maps = [maps]

            for map in maps:
                name = self._remove_set_from_index_name(self._pull_data_from_dict(map, path_to_name))
                set = self._pull_data_from_dict(map, path_to_set)

                # If the set is not in the index and config info, add it
                if set not in available_context_sets_and_indexes:
                    available_context_sets_and_indexes[set] = {}

                # Add the index to its set.
                index_config = self._generate_index_config(title, id=id, sort=sort, supported_operations=supported_operations, empty_term_supported=empty_term_supported)
                available_context_sets_and_indexes[set][name] = index_config

        return available_context_sets_and_indexes
    
    def _parse_config_info(self, raw_config_info) -> dict | None:
        if raw_config_info is None:
            return None
        
        driver_base = self.driver["configInfo"]

        try:
            path_to_defaults = driver_base["defaultsLocation"]
            path_to_settings = driver_base["settingsLocation"]
            path_to_supports = driver_base["supportsLocation"]
        except KeyError:
            sys.exit(f"One or more configInfo paths for driver '{self.driver.name}' are not specified.\nPlease add them to config.py.")

        parsed_config_info = {
            "default_context_set": None,
            "default_index": None,
            "default_relation": None,
            "default_record_schema": None,
            "default_sort_schema": None,
            "default_records_returned": None,
            "max_records_supported": None,
            "supported_relation_modifiers": []
        }

        default_information = self._pull_data_from_dict(raw_config_info, path_to_defaults)
        if default_information:
            if isinstance(default_information, dict):
                default_information = [default_information]

            for default in default_information:
                def_type = default["@type"]
                value = default["#text"]
                if def_type == "numberOfRecords":
                    parsed_config_info["default_records_returned"] = int(value)
                elif def_type == "contextSet":
                    parsed_config_info["default_context_set"] = value
                elif def_type == "index":
                    parsed_config_info["default_index"] = value
                elif def_type == "relation":
                    parsed_config_info["default_relation"] = value
                elif def_type == "retrieveSchema":
                    parsed_config_info["default_record_schema"] = value
                elif def_type == "sortSchema":
                    parsed_config_info["default_sort_schema"] = value

        settings_information = self._pull_data_from_dict(raw_config_info, path_to_settings)
        if settings_information:
            if isinstance(settings_information, dict):
                settings_information = [settings_information]

            for setting in settings_information:
                setting_name = setting["@type"]
                value = setting["#text"]

                if setting_name == "maximumRecords":
                    parsed_config_info["max_records_supported"] = int(value)

        supports_information = self._pull_data_from_dict(raw_config_info, path_to_supports)
        if supports_information:
            if isinstance(supports_information, dict):
                supports_information = [supports_information]

            for support_setting in supports_information:
                support_type = support_setting["@type"]

                if support_type == "relationModifier":
                    value = support_setting["#text"]
                    parsed_config_info["supported_relation_modifiers"].append(value)

        return parsed_config_info
    
    def _parse_schema_info(self, raw_schema_info) -> dict | None :
        if raw_schema_info is None:
            return None
        
        cleaned_record_schema_info: dict = {}
        
        # Turn dict to list so we can interate through it 
        # (just simplifies logic)
        if isinstance(raw_schema_info, dict):
            raw_schema_info = [raw_schema_info]

        for schema in raw_schema_info:
            sort = True
            if schema["@sort"] == "false":
                sort = False

            schema_name = schema["@name"]
            # The schema identifier can be used in place of the
            # name in a query
            alternate_schema_name = self._pull_data_from_dict(schema, ["@identifier"])

            cleaned_record_schema_info[schema_name] = {
                "sort": sort
            }

            if alternate_schema_name:
                cleaned_record_schema_info[alternate_schema_name] = {
                    "sort": sort
                }
        
        return cleaned_record_schema_info
    
    @staticmethod
    def _parse_sort_info(raw_index: dict, path_to_sort: list, sort_information_included_in_index_info: bool) -> bool:
        """Parses whether an index can be sorted
        
        For any index, 'sort' will either be None, or 'true'. This is because when sort is 'false', the
        sort information is not included.
        
        We need also need the boolean 'sort_information_included_in_index_info', as indexes in explainResponses that have
        no sort information look the same as ones where sort=false (they both have no sort key). 
        When a response DOES incude sort info on at least one index, we interpret missing sort info as meaning 
        the index cannot be sorted. Else, we will include 'None,' which indicates that the information is not available.
        
        We also, of course, need to convert the string 'true' to Python's boolean 'True'"""
        sort = SRUExplainXMLParser._pull_data_from_dict(raw_index, path_to_sort, throw_error_if_not_found=False)
        if sort is None and sort_information_included_in_index_info:
            sort = False
        elif sort == "true":
            sort = True

        return sort
    
    @staticmethod
    def _evaluate_if_sort_info_included_in_index_info(raw_index_info, path_to_sort) -> bool:
        sort_information_included_in_index_info = False
        for index in raw_index_info:
            sort_info = SRUExplainXMLParser._pull_data_from_dict(index, path_to_sort, throw_error_if_not_found=False)
            if sort_info != None:
                sort_information_included_in_index_info = True
                break

        return sort_information_included_in_index_info
    
    @staticmethod
    def _parse_raw_supported_operations(raw_supported_operations, ):
        supported_operations = []
        empty_term_supported = None
        if raw_supported_operations:
            empty_term_supported = False
            for operation in raw_supported_operations:
                if operation["@type"] == "emptyTerm":
                    empty_term_supported = True
                elif operation["@type"] == "relation":
                    supported_operations.append(operation["#text"])
        
        return empty_term_supported, supported_operations
        
    @staticmethod
    def _pull_data_from_dict(dict, path_to_data: list[str], throw_error_if_not_found: bool=True) -> dict | list | None:
        """Given a dictionary and an array of property names, goes down the chain to
        find the property you're looking for. Returns -1 if not found."""
        if not path_to_data:
            return None

        data = dict
        try:
            for path_segment in path_to_data:
                data = data[path_segment]
        except KeyError as ke:
            if throw_error_if_not_found:
                raise ke
            
            return None

        return data
    
    @staticmethod
    def _generate_index_config(title: str, id: str | None = None, sort: bool | None = None, supported_operations: list[str] = None, empty_term_supported: bool | None = None) -> dict:
        if supported_operations is None: 
            supported_operations = []
        index_config_dict = {
            "id": id,
            "title": title,
            "sort": sort,
            "supported_operations": supported_operations,
            "empty_term_supported": empty_term_supported
        }

        return index_config_dict
    
    @staticmethod
    def _remove_set_from_index_name(index_name: str) -> str:
        """Removes the set from an index name.
        
        One explain response included the set name in the index
        name, which broke validation for the default set (which
        didn't have the period in its name). Therefor, I'm
        removing the first value + period from every index name.
        
        This may have to be modified if there's an explain response
        which returns a period in the index name that's NOT the set."""
        period_in_index_name = index_name.find(".") != -1
        if period_in_index_name:
            index_of_period = index_name.find(".") + 1
            return index_name[index_of_period:]
        else:
            return index_name