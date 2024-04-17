import unittest
import xmltodict
import json
from unittest.mock import patch

from src.sru_queryer._base._sru_explain_xml_parser import SRUExplainXMLParser
from tests.testData.test_data import TestFiles, test_available_record_schemas, mock_searchable_indexes_and_descriptions

from src.sru_queryer.drivers import alma_driver, loc_driver, gapines_driver

# Format returned by SRUExplainXMLParser's '_parse_config_info'
gapines_test_parsed_config_info = {
    "default_context_set": "eg",
    "default_index": "keyword",
    "default_relation": "all",
    "default_record_schema": "marcxml",
    "default_sort_schema": "marcxml",
    "default_records_returned": 10,
    "max_records_supported": 50,
    "supported_relation_modifiers": ["relevant", "stem", "fuzzy", "word"]
}
alma_test_parsed_config_info = {
    "default_context_set": None,
    "default_index": None,
    "default_relation": None,
    "default_record_schema": None,
    "default_sort_schema": None,
    "default_records_returned": 10,
    "max_records_supported": 50,
    "supported_relation_modifiers": []
}

class TestSRUExplainXMLParser(unittest.TestCase):

    def test_parse_context_set_and_index_info_from_xml_alma(self):
        with open (TestFiles.explain_response_alma, "rb") as f:

            xml_unprocessed_dict = xmltodict.parse(f.read())

            sru_xml_parser = SRUExplainXMLParser(xml_unprocessed_dict, driver=alma_driver)
            xml_dict = sru_xml_parser._parse_raw_index_info_from_xml()

            with open (TestFiles.alma_raw_indexes, "r") as f:
                expected_dict = json.loads(f.read())

                self.assertListEqual(xml_dict, expected_dict)

    def test_parse_context_set_and_index_info_from_xml_loc(self):
        with open (TestFiles.explain_response_loc, "rb") as f:

            xml_unprocessed_dict = xmltodict.parse(f.read())

            sru_xml_parser = SRUExplainXMLParser(xml_unprocessed_dict, driver=loc_driver)
            xml_dict = sru_xml_parser._parse_raw_index_info_from_xml()

            with open (TestFiles.loc_raw_indexes, "r") as f:
                expected_dict = json.loads(f.read())

                self.assertListEqual(xml_dict, expected_dict)

    def test_parse_context_set_and_index_info_from_xml_gapines(self):
        with open (TestFiles.explain_response_gapines, "rb") as f:

            xml_unprocessed_dict = xmltodict.parse(f.read())

            sru_xml_parser = SRUExplainXMLParser(xml_unprocessed_dict, driver=gapines_driver)
            xml_dict = sru_xml_parser._parse_raw_index_info_from_xml()

            with open (TestFiles.gapines_raw_indexes, "r") as f:
                expected_dict = json.loads(f.read())

                self.assertListEqual(xml_dict, expected_dict)

    def test_parse_schema_info_from_xml_gapines(self):
        with open (TestFiles.explain_response_gapines, "rb") as f:

            xml_unprocessed_dict = xmltodict.parse(f.read())

            sru_xml_parser = SRUExplainXMLParser(xml_unprocessed_dict, driver=gapines_driver)
            xml_dict = sru_xml_parser._parse_raw_schema_info_from_xml()
            xml_dict = sru_xml_parser._parse_schema_info(xml_dict)

    def test_parse_schema_info_from_xml_alma(self):
        with open (TestFiles.explain_response_alma, "rb") as f:

            xml_unprocessed_dict = xmltodict.parse(f.read())

            sru_xml_parser = SRUExplainXMLParser(xml_unprocessed_dict, driver=alma_driver)
            xml_dict = sru_xml_parser._parse_raw_schema_info_from_xml()

            with open (TestFiles.alma_raw_schemas, "r") as f:
                expected_dict = json.loads(f.read())

                self.assertListEqual(xml_dict, expected_dict)

    def test_parse_schema_info_from_xml_loc(self):
        with open (TestFiles.explain_response_loc, "rb") as f:

            xml_unprocessed_dict = xmltodict.parse(f.read())

            sru_xml_parser = SRUExplainXMLParser(xml_unprocessed_dict, driver=loc_driver)
            xml_dict = sru_xml_parser._parse_raw_schema_info_from_xml()

            with open (TestFiles.loc_raw_schemas, "r") as f:
                expected_dict = json.loads(f.read())

                self.assertListEqual(xml_dict, expected_dict)

    def test_parse_config_info_from_xml_alma(self):
        with open (TestFiles.explain_response_alma, "rb") as f:

            xml_unprocessed_dict = xmltodict.parse(f.read())

            sru_xml_parser = SRUExplainXMLParser(xml_unprocessed_dict, driver=alma_driver)
            xml_dict = sru_xml_parser._parse_raw_config_info_from_xml()

            with open (TestFiles.alma_raw_config_info, "r") as f:
                expected_dict = json.loads(f.read())

                self.assertDictEqual(xml_dict, expected_dict)

    def test_parse_config_info_from_xml_alma(self):
        with open (TestFiles.explain_response_loc, "rb") as f:

            xml_unprocessed_dict = xmltodict.parse(f.read())

            sru_xml_parser = SRUExplainXMLParser(xml_unprocessed_dict, driver=loc_driver)
            xml_dict = sru_xml_parser._parse_raw_config_info_from_xml()

            self.assertIsNone(xml_dict)

    def test_parse_config_info_from_xml_gapines(self):
        with open (TestFiles.explain_response_gapines, "rb") as f:

            xml_unprocessed_dict = xmltodict.parse(f.read())

            sru_xml_parser = SRUExplainXMLParser(xml_unprocessed_dict, driver=gapines_driver)
            xml_dict = sru_xml_parser._parse_raw_config_info_from_xml()

            with open (TestFiles.gapines_raw_config_info, "r") as f:
                expected_dict = json.loads(f.read())

                self.assertDictEqual(xml_dict, expected_dict)

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

    def test_parse_available_context_set_and_index_info_from_xml_dict_alma(self):
        with open (TestFiles.alma_raw_indexes, "r") as f:
            explain_index_json = json.loads(f.read())

            sru_xml_parser = SRUExplainXMLParser({}, driver=alma_driver)
            available_context_set_and_index_info = sru_xml_parser._parse_available_context_sets_and_index_info(explain_index_json)
            
            self.verify_index_config_info(available_context_set_and_index_info["alma"]["bib_level"], {
                "id": None,
                "title": "Bibliographic Level",
                "sort": False,
                "supported_operations": ["==", "<>", "=", "all"],
                "empty_term_supported": True
            })

            self.verify_index_config_info(available_context_set_and_index_info["alma"]["serviceType"], {
                "id": None,
                "title": "Service Type",
                "sort": False,
                "supported_operations": ["==", "<>", "=", "all"],
                "empty_term_supported": True
            })

            self.verify_index_config_info(available_context_set_and_index_info["alma"]["main_pub_date"], {
                "id": None,
                "title": "Publication Year",
                "sort": True,
                "supported_operations": ["==", ">", ">=", "<", "<=", "<>", "=", "all"],
                "empty_term_supported": False
            })
    
    def test_parse_available_context_set_and_index_info_from_xml_dict_alma_different_set(self):
        with open (TestFiles.alma_raw_indexes, "r") as f:
            explain_index_json = json.loads(f.read())

            sru_xml_parser = SRUExplainXMLParser({}, driver=alma_driver)
            available_context_set_and_index_info = sru_xml_parser._parse_available_context_sets_and_index_info(explain_index_json)

            index = available_context_set_and_index_info["rec"]["id"]
            expected_index = self.create_index_config("Record Identifier (MMS ID)", None, False, ["==", ">", ">=", "<", "<=", "<>", "=", "all"], False)

            self.verify_index_config_info(index, expected_index)

    def test_parse_available_context_set_and_index_info_from_xml_dict_gapines(self):
        with open(TestFiles.gapines_raw_indexes, "r") as f:
            explain_index_json = json.loads(f.read())

            sru_xml_parser = SRUExplainXMLParser({}, driver=gapines_driver)
            available_context_set_and_index_info = sru_xml_parser._parse_available_context_sets_and_index_info(explain_index_json)

            index = available_context_set_and_index_info["bib"]["nameconference"]
            expected_index = self.create_index_config(title="nameconference", id="bib.nameconference", sort=None, supported_operations=[], empty_term_supported=None)

            self.verify_index_config_info(index, expected_index=expected_index)

    def test_parse_available_context_set_and_index_info_from_xml_dict_loc(self):
        with open(TestFiles.loc_raw_indexes, "r") as f:
            explain_index_json = json.loads(f.read())

            sru_xml_parser = SRUExplainXMLParser({}, driver=loc_driver)
            available_context_set_and_index_info = sru_xml_parser._parse_available_context_sets_and_index_info(explain_index_json)

            index = available_context_set_and_index_info["cql"]["anywhere"]
            expected_index = self.create_index_config("Keyword Anywhere", "1016", None, [], None)

            self.verify_index_config_info(index, expected_index=expected_index)

    def test_parse_config_info_alma(self):
        with open(TestFiles.alma_raw_config_info, "r") as f:
            explain_index_json = json.loads(f.read())

            sru_xml_parser = SRUExplainXMLParser({}, driver=alma_driver)
            config_info = sru_xml_parser._parse_config_info(explain_index_json)

            self.assertDictEqual(config_info, alma_test_parsed_config_info)

    def test_parse_config_info_gapines(self):
        with open(TestFiles.gapines_raw_config_info, "r") as f:
            explain_index_json = json.loads(f.read())

            sru_xml_parser = SRUExplainXMLParser({}, driver=gapines_driver)
            config_info = sru_xml_parser._parse_config_info(explain_index_json)

            self.assertDictEqual(config_info, gapines_test_parsed_config_info)

    def test_parse_config_info_loc(self):
        sru_xml_parser = SRUExplainXMLParser({}, driver=loc_driver)
        config_info = sru_xml_parser._parse_config_info(None)

        self.assertIsNone(config_info)

    def test_parse_schema_info_alma(self):
        with open(TestFiles.alma_raw_schemas, "r") as f:
            record_schema_info = json.loads(f.read())

            sru_xml_parser = SRUExplainXMLParser({}, driver=alma_driver)

            parsed_record_schema_info = sru_xml_parser._parse_schema_info(record_schema_info)

            parsed_stringified_available_record_schemas = json.dumps(parsed_record_schema_info)
            for record_schema in test_available_record_schemas:
                stringified_record_schema = json.dumps(record_schema)
                self.assertTrue(stringified_record_schema in parsed_stringified_available_record_schemas)

            self.assertEqual(len(parsed_record_schema_info), 16)

    def test_parse_schema_info_loc(self):
        with open(TestFiles.loc_raw_schemas, "r") as f:
            record_schema_info = json.loads(f.read())

            sru_xml_parser = SRUExplainXMLParser({}, driver=loc_driver)

            parsed_record_schema_info = sru_xml_parser._parse_schema_info(record_schema_info)

            self.assertEqual(len(parsed_record_schema_info), 8)

    @patch('src.sru_queryer._base._sru_explain_xml_parser.SRUExplainXMLParser._parse_raw_index_info_from_xml')
    @patch('src.sru_queryer._base._sru_explain_xml_parser.SRUExplainXMLParser._parse_raw_schema_info_from_xml')
    @patch('src.sru_queryer._base._sru_explain_xml_parser.SRUExplainXMLParser._parse_raw_config_info_from_xml')
    @patch('src.sru_queryer._base._sru_explain_xml_parser.SRUExplainXMLParser._parse_schema_info')
    @patch('src.sru_queryer._base._sru_explain_xml_parser.SRUExplainXMLParser._parse_available_context_sets_and_index_info')
    @patch('src.sru_queryer._base._sru_explain_xml_parser.SRUExplainXMLParser._parse_config_info')
    def test_construct_sru_configuration_alma(self, mock_parse_config_info, mock_parse_index_info, mock_parse_schema_info, *args):
        mock_parse_config_info.return_value = alma_test_parsed_config_info
        # The following two mock values aren't exactly what Alma returns, but should approximate it.
        mock_parse_index_info.return_value = mock_searchable_indexes_and_descriptions
        mock_parse_schema_info.return_value = test_available_record_schemas

        sru_xml_parser = SRUExplainXMLParser({}, driver=alma_driver)

        configuration = sru_xml_parser.get_sru_configuration_from_explain_response()

        self.assertDictEqual(configuration.available_context_sets_and_indexes, mock_searchable_indexes_and_descriptions)
        self.assertDictEqual(configuration.available_record_schemas, test_available_record_schemas)
        self.assertListEqual(configuration.supported_relation_modifiers, [])
        self.assertEqual(configuration.default_context_set, None)
        self.assertEqual(configuration.default_index, None)
        self.assertEqual(configuration.default_relation, None)
        self.assertEqual(configuration.default_record_schema, None)
        self.assertEqual(configuration.default_sort_schema, None)
        self.assertEqual(configuration.default_records_returned, 10)
        self.assertEqual(configuration.max_records_supported, 50)

    @patch('src.sru_queryer._base._sru_explain_xml_parser.SRUExplainXMLParser._parse_raw_index_info_from_xml')
    @patch('src.sru_queryer._base._sru_explain_xml_parser.SRUExplainXMLParser._parse_raw_schema_info_from_xml')
    @patch('src.sru_queryer._base._sru_explain_xml_parser.SRUExplainXMLParser._parse_raw_config_info_from_xml')
    @patch('src.sru_queryer._base._sru_explain_xml_parser.SRUExplainXMLParser._parse_schema_info')
    @patch('src.sru_queryer._base._sru_explain_xml_parser.SRUExplainXMLParser._parse_available_context_sets_and_index_info')
    @patch('src.sru_queryer._base._sru_explain_xml_parser.SRUExplainXMLParser._parse_config_info')
    def test_construct_sru_configuration_gapines_config_info(self, mock_parse_config_info, mock_parse_index_info, mock_parse_schema_info, *args):
        # Only tests properly parsing the Gapines CONFIG info. Other stuff is
        # simply there to allow the test to work
        mock_parse_config_info.return_value = gapines_test_parsed_config_info
        mock_parse_index_info.return_value = mock_searchable_indexes_and_descriptions
        mock_parse_schema_info.return_value = test_available_record_schemas

        sru_xml_parser = SRUExplainXMLParser({}, driver=gapines_driver)

        configuration = sru_xml_parser.get_sru_configuration_from_explain_response()

        self.assertListEqual(configuration.supported_relation_modifiers, ["relevant", "stem", "fuzzy", "word"])
        self.assertEqual(configuration.default_context_set, "eg")
        self.assertEqual(configuration.default_index, "keyword")
        self.assertEqual(configuration.default_relation, "all")
        self.assertEqual(configuration.default_record_schema, "marcxml")
        self.assertEqual(configuration.default_sort_schema, "marcxml")
        self.assertEqual(configuration.default_records_returned, 10)
        self.assertEqual(configuration.max_records_supported, 50)

    def test_construct_sru_configuration_integration_alma(self):
        with open(TestFiles.explain_response_alma, "rb") as f:
            xml_dict = xmltodict.parse(f.read())
            sru_xml_parser = SRUExplainXMLParser(xml_dict, driver=alma_driver)
            configuration = sru_xml_parser.get_sru_configuration_from_explain_response()

            # Check if each record schema is in the parsed record schemas
            # (The test_available_record_schemas are a subset of what's included in 
            # explain_response_alma)
            parsed_stringified_available_record_schemas = json.dumps(configuration.available_record_schemas)
            for record_schema in test_available_record_schemas:
                stringified_record_schema = json.dumps(record_schema)
                self.assertTrue(stringified_record_schema in parsed_stringified_available_record_schemas)

            self.assertListEqual(configuration.supported_relation_modifiers, [])
            self.assertEqual(configuration.default_context_set, None)
            self.assertEqual(configuration.default_index, None)
            self.assertEqual(configuration.default_relation, None)
            self.assertEqual(configuration.default_record_schema, None)
            self.assertEqual(configuration.default_sort_schema, None)
            self.assertEqual(configuration.default_records_returned, 10)
            self.assertEqual(configuration.max_records_supported, 50)

            with open(TestFiles.alma_available_context_sets_and_indexes, "r") as f2:
                expected_indexes = json.loads(f2.read())

                self.assertDictEqual(configuration.available_context_sets_and_indexes, expected_indexes)

    def test_construct_sru_configuration_integration_gapines(self):
        with open(TestFiles.explain_response_gapines, "rb") as f:
            with open(TestFiles.gapines_available_context_sets_and_indexes, "r") as f2:
                expected_indexes = json.loads(f2.read())

                xml_dict = xmltodict.parse(f.read())
                sru_xml_parser = SRUExplainXMLParser(xml_dict, driver=gapines_driver)
                configuration = sru_xml_parser.get_sru_configuration_from_explain_response()

                self.assertDictEqual({'marcxml': {'sort': True}, 'info:srw/schema/1/marcxml-v1.1': {'sort': True}}, configuration.available_record_schemas)
                self.assertDictEqual(configuration.available_context_sets_and_indexes, expected_indexes)
                self.assertListEqual(configuration.supported_relation_modifiers, ["relevant", "stem", "fuzzy", "word"])
                self.assertEqual(configuration.default_context_set, "eg")
                self.assertEqual(configuration.default_index, "keyword")
                self.assertEqual(configuration.default_relation, "all")
                self.assertEqual(configuration.default_record_schema, "marcxml")
                self.assertEqual(configuration.default_sort_schema, "marcxml")
                self.assertEqual(configuration.default_records_returned, 10)
                self.assertEqual(configuration.max_records_supported, 50)

    def test_construct_sru_configuration_integration_loc(self):
        with open(TestFiles.explain_response_loc, "rb") as f:
            xml_dict = xmltodict.parse(f.read())
            sru_xml_parser = SRUExplainXMLParser(xml_dict, driver=loc_driver)
            configuration = sru_xml_parser.get_sru_configuration_from_explain_response()

            stringified_available_record_schemas = json.dumps(configuration.available_record_schemas)
            self.assertTrue(json.dumps({"marcxml": {"sort": False}}).strip("{}") in stringified_available_record_schemas)
            self.assertTrue(json.dumps({"http://www.loc.gov/MARC21/slim": {"sort": False}}).strip("{}") in stringified_available_record_schemas)

            self.assertListEqual(configuration.supported_relation_modifiers, [])
            self.assertEqual(configuration.default_context_set, None)
            self.assertEqual(configuration.default_index, None)
            self.assertEqual(configuration.default_relation, None)
            self.assertEqual(configuration.default_record_schema, None)
            self.assertEqual(configuration.default_sort_schema, None)
            self.assertEqual(configuration.default_records_returned, None)
            self.assertEqual(configuration.max_records_supported, None)

            with open (TestFiles.loc_available_context_sets_and_indexes, "r") as f:
                expected_indexes = json.loads(f.read())

                self.assertEqual(configuration.available_context_sets_and_indexes, expected_indexes)