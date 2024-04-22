from __future__ import annotations
from requests import Request, PreparedRequest

from ._search_index_config import IndexQuery
from ._cql_literal import LITERAL
from ._cql_boolean_operators import CQLBooleanOperatorBase
from ._sru_configuration import SRUConfiguration
from ._sru_validator import SRUValidator
from ._sru_aux_formatter import SRUAuxiliaryFormatter
from ._sort_key import SortKey

class Query:

    def __init__(self, sru_configuration: SRUConfiguration, index_search: IndexQuery | CQLBooleanOperatorBase | LITERAL, start_record: int | None = None, maximum_records: int | None = None, record_schema: str | None = None, sort_queries: list[dict] | list[SortKey] | None = None, record_packing: str | None = None):
        self.sru_configuration = sru_configuration
        self.index_search = index_search
        self.start_record = start_record
        self.maximum_records = maximum_records
        self.record_schema = record_schema
        self.record_packing = record_packing

        if sru_configuration.sru_version == "1.2":
            if sort_queries and isinstance(sort_queries[0], SortKey):
                raise ValueError("You cannot use SortKeys with SRU version 1.2. Please see documentation on constructing a SortBy request.")
        if sru_configuration.sru_version == "1.1":
            if sort_queries and not isinstance(sort_queries[0], SortKey):
                raise ValueError("You must use SortKeys for sorting with SRU version 1.1. Please see documentation on SortKey objects.")
        self.sort_queries = sort_queries

    def validate(self):
        """Validates the query. 
        Keep in mind that not all facets of the query are validated."""

        SRUValidator.validate_base_query(self.sru_configuration,
            self.start_record, self.maximum_records, self.record_schema, self.record_packing)

        self.index_search.validate(self.sru_configuration)

        SRUValidator.validate_sort(self.sru_configuration, self.sort_queries, self.record_schema)

    def construct_request(self) -> PreparedRequest:
        """Constructs the searchRetrieve request.

        Constructs the searchRetrieve request, including the base request, CQL query, and sortBy.

        If you added a username and password when initializing the SRUUtil, it will be added to the
        headers of the request using the 'Basic access authentication' protocol.

        Returns a PreparedRequest object. You can execute it using an instance of requests.Session:\n
            s = requests.Session()\n
            response = s.send(request)\n"""
        search_retrieve_query = SRUAuxiliaryFormatter.format_base_search_retrieve_query(self.sru_configuration,
            self.start_record, self.maximum_records, self.record_schema, self.record_packing)

        if isinstance(self.index_search, IndexQuery) and not (self.index_search.get_index_name() and self.index_search.get_operation()):
            # If it's just a single value (search term) as the query, without anything else, append an equals sign.
            search_retrieve_query += "="
        search_retrieve_query += self.index_search.format()

        search_retrieve_query += SRUAuxiliaryFormatter.format_sort_query(self.sort_queries)

        # Create the actual request object
        request = Request("GET", search_retrieve_query)
        if self.sru_configuration.username and self.sru_configuration.password:
            request.headers["Authorization"] = SRUAuxiliaryFormatter.format_basic_access_authentication_header_payload(self.sru_configuration.username, self.sru_configuration.password)

        request = request.prepare()

        return request
