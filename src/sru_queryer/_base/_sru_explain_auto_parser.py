from __future__ import annotations

from ._sru_configuration import SRUConfiguration
from ._exceptions import NoExplainResponseException

generic_driver = {
    "name": "Generic Driver for auto-detect",
    "version": {
        "location": ["explainResponse", "version"]
    },
    "index": {
        'location': ["explainResponse", "record", "recordData", "explain", "index", "index"],
        # Relative to the index info location above
        "sortLocation": ["@sort"],
        "idLocation": ["@id"], 
        "titleLocation": ["title"],
        "supportedRelationsLocation": ["configInfo", "supports"],
        # Below is relative to map location (hard-coded to ...index["map"])
        "nameLocation": ["name", "#text"],
        "setLocation": ["name", "@set"]
    },
    "schema": {
        "location": ["explainResponse", "record", "recordData", "explain", "schemaInfo", "schema"]
    },
    "defaults": {
        "location": ["explainResponse", "record", "recordData", "explain", "configInfo", "default"]
    },
    "settings": {
        "location": ["explainResponse", "record", "recordData", "explain", "configInfo", "setting"]
    },
    "supports": {
        "location": ["explainResponse", "record", "recordData", "explain", "configInfo", "supports"]
    }
}

class SRUExplainAutoParser():

    def __init__(self, sru_explain_dict: dict):
        self.sru_explain_dict = sru_explain_dict
        self.sru_config: SRUConfiguration = None

    def get_sru_configuration_from_explain_response(self) -> SRUConfiguration:

        # Raise exception if the explainResponse can't be parsed.
        # Check validity - invalid ones will not contain explainResponse 
        contains_explain_response = self._find_property_value(self.sru_explain_dict, ["explainResponse"])
        if not contains_explain_response:
            raise NoExplainResponseException("ExplainResponse could not be parsed", self.sru_explain_dict)

        self.sru_config = SRUConfiguration()
        self.sru_config.sru_version = self._find_property_value(self.sru_explain_dict, generic_driver["version"]["location"])
        self._parse_context_set_and_index_info()
        self._parse_config_info()
        self._parse_schema_info()
       
        return self.sru_config
    
    def _parse_context_set_and_index_info(self):
        """Parses the context set and index information from the explainResponse.
        
        Relies on the sru_explain_dict and sru_config property."""
        index_information = self._find_property_value(self.sru_explain_dict, generic_driver["index"]["location"])
        self.sru_config.available_context_sets_and_indexes = {}
        for index in index_information:
            id = self._find_property_value(index, generic_driver["index"]["idLocation"])
            title = self._find_property_value(index, generic_driver["index"]["titleLocation"])
            empty_term_supported, supported_relations = self._get_supported_relations_for_index(index)

            # Get the sort information
            sortable = None
            sort_info_included_in_indexes = self._evaluate_if_sort_info_included_in_index_info()
            if sort_info_included_in_indexes:
                sort = self._find_property_value(index, generic_driver["index"]["sortLocation"])
                if sort == "true":
                    sortable = True
                else:
                    sortable = False


            context_sets_that_include_this_index = index["map"]
            if isinstance(context_sets_that_include_this_index, dict):
                # A few indexes are part of multiple context sets, so
                # I'll just loop over them. This means turning dicts into
                # a list. 
                context_sets_that_include_this_index = [context_sets_that_include_this_index]

            for context_set in context_sets_that_include_this_index:
                name = self._remove_set_from_index_name(context_set["name"]["#text"])
                set = context_set["name"]["@set"]

                # If the set is not in the index and config info, add it
                if set not in self.sru_config.available_context_sets_and_indexes:
                    self.sru_config.available_context_sets_and_indexes[set] = {}

                # Add the index to its set.
                index_config = self._generate_index_config(title, id=id, sort=sortable, supported_relations=supported_relations, empty_term_supported=empty_term_supported)
                self.sru_config.available_context_sets_and_indexes[set][name] = index_config

    def _parse_config_info(self):
        """Parses the configuration info from the explainResponse."""

        default_information = self._find_property_value(self.sru_explain_dict, generic_driver["defaults"]["location"])
        if default_information:
            if isinstance(default_information, dict):
                default_information = [default_information]

            for default in default_information:
                def_type = default["@type"]
                value = default["#text"]
                if def_type == "numberOfRecords":
                    self.sru_config.default_records_returned = int(value)
                elif def_type == "contextSet":
                    self.sru_config.default_context_set = value
                elif def_type == "index":
                    self.sru_config.default_index = value
                elif def_type == "relation":
                    self.sru_config.default_relation = value
                elif def_type == "retrieveSchema":
                    self.sru_config.default_record_schema = value
                elif def_type == "sortSchema":
                    self.sru_config.default_sort_schema = value

        settings_information = self._find_property_value(self.sru_explain_dict, generic_driver["settings"]["location"])
        if settings_information:
            if isinstance(settings_information, dict):
                settings_information = [settings_information]

            for setting in settings_information:
                setting_name = setting["@type"]
                value = setting["#text"]

                if setting_name == "maximumRecords":
                    self.sru_config.max_records_supported = int(value)

        supports_information = self._find_property_value(self.sru_explain_dict, generic_driver["supports"]["location"])
        if supports_information:
            self.sru_config.supported_relation_modifiers = []
            if isinstance(supports_information, dict):
                supports_information = [supports_information]

            for support_setting in supports_information:
                if support_setting["@type"] == "relationModifier":
                    self.sru_config.supported_relation_modifiers.append(support_setting["#text"])


    def _parse_schema_info(self):
        """Parse the record schema information from the explainResponse.
        
        This will add a list of available schemas to sru_configuration.available_record_schemas.
        
        It counts both the identifier and the official name of the schema as a available record schemas.
        While this is technically duplication, they're both valid ways to write a schema in an SRU query.
        I didn't know this until I had already defined the available_record_schemas as a simple list, and
        didn't want to rip my program apart to fix this. So, for now, the record schemas are all duplicated
        if they have identifiers so that validation will work with those identifier names."""
        schema_information = self._find_property_value(self.sru_explain_dict, generic_driver["schema"]["location"])
        cleaned_record_schema_info: dict = {}
        
        # Turn dict to list so we can interate through it 
        # (just simplifies logic)
        if isinstance(schema_information, dict):
            schema_information = [schema_information]

        for schema in schema_information:
            sort = True
            if schema["@sort"] == "false":
                sort = False

            schema_name = schema["@name"]
            schema_identifier = schema["@identifier"]

            cleaned_record_schema_info[schema_name] = {
                "sort": sort,
                "identifier": schema_identifier
            }
        
        self.sru_config.available_record_schemas = cleaned_record_schema_info

    @staticmethod
    def _find_property_value(input_dict: dict, location: list[str]) -> any | None:
        """This method takes a location in a dict and returns the value at that location.

        The input 'location' is a list of strings that represents the dictionary path to the value
        we want. 

        It's designed to work with different namespaces, so it checks the keys of the dictionary
        to see if any of them INCLUDE the term (rather than exact match). It will then use that
        term.

        If it finds nothing, it will return None. Else, it will return whatever it finds. 
        """
        data = input_dict
        for path_segment in location:
            # Get the available keys and try to find a match
            keys = data.keys()
            actual_key = None
            for key in keys:
                if path_segment in key:
                    actual_key = key

            if actual_key:
                data = data[actual_key]
            else:
                return None

        return data
    
    def _evaluate_if_sort_info_included_in_index_info(self) -> bool:
        sort_information_included_in_index_info = False
        for index in self._find_property_value(self.sru_explain_dict, generic_driver["index"]["location"]):
            sort_info = self._find_property_value(index, generic_driver["index"]["sortLocation"])
            if sort_info != None:
                sort_information_included_in_index_info = True
                break

        return sort_information_included_in_index_info
        

    def _get_supported_relations_for_index(self, index) -> tuple[bool, list[str]]:
        """Get the relations supported by a CQL index.
        
        This takes a CQL index from the explainResponse after being parsed from xmltodict,
        and returns whether empty terms are supported and the other terms that are supported"""
        raw_supported_relations = self._find_property_value(index, generic_driver["index"]["supportedRelationsLocation"])

        if not raw_supported_relations:
            return None, None
        
        supported_relations: dict = []
        empty_term_supported = False
        for relation in raw_supported_relations:
            if relation["@type"] == "emptyTerm":
                empty_term_supported = True
            elif relation["@type"] == "relation":
                supported_relations.append(relation["#text"])

        return empty_term_supported, supported_relations
    
    @staticmethod
    def _generate_index_config(title: str, id: str | None = None, sort: bool | None = None, supported_relations: list[str] = None, empty_term_supported: bool | None = None) -> dict:
        if supported_relations is None: 
            supported_relations = []
        index_config_dict = {
            "id": id,
            "title": title,
            "sort": sort,
            "supported_relations": supported_relations,
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