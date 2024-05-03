from __future__ import annotations

import logging
import xmltodict
import requests
from requests import Request
from urllib3.exceptions import NewConnectionError

from ._sru_aux_formatter import SRUAuxiliaryFormatter
from ._exceptions import NoExplainResponseException, ExplainResponseContentTypeException, ExplainResponseParserException
from ._sru_explain_auto_parser import SRUExplainAutoParser
from ._sru_configuration import SRUConfiguration
from ._search_clause import SearchClause
from ._raw_cql import RawCQL
from ._cql_boolean_operators import CQLBooleanOperatorBase
from ._sort_key import SortKey
from ._search_retrieve import SearchRetrieve

class SRUQueryer():
    supported_sru_versions = ["1.2", "1.1"]
    
    def __init__(self, server_url: str, sru_version: str = None, username: str | None = None, password: str | None = None, default_cql_context_set: str | None = None, default_cql_index: str | None = None, default_cql_relation: str | None = None, disable_validation_for_cql_defaults: bool = False, max_records_supported: int | None = None, default_records_returned: int | None = None , default_record_schema: str | None = None, default_sort_schema: str | None = None):
        """Raises ExplainResponseContentTypeException, NoExplainResponseException, ExplainResponseParserException, or PermissionError"""
        sru_version_to_use = sru_version
        if not sru_version_to_use:
            sru_version_to_use = "1.2"
        elif sru_version_to_use not in self.supported_sru_versions:
            logging.warning(f"SRU version {sru_version_to_use} is not supported. Defaulting to version 1.2...")
            sru_version_to_use = "1.2"

        formatted_explain_query = SRUAuxiliaryFormatter.format_base_explain_query(server_url, sru_version_to_use)

        explain_response_xml: bytes = None
        try:
            explain_response_xml = self._retrieve_explain_response_xml(formatted_explain_query, username, password)
            configuration = self._parse_explain_response_configuration(explain_response_xml)
        except NoExplainResponseException as be:
            logging.exception(be.__str__())
            raise be
        except PermissionError as pe:
            raise pe
        except ExplainResponseContentTypeException as pf: 
            raise pf
        except Exception as e:
            logging.exception(e.__str__())
            if explain_response_xml:
                raise ExplainResponseParserException(e.__str__(), xmltodict.parse(explain_response_xml))
            else: raise NoExplainResponseException(f"Could not connect to the SRU server: {e.__str__()}", e.__str__())
                

        # If the server has sent back a different SRU version than what the explainResponse requested...
        if sru_version_to_use != configuration.sru_version:
            # If the SRU version that the user requested is being used, warn them that the server isn't using this version
            if sru_version == sru_version_to_use:
                logging.warning(f"Server ExplainResponse returned a different SRU version than that which was requested (Returned {configuration.sru_version}, requested {sru_version}). Using version {configuration.sru_version}...")
            else:
                # If the program has overridden the SRU version
                logging.debug(f"Server ExplainResponse returned a different SRU version than that which was requested (Returned {configuration.sru_version}, requested {sru_version}). Using version {configuration.sru_version}...")
            
        # If the user did not request an SRU version, notify themn of which one is being used.
        if not sru_version:
            logging.info(f"Using SRU version {configuration.sru_version}")

        # If there is not a default cql relation returned by the server, set it to '=' (this is the default from the LOC standards)
        # This will later be overridden if the user chooses a value.
        if not configuration.default_relation:
            configuration.default_relation = '='

        configuration.server_url = server_url
        configuration.username = username
        configuration.password = password
        configuration.disable_validation_for_cql_defaults = disable_validation_for_cql_defaults

        # Override SRUExplain values / set if not provided
        if default_records_returned:
            if configuration.default_records_returned and (configuration.default_records_returned != default_records_returned): logging.info(f"Overriding default number of records returned (Using {default_records_returned}, server specified {configuration.default_records_returned}).")
            configuration.default_records_returned = default_records_returned

        if max_records_supported:
            if configuration.max_records_supported and (configuration.max_records_supported != max_records_supported): logging.warning(f"Overriding max records supported (Using {max_records_supported}, server specified {configuration.max_records_supported}).")
            configuration.max_records_supported = max_records_supported

        if default_cql_context_set:
            if configuration.default_context_set and (configuration.default_context_set != default_cql_context_set): logging.warning(f"Overriding default context set (Using {default_cql_context_set}, server specified {configuration.default_context_set}).")
            configuration.default_context_set = default_cql_context_set

        if default_cql_index:
            if configuration.default_index and (configuration.default_index != default_cql_index): logging.warning(f"Overriding default index (Using {default_cql_index}, server specified {configuration.default_index}).")
            configuration.default_index = default_cql_index

        if default_cql_relation:
            if configuration.default_relation and (configuration.default_relation != default_cql_relation): logging.warning(f"Overriding default CQL relation (Using {default_cql_relation}, server specified {configuration.default_relation}).")
            configuration.default_relation = default_cql_relation

        if default_record_schema:
            if configuration.default_record_schema and (configuration.default_record_schema != default_record_schema): logging.info(f"Overriding server specified record schema (Using {default_record_schema}, server specified {configuration.default_record_schema}).")
            configuration.default_record_schema = default_record_schema

        if default_sort_schema:
            if configuration.default_sort_schema and (configuration.default_sort_schema != default_sort_schema): logging.warning(f"Overriding default sort schema (Using {default_sort_schema}, server specified {configuration.default_sort_schema}).")
            configuration.default_sort_schema = default_sort_schema

        self.sru_configuration = configuration

    def search_retrieve(self, cql_query: SearchClause | CQLBooleanOperatorBase | RawCQL, start_record: int | None = None, maximum_records: int | None = None, record_schema: str | None = None, sort_queries: list[dict] | list[SortKey] | None = None, record_packing: str | None = None, validate: bool = True) -> bytes:
        """Conducts a searchRetrieve request and returns the response.

        This will throw ValueErrors for any incorrect portion of the query. 
        
        This function does not handle any errors in the searchRetrieveResponse."""
        query = SearchRetrieve(self.sru_configuration, cql_query, start_record, maximum_records, record_schema, sort_queries, record_packing)
        if validate:
            query.validate()
        request = query.construct_request()
        logging.info(f"Querying {request.url}")
        request = request.prepare()
        s = requests.Session()
        response = s.send(request)
        return response.content
    
    def construct_search_retrieve_request(self, cql_query: SearchClause | CQLBooleanOperatorBase | RawCQL, start_record: int | None = None, maximum_records: int | None = None, record_schema: str | None = None, sort_queries: list[dict] | list[SortKey] | None = None, record_packing: str | None = None, validate: bool = True) -> Request:
        """Construct a requests.Request object, which you can then prepare and use.
        
        This is helpful (as compared to search_retrieve) when you want to create a request, and perhaps modify it
        or use it with your own session mechanism."""
        query = SearchRetrieve(self.sru_configuration, cql_query, start_record, maximum_records, record_schema, sort_queries, record_packing)
        if validate:
            query.validate()
        return query.construct_request()
    
    def format_available_indexes(self, filename: str | None = None, print_to_console: bool = True, title_filter: str | None = None):
        """Formats available indexes, and prints to the console by default.

        Can also print to a file and disable printing to the console."""
        available_context_sets_and_indexes = self.sru_configuration.available_context_sets_and_indexes

        if title_filter:
            available_context_sets_and_indexes = self._filter_available_context_sets_and_indexes(
                available_context_sets_and_indexes, title_filter)

        SRUAuxiliaryFormatter.format_available_indexes(available_context_sets_and_indexes, filename, print_to_console)

    @staticmethod
    def _filter_available_context_sets_and_indexes(available_context_sets_and_indexes: dict, title: str = None) -> dict:
        new_dict: dict = {}

        for context_set in available_context_sets_and_indexes:
            matched_contents = {}
            for index_code in available_context_sets_and_indexes[context_set]:
                index_data = available_context_sets_and_indexes[context_set][index_code]

                if title.lower() in index_data['title'].lower():
                    matched_contents[index_code] = index_data

            if matched_contents:
                new_dict[context_set] = matched_contents

        return new_dict

    @staticmethod
    def _retrieve_explain_response_xml(server_url: str, username: str | None, password: str | None) -> dict:
        response_content = SRUQueryer._get_request_contents(server_url, username, password)
        try:
            content = xmltodict.parse(response_content)
        except Exception as e:
            raise ExplainResponseContentTypeException(f'Couldn\'t convert the explainResponse to a dict: "{e.__str__()}". This is most likely due to receiving a format other than XML.', response_content)
        return content

    @staticmethod
    def _parse_explain_response_configuration(sru_explain_dict: dict) -> SRUConfiguration:
        """This function seems dumb, but is here for mocking purposes."""
        sru_dict_parser = SRUExplainAutoParser(sru_explain_dict)
        return sru_dict_parser.get_sru_configuration_from_explain_response()
    
    @staticmethod
    def _get_request_contents(url: str, username, password):
        """Sends a request and returns the contents - it's a seperate method so we can mock it."""

        if username and password:
            response = requests.get(url, headers={
                "Authorization": SRUAuxiliaryFormatter.format_basic_access_authentication_header_payload(username, password)
            })
        else:
            response = requests.get(url)

        if response.status_code == 401 or response.status_code == 403:
            logging.exception(f"You are not authorized to access this SRU Explain server ({url})")
            raise PermissionError(
                "You are not authorized to access this SRU Explain server")

        return response.content