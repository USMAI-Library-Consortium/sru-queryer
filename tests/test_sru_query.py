from unittest.mock import patch
import unittest
from requests import Request

from src.sru_queryer import Query
from src.sru_queryer.sru import SRUUtil
from src.sru_queryer.cql import IndexQuery
from src.sru_queryer.cql import AND, OR, LITERAL
from src.sru_queryer.sru import SortKey
from tests.testData.test_data import TestFiles, get_alma_sru_configuration
from src.sru_queryer.drivers import gapines_driver, alma_driver, loc_driver


class TestSRUQuery(unittest.TestCase):

    def test_construct_request(self):
        sru_configuration = get_alma_sru_configuration()
        sru_configuration.search_retrieve_url = "https://example.com"
        sru_configuration.sru_version = "1.2"
        sru_configuration.default_records_returned = None

        constructed_search_retrieve_request = Query(sru_configuration, IndexQuery("alma", "bib_holding_count", "==", "10"), record_schema="marcxml").construct_request()

        expected_request = Request(
            "GET", f'https://example.com?version=1.2&operation=searchRetrieve&recordSchema=marcxml&query=alma.bib_holding_count==%2210%22').prepare()

        self.assertEqual(
            constructed_search_retrieve_request.method, expected_request.method)
        self.assertEqual(
            constructed_search_retrieve_request.url, expected_request.url)
        self.assertEqual(
            constructed_search_retrieve_request.headers, expected_request.headers)

    def test_construct_request_complex(self):
        sru_configuration = get_alma_sru_configuration()
        sru_configuration.search_retrieve_url = "https://example.com"
        sru_configuration.sru_version = "1.2"
        sru_configuration.default_records_returned = None
        sru_configuration.default_record_schema = "marcxml"

        constructed_search_retrieve_request = Query(sru_configuration, AND(
            IndexQuery("alma", "bib_holding_count", ">", "15"),
            IndexQuery("rec", "mms_id",  "==", "112233")
        )).construct_request()

        expected_request = Request(
            "GET", f'https://example.com/?version=1.2&operation=searchRetrieve&recordSchema=marcxml&query=alma.bib_holding_count%3E%2215%22%20and%20rec.mms_id==%22112233%22').prepare()

        self.assertEqual(
            constructed_search_retrieve_request.method, expected_request.method)
        self.assertEqual(
            constructed_search_retrieve_request.url, expected_request.url)
        self.assertEqual(
            constructed_search_retrieve_request.headers, expected_request.headers)

    def test_construct_request_with_credentials(self):
        sru_configuration = get_alma_sru_configuration()
        sru_configuration.search_retrieve_url = "https://example.com"
        sru_configuration.sru_version = "1.2"
        sru_configuration.default_records_returned = None
        sru_configuration.username = "test_user"
        sru_configuration.password = "test_password"

        constructed_search_retrieve_request = Query(sru_configuration, AND(
            IndexQuery("alma", "bib_holding_count", ">", "15"),
            IndexQuery("rec", "mms_id",  "==", "112233")
        ), record_schema="marcxml").construct_request()

        credentials_encoded = "dGVzdF91c2VyOnRlc3RfcGFzc3dvcmQ="
        expected_request = Request(
            "GET", f'https://example.com/?version=1.2&operation=searchRetrieve&recordSchema=marcxml&query=alma.bib_holding_count%3E%2215%22%20and%20rec.mms_id==%22112233%22', headers={
                "Authorization": f'Basic {credentials_encoded}'
            })

        self.assertEqual(
            constructed_search_retrieve_request.method, expected_request.method)
        self.assertEqual(
            constructed_search_retrieve_request.url, expected_request.url)
        self.assertEqual(
            constructed_search_retrieve_request.headers, expected_request.headers)

    def test_construct_request_with_sort_by(self):
        sru_configuration = get_alma_sru_configuration()
        sru_configuration.search_retrieve_url = "https://example.com"
        sru_configuration.sru_version = "1.2"
        sru_configuration.default_records_returned = None

        constructed_search_retrieve_request = Query(sru_configuration,
                                                    IndexQuery("alma", "bib_holding_count", "==", '10'), record_schema="marcxml", sort_queries=[{"index_set": "alma", "index_name": "bib_holding_count", "sort_order": "ascending"}, {"index_set": "alma", "index_name": "title", "sort_order": "descending"}]).construct_request()

        expected_request = Request(
            "GET", f'https://example.com/?version=1.2&operation=searchRetrieve&recordSchema=marcxml&query=alma.bib_holding_count==%2210%22%20sortBy%20alma.bib_holding_count/sort.ascending%20alma.title/sort.descending')

        self.assertEqual(
            constructed_search_retrieve_request.method, expected_request.method)
        self.assertEqual(
            constructed_search_retrieve_request.url, expected_request.url)
        self.assertEqual(
            constructed_search_retrieve_request.headers, expected_request.headers)

    def test_validate_query_with_base_query_error(self):
        sru_configuration = get_alma_sru_configuration()
        sru_configuration.search_retrieve_url = "https://example.com"
        sru_configuration.sru_version = "1.2"
        sru_configuration.default_records_returned = None

        with self.assertRaises(ValueError) as ve:
            Query(sru_configuration, IndexQuery("alma", "bib_holding_count", "==", "10"), record_schema='fakefake').validate()

        self.assertIn("'fakefake'", ve.exception.__str__())
        self.assertIn("not available", ve.exception.__str__())

    def test_validate_query_with_index_error_raises_error_query(self):
        """Integration Test"""
        sru_configuration = get_alma_sru_configuration()
        sru_configuration.search_retrieve_url = "https://example.com"
        sru_configuration.sru_version = "1.2"
        sru_configuration.default_records_returned = None

        with self.assertRaises(ValueError) as ve:
            Query(sru_configuration, IndexQuery(
                "alma", "fake_index", "==", "10"), record_schema="marcxml").validate()

        self.assertIn("'fake_index'", ve.exception.__str__())
                
