from __future__ import annotations

class SRUConfiguration():

    def __init__(self, from_dict: dict = None):

        if from_dict:
            try:
                # Values (possibly) pulled from SRU ExplainResponse (some can be overridden by user settings):
                # Availability
                self.available_context_sets_and_indexes: dict = from_dict["available_context_sets_and_indexes"]
                self.available_record_schemas: dict | None = from_dict["available_record_schemas"]
                self.supported_relation_modifiers: list[str] = from_dict["supported_relation_modifiers"]
                # Default CQL
                self.default_context_set: str | None = from_dict["default_context_set"]
                self.default_index: str | None = from_dict["default_index"]
                self.default_relation: str | None = from_dict["default_relation"]
                self.default_record_schema: str | None = from_dict["default_record_schema"]
                self.default_sort_schema: str | None = from_dict["default_sort_schema"]
                # Default record numbers
                self.default_records_returned: int | None = int(from_dict["default_records_returned"])
                self.max_records_supported: int | None = int(from_dict["max_records_supported"])

                # Hard-coded limits from documentation
                self.available_record_packing_values = ["string", "xml"]

                # Values set by user
                self.server_url: str = from_dict["server_url"]
                self.sru_version: str = from_dict["sru_version"]
                self.username: str | None = from_dict["username"]
                self.password: str | None = from_dict["password"]
                self.disable_validation_for_cql_defaults: bool = from_dict["disable_validation_for_cql_defaults"]
            except KeyError as ke:
                raise ValueError(f"SRU Configuration dict is not valid: '{ke.__str__()}'")

            return

        # Values (possibly) pulled from SRU ExplainResponse (some can be overridden by user settings):
        # Availability
        self.available_context_sets_and_indexes: dict = {}
        self.available_record_schemas: dict | None = None
        self.supported_relation_modifiers: list[str] = []
        # Default CQL
        self.default_context_set: str | None = None
        self.default_index: str | None = None
        self.default_relation: str | None = None
        self.default_record_schema: str | None = None
        self.default_sort_schema: str | None = None
        # Default record numbers
        self.default_records_returned: int | None = None
        self.max_records_supported: int | None = None

        # Hard-coded limits from documentation
        self.available_record_packing_values = ["string", "xml"]

        # Values set by user
        self.server_url: str = None
        self.sru_version: str = None
        self.username: str | None = None
        self.password: str | None = None
        self.disable_validation_for_cql_defaults: bool = False
