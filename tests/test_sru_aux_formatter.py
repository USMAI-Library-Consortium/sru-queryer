import unittest

from tests.testData.test_data import get_gapines_sru_configuration, get_alma_sru_configuration
from src.sru_queryer._base._sru_aux_formatter import SRUAuxiliaryFormatter

class TestSRUAuxiliaryFormatter(unittest.TestCase):
    def test_format_basic_access_authentication_header_payload(self, *args):
        username = "testusername01"
        password = "testpass01"

        actual_payload = SRUAuxiliaryFormatter.format_basic_access_authentication_header_payload(
            username, password)

        self.assertEqual(
            "Basic dGVzdHVzZXJuYW1lMDE6dGVzdHBhc3MwMQ==", actual_payload)

    def test_format_basic_access_authentication_header_payload_with_underscore(self, *args):
        username = "testusername__01"
        password = "testpass01"

        actual_payload = SRUAuxiliaryFormatter.format_basic_access_authentication_header_payload(
            username, password)

        self.assertEqual(
            "Basic dGVzdHVzZXJuYW1lX18wMTp0ZXN0cGFzczAx", actual_payload)

    def test_format_basic_access_authentication_header_payload_with_special_character(self, *args):
        username = "testusername01"
        password = "testpass01!!"

        actual_payload = SRUAuxiliaryFormatter.format_basic_access_authentication_header_payload(
            username, password)

        self.assertEqual(
            "Basic dGVzdHVzZXJuYW1lMDE6dGVzdHBhc3MwMSEh", actual_payload)
        
    def test_format_search_explain_url_with_version_1_1(self):
        base_url =  "https://example.com"
        expected_url = f"{base_url}?version=1.1&operation=explain"

        actual_url = SRUAuxiliaryFormatter.format_base_explain_query(base_url, "1.1")

        self.assertEqual(expected_url, actual_url)

    def test_format_search_retrieve_query_start_record_not_default(self):
        sru_configuration = get_gapines_sru_configuration()
        sru_configuration.search_retrieve_url = "https://example.com"
        sru_configuration.sru_version = "1.2"

        actual_query = SRUAuxiliaryFormatter.format_base_search_retrieve_query(sru_configuration,
            start_record=7, maximum_records=10, record_schema="marcxml")

        expected_query = "https://example.com?version=1.2&operation=searchRetrieve&recordSchema=marcxml&startRecord=7&maximumRecords=10&query="

        self.assertEqual(actual_query, expected_query)

    def test_format_search_retrieve_query_maximum_records_not_default(self):
        sru_configuration = get_gapines_sru_configuration()
        sru_configuration.search_retrieve_url = "https://example.com"
        sru_configuration.sru_version = "1.2"

        actual_query = SRUAuxiliaryFormatter.format_base_search_retrieve_query(sru_configuration,
            start_record=1, maximum_records=7, record_schema="marcxml")

        expected_query = "https://example.com?version=1.2&operation=searchRetrieve&recordSchema=marcxml&startRecord=1&maximumRecords=7&query="

        self.assertEqual(actual_query, expected_query)

    def test_format_search_retrieve_query_version_1_1(self):
        sru_configuration = get_gapines_sru_configuration()
        sru_configuration.search_retrieve_url = "https://example.com"
        sru_configuration.sru_version = "1.1"

        actual_query = SRUAuxiliaryFormatter.format_base_search_retrieve_query(sru_configuration,
            start_record=1, maximum_records=10, record_schema="marcxml")

        expected_query = "https://example.com?version=1.1&operation=searchRetrieve&recordSchema=marcxml&startRecord=1&maximumRecords=10&query="

        self.assertEqual(actual_query, expected_query)

    def test_format_search_retrieve_query_default_record_schema(self):
        sru_configuration = get_gapines_sru_configuration()
        sru_configuration.search_retrieve_url = "https://example.com"
        sru_configuration.sru_version = "1.1"

        actual_query = SRUAuxiliaryFormatter.format_base_search_retrieve_query(sru_configuration,
            start_record=1, maximum_records=10)

        expected_query = "https://example.com?version=1.1&operation=searchRetrieve&recordSchema=marcxml&startRecord=1&maximumRecords=10&query="

        self.assertEqual(actual_query, expected_query)

    def test_format_search_retrieve_query_no_default_record_schema_or_user_defined_record_schema(self):
        sru_configuration = get_gapines_sru_configuration()
        sru_configuration.search_retrieve_url = "https://example.com"
        sru_configuration.sru_version = "1.1"
        sru_configuration.default_record_schema = None

        actual_query = SRUAuxiliaryFormatter.format_base_search_retrieve_query(sru_configuration,
            start_record=1, maximum_records=10)

        expected_query = "https://example.com?version=1.1&operation=searchRetrieve&startRecord=1&maximumRecords=10&query="

        self.assertEqual(actual_query, expected_query)

    def test_format_search_retrieve_query_no_user_defined_start_record(self):
        sru_configuration = get_gapines_sru_configuration()
        sru_configuration.search_retrieve_url = "https://example.com"
        sru_configuration.sru_version = "1.1"

        actual_query = SRUAuxiliaryFormatter.format_base_search_retrieve_query(sru_configuration, maximum_records=10)

        expected_query = "https://example.com?version=1.1&operation=searchRetrieve&recordSchema=marcxml&maximumRecords=10&query="

        self.assertEqual(actual_query, expected_query)

    def test_format_search_retrieve_query_no_user_defined_maximum_record_default_maximum_record(self):
        sru_configuration = get_gapines_sru_configuration()
        sru_configuration.search_retrieve_url = "https://example.com"
        sru_configuration.sru_version = "1.1"

        actual_query = SRUAuxiliaryFormatter.format_base_search_retrieve_query(sru_configuration)

        expected_query = "https://example.com?version=1.1&operation=searchRetrieve&recordSchema=marcxml&maximumRecords=10&query="

        self.assertEqual(actual_query, expected_query)

    def test_format_search_retrieve_query_no_user_defined_maximum_record_no_default_maximum_record(self):
        sru_configuration = get_gapines_sru_configuration()
        sru_configuration.search_retrieve_url = "https://example.com"
        sru_configuration.sru_version = "1.1"
        sru_configuration.default_records_returned = None

        actual_query = SRUAuxiliaryFormatter.format_base_search_retrieve_query(sru_configuration)

        expected_query = "https://example.com?version=1.1&operation=searchRetrieve&recordSchema=marcxml&query="

        self.assertEqual(actual_query, expected_query)

    def test_format_search_retrieve_query_record_packing(self):
        sru_configuration = get_alma_sru_configuration()
        sru_configuration.search_retrieve_url = "https://example.com"
        sru_configuration.sru_version = "1.1"
        sru_configuration.default_records_returned = None

        actual_query = SRUAuxiliaryFormatter.format_base_search_retrieve_query(sru_configuration, record_packing="xml")

        expected_query = "https://example.com?version=1.1&operation=searchRetrieve&recordPacking=xml&query="

        self.assertEqual(actual_query, expected_query)

    def test_format_sort_query(self):
        actual_search_retrieve_query = SRUAuxiliaryFormatter.format_sort_query(
            sort_queries=[{"index_set": "alma", "index_name": "bib_holding_count", "sort_order": "ascending"}])
        expected_search_retrieve_query = "%20sortBy%20alma.bib_holding_count/sort.ascending"

        self.assertEqual(actual_search_retrieve_query,
                         expected_search_retrieve_query)

    def test_format_sort_query_two_indexes(self):
        actual_search_retrieve_query = SRUAuxiliaryFormatter.format_sort_query(
            sort_queries=[{"index_set": "alma", "index_name": "bib_holding_count", "sort_order": "ascending"}, {"index_set": "alma", "index_name": "title", "sort_order": "descending"}])
        expected_search_retrieve_query = "%20sortBy%20alma.bib_holding_count/sort.ascending%20alma.title/sort.descending"

        self.assertEqual(actual_search_retrieve_query,
                         expected_search_retrieve_query)