class TestQueryWithXMLData(unittest.TestCase):
    @patch("src.sru_queryer._base._sru_util.requests.get")
    def test_construct_request_gapines_data_default_schema_returned_by_explain(self, mock_get):
        """Integration"""
        with open(TestFiles.explain_response_gapines, "rb") as f:
            mock_get.return_value.content = f.read()

            # Initialize the gapines configuration
            sru_configuration = SRUUtil.create_configuration_for_server("https://example.com", "https://example.com", sru_version="1.1", driver=gapines_driver)

            constructed_search_retrieve_request = Query(sru_configuration, IndexQuery("alma", "bib_holding_count", "==", "10")).construct_request()

            expected_request = Request(
                "GET", f'https://example.com?version=1.1&operation=searchRetrieve&recordSchema=marcxml&maximumRecords=10&query=alma.bib_holding_count==%2210%22').prepare()
            
            self.assertEqual(
                constructed_search_retrieve_request.url, expected_request.url)
            
    @patch("src.sru_queryer._base._sru_util.requests.get")
    def test_initialize_1_2_query_with_invalid_sort_type_raises_error(self, mock_get):
         with open(TestFiles.explain_response_gapines, "rb") as f:
            mock_get.return_value.content = f.read()

            with self.assertRaises(ValueError) as ve:
                sru_configuration = SRUUtil.create_configuration_for_server("https://example.com", "https://example.com", sru_version="1.2", driver=gapines_driver)
                Query(sru_configuration, IndexQuery(value="dummyval"), record_schema="marcxml", sort_queries=[SortKey("example_xpath")])

            self.assertIn("SortKeys", ve.exception.__str__())
            self.assertIn("1.2", ve.exception.__str__())

    @patch("src.sru_queryer._base._sru_util.requests.get")
    def test_initialize_1_1_query_with_invalid_sort_type_raises_error(self, mock_get):
        with open(TestFiles.explain_response_gapines, "rb") as f:
            mock_get.return_value.content = f.read()

            with self.assertRaises(ValueError) as ve:
                sru_configuration = SRUUtil.create_configuration_for_server("https://example.com", "https://example.com", sru_version="1.1", driver=gapines_driver)
                Query(sru_configuration, IndexQuery(value="dummyval"), sort_queries=[{"index_set": "alma", "index_name": "bib_holding_count", "sort_order": "ascending"}])
            
            self.assertIn("SortKeys", ve.exception.__str__())
            self.assertIn("1.1", ve.exception.__str__())

    @patch('src.sru_queryer._base._sru_util.requests.get')
    def test_initialize_and_format_base_query_no_schema_no_error(self, mock_get):
        """Integration"""
        with open(TestFiles.explain_response_loc, "rb") as f:
            mock_get.return_value.content = f.read()

            sru_configuration = SRUUtil.create_configuration_for_server("https://example.com", "https://example2.com", sru_version="1.1", driver=loc_driver)

            Query(sru_configuration, LITERAL("pass")).validate()
    
    @patch('src.sru_queryer._base._sru_util.requests.get')
    def test_initialize_query_default_schema_raises_no_error(self, mock_get):
        """Integration"""
        with open(TestFiles.explain_response_gapines, "rb") as f:
            mock_get.return_value.content = f.read() 

            sru_configuration = SRUUtil.create_configuration_for_server("https://example.com", "https://example2.com", sru_version="1.1", driver=gapines_driver)

            Query(sru_configuration, LITERAL("pass"))
