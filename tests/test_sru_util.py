import unittest
from unittest.mock import patch

from src.sru_queryer.sru import SRUUtil
from tests.testData.test_data import get_alma_sru_configuration, get_gapines_sru_configuration, mock_searchable_indexes_and_descriptions

@patch("src.sru_queryer.sru.SRUUtil._retrieve_explain_response_xml")
@patch("src.sru_queryer.sru.SRUUtil._parse_explain_response_configuration")
class TestSRUUtilCreateConfiguration(unittest.TestCase):

    def test_merge_config_and_user_settings_urls_set_correctly(self, mock_parse_explain_response, *args):
        mock_parse_explain_response.return_value = get_alma_sru_configuration()

        updated_config = SRUUtil.create_configuration_for_server("testurl2.com", "testurl.com")

        self.assertEqual(updated_config.explain_url, "testurl2.com")
        self.assertEqual(updated_config.search_retrieve_url, "testurl.com")

    def test_merge_config_and_user_settings_version_set_correctly(self, mock_parse_explain_response, *args):
        mock_parse_explain_response.return_value = get_alma_sru_configuration()

        updated_config = SRUUtil.create_configuration_for_server("testurl2.com", "testurl.com", sru_version="1.1")

        self.assertEqual(updated_config.sru_version, "1.1")

    def test_merge_config_and_user_settings_set_record_numbers_returned_correctly(self, mock_parse_explain_response, *args):
        mock_parse_explain_response.return_value = get_alma_sru_configuration()

        updated_config = SRUUtil.create_configuration_for_server("testurl2.com", "testurl.com", default_records_returned=15, max_records_supported=40)

        self.assertEqual(updated_config.default_records_returned, 15)
        self.assertEqual(updated_config.max_records_supported, 40)

    def test_merge_config_and_user_settings_set_username_password_returned_correctly(self, mock_parse_explain_response, *args):
        mock_parse_explain_response.return_value = get_alma_sru_configuration()

        updated_config = SRUUtil.create_configuration_for_server("testurl2.com", "testurl.com", username="testusername", password="testpassword")

        self.assertEqual(updated_config.username, "testusername")
        self.assertEqual(updated_config.password, "testpassword")

    def test_merge_config_and_user_settings_set_cql_defaults_returned_correctly(self, mock_parse_explain_response, *args):
        mock_parse_explain_response.return_value = get_alma_sru_configuration()

        updated_config = SRUUtil.create_configuration_for_server("testurl2.com", "testurl.com", default_cql_context_set="alma", default_cql_index="all_for_ui", default_cql_relation="all")

        self.assertEqual(updated_config.default_context_set, "alma")
        self.assertEqual(updated_config.default_index, "all_for_ui")
        self.assertEqual(updated_config.default_relation, "all")

    def test_merge_config_and_user_settings_set_default_schemas_returned_correctly(self, mock_parse_explain_response, *args):
        mock_parse_explain_response.return_value = get_alma_sru_configuration()

        updated_config = SRUUtil.create_configuration_for_server("testurl2.com", "testurl.com", default_record_schema="marcxml", default_sort_schema="marcxml")

        self.assertEqual(updated_config.default_record_schema, "marcxml")
        self.assertEqual(updated_config.default_sort_schema, "marcxml")

    def test_merge_config_and_user_settings_set_disable_validation_for_cql_defaults_returned_correctly(self, mock_parse_explain_response, *args):
        mock_parse_explain_response.return_value = get_alma_sru_configuration()

        updated_config = SRUUtil.create_configuration_for_server("testurl2.com", "testurl.com", disable_validation_for_cql_defaults=True)

        self.assertEqual(updated_config.disable_validation_for_cql_defaults, True)

    def test_merge_config_and_user_settings_full_configuration_no_user_changes_stays_original(self, mock_parse_explain_response, *args):
        configuration_parsed_from_explain_response = get_gapines_sru_configuration()
        mock_parse_explain_response.return_value = configuration_parsed_from_explain_response

        updated_config = SRUUtil.create_configuration_for_server("testurl2.com", "testurl.com")

        self.assertEqual(updated_config.disable_validation_for_cql_defaults, False)
        self.assertEqual(updated_config.default_context_set, "eg")
        self.assertEqual(updated_config.default_index, "keyword")
        self.assertEqual(updated_config.default_relation, "all")
        self.assertEqual(updated_config.default_record_schema, "marcxml")
        self.assertEqual(updated_config.default_sort_schema, "marcxml")
        self.assertEqual(updated_config.default_records_returned, 10)
        self.assertEqual(updated_config.max_records_supported, 50)

    @staticmethod
    def create_index_config(title, id, sort, supported_operations, empty_term_supported) -> dict:
        return {
                "id": id,
                "title": title,
                "sort": sort,
                "supported_operations": supported_operations,
                "empty_term_supported": empty_term_supported
    }

    def verify_index_config_info(self, index, expected_index):
        self.assertEqual(index["title"], expected_index["title"], "Title Incorrect!")
        self.assertEqual(index["id"], expected_index["id"], "ID Incorrect! ")
        self.assertEqual(index["sort"], expected_index["sort"], "Sort Incorrect!")
        self.assertListEqual(index["supported_operations"], expected_index["supported_operations"], "Supported Operations incorrect!")
        self.assertEqual(index["empty_term_supported"], expected_index["empty_term_supported"], "Empty Term Supported Incorrect!")


    def test_filter_available_context_sets_and_indexes_different_capitalization(self, *args):
        filtered_dict = SRUUtil._filter_available_context_sets_and_indexes(
            mock_searchable_indexes_and_descriptions, title="library")

        self.assertDictEqual(filtered_dict, {
            "alma": {
                "library": {
                    "id": None,
                    "title": "Library Code",
                    "sort": False,
                    "supported_operations": ["==", "all"],
                    "empty_term_supported": True
                },
                "library_status": {
                    "id": None,
                    "title": "Library Status",
                    "sort": False,
                    "supported_operations": ["==", "all"],
                    "empty_term_supported": True
                },
            },
        })

    def test_filter_available_context_sets_and_indexes_different_set(self, *args):
        filtered_dict = SRUUtil._filter_available_context_sets_and_indexes(
            mock_searchable_indexes_and_descriptions, title="mms")
        
        expected_index = self.create_index_config("Bib MMS ID", None, False, ["==", "all"], True)

        self.verify_index_config_info(filtered_dict["rec"]["mms_id"], expected_index)


    def test_filter_available_context_sets_and_indexes_two_sets(self, *args):
        filtered_dict = SRUUtil._filter_available_context_sets_and_indexes(
            mock_searchable_indexes_and_descriptions, title="bib")

        self.assertDictEqual(filtered_dict, {
            "alma": {
                "bib_holding_count": {
                    "id": None,
                    "title": "Bib Holding Count (Alma)",
                    "sort": True,
                    "supported_operations": [">", ">=", "==", "<", "<="],
                    "empty_term_supported": True
                },
            },
            "rec": {
                "mms_id": {
                    "id": None,
                    "title": "Bib MMS ID",
                    "sort": False,
                    "supported_operations": ["==", "all"],
                    "empty_term_supported": True
                },
            },
        })

