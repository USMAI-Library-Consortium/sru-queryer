from __future__ import annotations

from abc import ABC, abstractmethod
import xmltodict
import requests

from ._drivers import alma_driver

from ._sru_explain_xml_parser import SRUExplainXMLParser
from ._sru_configuration import SRUConfiguration
from ._sru_aux_formatter import SRUAuxiliaryFormatter


class SRUUtilAbstract(ABC):

    @staticmethod
    @abstractmethod
    def create_configuration_for_server(explain_url: str, search_retrieve_url: str, sru_version: str = "1.2", driver: str = "alma", username: str | None = None, password: str | None = None, default_cql_context_set: str | None = None, default_cql_index: str | None = None, default_cql_relation: str | None = None, disable_validation_for_cql_defaults: bool = False, max_records_supported: int | None = None, default_records_returned: int | None = None, default_record_schema: str | None = None, default_sort_schema: str | None = None) -> SRUConfiguration:
        pass

    @staticmethod
    @abstractmethod
    def format_available_indexes(sru_configuration: SRUConfiguration, filename: str | None = None, print_to_console: bool = False, title_filter: str | None = None):
        pass


class SRUUtil(SRUUtilAbstract):

    @staticmethod
    def create_configuration_for_server(explain_url: str, search_retrieve_url: str, sru_version: str = "1.2", driver: dict = alma_driver, username: str | None = None, password: str | None = None, default_cql_context_set: str | None = None, default_cql_index: str | None = None, default_cql_relation: str | None = None, disable_validation_for_cql_defaults: bool = False, max_records_supported: int | None = None, default_records_returned: int | None = None , default_record_schema: str | None = None, default_sort_schema: str | None = None) -> SRUConfiguration:
        formatted_explain_query = SRUAuxiliaryFormatter.format_base_explain_query(explain_url, sru_version)
        explain_response_xml = SRUUtil._retrieve_explain_response_xml(formatted_explain_query, username, password)
        configuration = SRUUtil._parse_explain_response_configuration(explain_response_xml, driver)

        # Add user-defined values
        configuration.explain_url = explain_url
        configuration.search_retrieve_url = search_retrieve_url
        configuration.sru_version = sru_version
        configuration.username = username
        configuration.password = password
        configuration.disable_validation_for_cql_defaults = disable_validation_for_cql_defaults

        # Override SRUExplain values / set if not provided
        if default_records_returned:
            configuration.default_records_returned = default_records_returned

        if max_records_supported:
            configuration.max_records_supported = max_records_supported

        if default_cql_context_set:
            configuration.default_context_set = default_cql_context_set

        if default_cql_index:
            configuration.default_index = default_cql_index

        if default_cql_relation:
            configuration.default_relation = default_cql_relation

        if default_record_schema:
            configuration.default_record_schema = default_record_schema

        if default_sort_schema:
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
    def _retrieve_explain_response_xml(sru_explain_url: str, username: str | None, password: str | None) -> dict:
        response_content = SRUUtil._get_request_contents(sru_explain_url, username, password)
        return xmltodict.parse(response_content)

    @staticmethod
    def _parse_explain_response_configuration(sru_explain_dict: dict, driver: str) -> SRUConfiguration:
        sru_xml_parser = SRUExplainXMLParser(sru_explain_dict, driver)
        return sru_xml_parser.get_sru_configuration_from_explain_response()
    
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
