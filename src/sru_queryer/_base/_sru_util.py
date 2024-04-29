from __future__ import annotations
import logging

from abc import ABC, abstractmethod
import xmltodict
import requests

from ._drivers import alma_driver

from ._sru_explain_dict_parser import SRUExplainDictParser
from ._sru_configuration import SRUConfiguration
from ._sru_aux_formatter import SRUAuxiliaryFormatter


class SRUUtilAbstract(ABC):

    @staticmethod
    @abstractmethod
    def create_configuration_for_server(server_url: str, driver: dict = alma_driver, sru_version: str = None, username: str | None = None, password: str | None = None, default_cql_context_set: str | None = None, default_cql_index: str | None = None, default_cql_relation: str | None = None, disable_validation_for_cql_defaults: bool = False, max_records_supported: int | None = None, default_records_returned: int | None = None, default_record_schema: str | None = None, default_sort_schema: str | None = None) -> SRUConfiguration:
        pass

    @staticmethod
    @abstractmethod
    def format_available_indexes(sru_configuration: SRUConfiguration, filename: str | None = None, print_to_console: bool = False, title_filter: str | None = None):
        pass


class SRUUtil(SRUUtilAbstract):

    @staticmethod
    def create_configuration_for_server(server_url: str, driver: dict = alma_driver, sru_version: str = None, username: str | None = None, password: str | None = None, default_cql_context_set: str | None = None, default_cql_index: str | None = None, default_cql_relation: str | None = None, disable_validation_for_cql_defaults: bool = False, max_records_supported: int | None = None, default_records_returned: int | None = None , default_record_schema: str | None = None, default_sort_schema: str | None = None) -> SRUConfiguration:

        if sru_version not in ["1.2", "1.1"]:
            sru_version = None

        supports_versionless_explain_response = driver["version"]["supportsVersionlessExplainResponse"]
        if not supports_versionless_explain_response and not sru_version:
            logging.warning("This server requires that you specify an SRU version. This tool will continue by assuming version 1.2...")
            sru_version = "1.2"

        formatted_explain_query = SRUAuxiliaryFormatter.format_base_explain_query(server_url, sru_version)
        explain_response_xml = SRUUtil._retrieve_explain_response_xml(formatted_explain_query, username, password)
        configuration = SRUUtil._parse_explain_response_configuration(explain_response_xml, driver)

        # Add user-defined values
        if sru_version and sru_version != configuration.sru_version:
            logging.warning(f"Server ExplainResponse returned a different SRU version than that which was requested (Returned {configuration.sru_version}, requested {sru_version}). Using version {configuration.sru_version}...")
        configuration.server_url = server_url
        configuration.username = username
        configuration.password = password
        configuration.disable_validation_for_cql_defaults = disable_validation_for_cql_defaults

        # Override SRUExplain values / set if not provided
        if default_records_returned:
            if configuration.default_records_returned and (configuration.default_records_returned != default_records_returned): logging.info(f"Overriding default number of records returned (Set {default_records_returned}, server specified {configuration.default_records_returned}).")
            configuration.default_records_returned = default_records_returned

        if max_records_supported:
            if configuration.max_records_supported and (configuration.max_records_supported != max_records_supported): logging.warning(f"Overriding max records supported (Set {max_records_supported}, server specified {configuration.max_records_supported}).")
            configuration.max_records_supported = max_records_supported

        if default_cql_context_set:
            if configuration.default_context_set and (configuration.default_context_set != default_cql_context_set): logging.warning(f"Overriding default context set (Set {default_cql_context_set}, server specified {configuration.default_context_set}).")
            configuration.default_context_set = default_cql_context_set

        if default_cql_index:
            if configuration.default_index and (configuration.default_index != default_cql_index): logging.warning(f"Overriding default index (Set {default_cql_index}, server specified {configuration.default_index}).")
            configuration.default_index = default_cql_index

        if default_cql_relation:
            if configuration.default_relation and (configuration.default_relation != default_cql_relation): logging.warning(f"Overriding default CQL relation (Set {default_cql_relation}, server specified {configuration.default_relation}).")
            configuration.default_relation = default_cql_relation

        if default_record_schema:
            if configuration.default_record_schema and (configuration.default_record_schema != default_record_schema): logging.info(f"Overriding default record schema (Set {default_record_schema}, server specified {configuration.default_record_schema}).")
            configuration.default_record_schema = default_record_schema

        if default_sort_schema:
            if configuration.default_sort_schema and (configuration.default_sort_schema != default_sort_schema): logging.warning(f"Overriding default sort schema (Set {default_sort_schema}, server specified {configuration.default_sort_schema}).")
            configuration.default_sort_schema = default_sort_schema

        return configuration
    
    @staticmethod
    def format_available_indexes(sru_configuration, filename: str | None = None, print_to_console: bool = True, title_filter: str | None = None):
        """Formats available indexes, and prints to the console by default.

        Can also print to a file and disable printing to the console."""
        available_context_sets_and_indexes = sru_configuration.available_context_sets_and_indexes

        if title_filter:
            available_context_sets_and_indexes = SRUUtil._filter_available_context_sets_and_indexes(
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
        response_content = SRUUtil._get_request_contents(server_url, username, password)
        content = xmltodict.parse(response_content)
        return content

    @staticmethod
    def _parse_explain_response_configuration(sru_explain_dict: dict, driver: str) -> SRUConfiguration:
        sru_dict_parser = SRUExplainDictParser(sru_explain_dict, driver)
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

        if response.status_code == 500:
            print(response.content)
            raise RuntimeError("SRU Explain request failed.")
        if response.status_code == 401:
            print(response.content)
            raise PermissionError(
                "You are not authorized to access this SRU Explain URL")

        return response.content
