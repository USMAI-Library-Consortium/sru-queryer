from __future__ import annotations

class SRUConfiguration():

    def __init__(self):
        # Values (possibly) pulled from SRU ExplainResponse (some can be overridden by user settings):
        # Availability
        self.available_context_sets_and_indexes: dict = {}
        self.available_record_schemas: dict = {}
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
        self.explain_url: str = None
        self.search_retrieve_url: str = None
        self.sru_version: str = None
        self.username: str | None = None
        self.password: str | None = None
        self.disable_validation_for_cql_defaults: bool = False
