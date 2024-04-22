from __future__ import annotations

from abc import ABC, abstractmethod
from base64 import b64encode

from ._sru_configuration import SRUConfiguration
from ._sort_key import SortKey

class SRUAuxiliaryFormatterAbstract(ABC):

    @staticmethod
    @abstractmethod
    def format_available_indexes(available_context_sets_and_indexes: dict, filename: str | None = None, print_to_console: bool = True):
        pass

    @staticmethod
    @abstractmethod
    def format_base_explain_query(base_explain_url: str, version: str) -> str:
        pass
    
    @staticmethod
    @abstractmethod
    def format_base_search_retrieve_query(sru_configuration: SRUConfiguration, start_record: int | None = None, maximum_records: int | None = None, record_schema: str | None = None, record_packing: str |  None = None) -> str:
        pass

    @staticmethod
    @abstractmethod
    def format_sort_query(sort_queries: list[dict] | list[SortKey] | None) -> str:
        pass

    @staticmethod
    @abstractmethod
    def format_basic_access_authentication_header_payload(username: str, password: str):
        pass


class SRUAuxiliaryFormatter(SRUAuxiliaryFormatterAbstract):

    @staticmethod
    def format_available_indexes(available_context_sets_and_indexes: dict, filename: str | None = None, print_to_console: bool = True):
        formatted_string = ""

        for context_set in available_context_sets_and_indexes:
            formatted_string += f"------INDEX SET: {context_set}------\n\n"
            for index_code in available_context_sets_and_indexes[context_set]:
                index_data = available_context_sets_and_indexes[context_set][index_code]

                formatted_string += f"Index: {index_data['title']}\n"

                if index_data["id"]:
                    formatted_string += f"     Index ID:               | {index_data['id']}\n"

                formatted_string += f"     Index Set:              | {context_set}\n"
                formatted_string += f"     Index Code:             | {index_code}\n"

                if index_data["supported_operations"]:
                    formatted_string += f"     Supported Operations:   | {index_data['supported_operations'].__str__()}\n"

                sort = index_data['sort']
                if sort != None:
                    formatted_string += f"     Sortable:               | {sort}\n\n"
                formatted_string += "\n"

        if print_to_console:
            print(formatted_string)

        if filename:
            with open(filename, "w") as f:
                f.write(formatted_string)

    @staticmethod
    def format_base_explain_query(base_explain_url: str, version: str) -> str:
        return f'{base_explain_url}?version={str(version)}&operation=explain'
    
    @staticmethod
    def format_base_search_retrieve_query(sru_configuration: SRUConfiguration, start_record: int | None = None, maximum_records: int | None = None, record_schema: str | None = None, record_packing: str | None = None) -> str:
        search_retrieve_base_query = f"{sru_configuration.search_retrieve_url}?version={sru_configuration.sru_version}&operation=searchRetrieve"

        record_schema_to_include = record_schema
        if not record_schema:
            if sru_configuration.default_record_schema:
                record_schema_to_include = sru_configuration.default_record_schema
        if record_schema_to_include:
            search_retrieve_base_query += f'&recordSchema={record_schema_to_include}'

        if start_record:
            search_retrieve_base_query += f"&startRecord={start_record}"

        maximum_records_to_include = maximum_records
        if not maximum_records:
            if sru_configuration.default_records_returned:
                maximum_records_to_include = sru_configuration.default_records_returned
        if maximum_records_to_include:
            search_retrieve_base_query += f"&maximumRecords={maximum_records_to_include}"
            
        if record_packing:
            search_retrieve_base_query += f"&recordPacking={record_packing}"

        search_retrieve_base_query += "&query="

        return search_retrieve_base_query

    @staticmethod
    def format_sort_query(sort_queries: list[dict] | list[SortKey] | None) -> str:
        """Formats an array of sortBy clauses or SortKeys."""
        if not sort_queries:
            return ""
        
        sort_query = ""
        if isinstance(sort_queries[0], SortKey):
            sort_query += "&sortKeys="
            sort_query += SortKey.format_array(sort_queries)
        else:
            sort_query += "%20sortBy"
            for sort in sort_queries:
                index_set = sort["index_set"]
                index_name = sort["index_name"]
                sort_order = sort["sort_order"]

                sort_query += f"%20{index_set}.{index_name}/sort.{sort_order}"

        return sort_query

    @staticmethod
    def format_basic_access_authentication_header_payload(username: str, password: str):
        credentials = f"{username}:{password}"
        return f"Basic {b64encode(credentials.encode()).decode()}"