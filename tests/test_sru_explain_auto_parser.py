import unittest
import xmltodict
import json

from src.sru_queryer._base._exceptions import NoExplainResponseException
from src.sru_queryer._base._sru_explain_auto_parser import SRUExplainAutoParser
from tests.testData.test_data import TestFiles, test_available_record_schemas

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

class TestSRUExplainAutoParser(unittest.TestCase):

    def test_parse_context_set_and_index_info_from_alma(self):
        with open (TestFiles.explain_response_alma, "rb") as f:

            xml_unprocessed_dict = xmltodict.parse(f.read())

            sru_dict_parser = SRUExplainAutoParser(xml_unprocessed_dict)
            sru_configuration = sru_dict_parser.get_sru_configuration_from_explain_response()

            with open (TestFiles.alma_available_context_sets_and_indexes, "r") as f:
                expected_dict = json.loads(f.read())

            self.assertDictEqual(sru_configuration.available_context_sets_and_indexes["alma"]["accompanying_material"], expected_dict["alma"]["accompanying_material"])
            self.assertDictEqual(sru_configuration.available_context_sets_and_indexes, expected_dict)

    def test_parse_context_set_and_index_info_from_loc(self):
        with open (TestFiles.explain_response_loc, "rb") as f:

            xml_unprocessed_dict = xmltodict.parse(f.read())

            sru_dict_parser = SRUExplainAutoParser(xml_unprocessed_dict)
            sru_configuration = sru_dict_parser.get_sru_configuration_from_explain_response()

            with open (TestFiles.loc_available_context_sets_and_indexes, "r") as f:
                expected_dict = json.loads(f.read())

            self.assertDictEqual(sru_configuration.available_context_sets_and_indexes["dc"]["author"], expected_dict["dc"]["author"])
            self.assertDictEqual(sru_configuration.available_context_sets_and_indexes, expected_dict)

    def test_parse_context_set_and_index_info_from_gapines(self):
        with open (TestFiles.explain_response_gapines, "rb") as f:

            xml_unprocessed_dict = xmltodict.parse(f.read())

            sru_dict_parser = SRUExplainAutoParser(xml_unprocessed_dict)
            sru_configuration = sru_dict_parser.get_sru_configuration_from_explain_response()

            with open (TestFiles.gapines_available_context_sets_and_indexes, "r") as f:
                expected_dict = json.loads(f.read())

            self.assertDictEqual(sru_configuration.available_context_sets_and_indexes["eg"]["author"], expected_dict["eg"]["author"])
            self.assertDictEqual(sru_configuration.available_context_sets_and_indexes, expected_dict)

    def test_parse_sru_version_from_dict_alma(self):
        with open (TestFiles.explain_response_alma, "rb") as f:

            xml_unprocessed_dict = xmltodict.parse(f.read())

            sru_dict_parser = SRUExplainAutoParser(xml_unprocessed_dict)
            sc = sru_dict_parser.get_sru_configuration_from_explain_response()

            self.assertEqual(sc.sru_version, "1.2")

    def test_parse_sru_version_from_dict_loc(self):
        with open (TestFiles.explain_response_loc, "rb") as f:

            xml_unprocessed_dict = xmltodict.parse(f.read())

            sru_dict_parser = SRUExplainAutoParser(xml_unprocessed_dict)
            sc = sru_dict_parser.get_sru_configuration_from_explain_response()

            self.assertEqual(sc.sru_version, "1.1")

    def test_parse_sru_version_from_dict_gapines(self):
        with open (TestFiles.explain_response_gapines, "rb") as f:

            xml_unprocessed_dict = xmltodict.parse(f.read())

            sru_dict_parser = SRUExplainAutoParser(xml_unprocessed_dict)
            sc = sru_dict_parser.get_sru_configuration_from_explain_response()

            self.assertEqual(sc.sru_version, "1.1")

    def test_parse_config_info_alma(self):
        with open(TestFiles.explain_response_alma, "rb") as f:
            explain_response = xmltodict.parse(f.read())

            sru_dict_parser = SRUExplainAutoParser(explain_response)
            sc = sru_dict_parser.get_sru_configuration_from_explain_response()

            self.assertEqual(sc.default_context_set, alma_test_parsed_config_info["default_context_set"])
            self.assertEqual(sc.default_index, alma_test_parsed_config_info["default_index"])
            self.assertEqual(sc.default_relation, alma_test_parsed_config_info["default_relation"])
            self.assertEqual(sc.default_record_schema, alma_test_parsed_config_info["default_record_schema"])
            self.assertEqual(sc.default_records_returned, alma_test_parsed_config_info["default_records_returned"])
            self.assertEqual(sc.max_records_supported, alma_test_parsed_config_info["max_records_supported"])
            self.assertListEqual(sc.supported_relation_modifiers, alma_test_parsed_config_info["supported_relation_modifiers"])

    def test_parse_config_info_gapines(self):
        with open(TestFiles.explain_response_gapines, "rb") as f:
            explain_response = xmltodict.parse(f.read())

            sru_dict_parser = SRUExplainAutoParser(explain_response)
            sc = sru_dict_parser.get_sru_configuration_from_explain_response()

            self.assertEqual(sc.default_context_set, gapines_test_parsed_config_info["default_context_set"])
            self.assertEqual(sc.default_index, gapines_test_parsed_config_info["default_index"])
            self.assertEqual(sc.default_relation, gapines_test_parsed_config_info["default_relation"])
            self.assertEqual(sc.default_record_schema, gapines_test_parsed_config_info["default_record_schema"])
            self.assertEqual(sc.default_records_returned, gapines_test_parsed_config_info["default_records_returned"])
            self.assertEqual(sc.max_records_supported, gapines_test_parsed_config_info["max_records_supported"])
            self.assertListEqual(sc.supported_relation_modifiers, gapines_test_parsed_config_info["supported_relation_modifiers"])

    def test_parse_schema_info_alma(self):
        with open(TestFiles.explain_response_alma, "rb") as f:
            alma_dict = xmltodict.parse(f.read())

            sru_dict_parser = SRUExplainAutoParser(alma_dict)
            sc = sru_dict_parser.get_sru_configuration_from_explain_response()

            for record_schema_name in test_available_record_schemas.keys():
                self.assertTrue(record_schema_name in sc.available_record_schemas.keys(), "Parsed record schemas are missing an expected record schema.")
                self.assertDictEqual(test_available_record_schemas[record_schema_name], sc.available_record_schemas[record_schema_name], "An expected record schema does not match an actual record schema.")

            self.assertEqual(len(sc.available_record_schemas), 8)

    def test_parse_schema_info_loc(self):
        with open(TestFiles.explain_response_loc, "rb") as f:
            loc_dict = xmltodict.parse(f.read())

            sru_dict_parser = SRUExplainAutoParser(loc_dict)
            sc = sru_dict_parser.get_sru_configuration_from_explain_response()

            self.assertEqual(len(sc.available_record_schemas), 4)

    def test_bad_explain_response_loc_raises_exception(self):
        with open(TestFiles.loc_bad_explain_response, "rb") as f:
            bad_response_dict = xmltodict.parse(f.read())

            sru_dict_parser = SRUExplainAutoParser(bad_response_dict)

            with self.assertRaises(NoExplainResponseException) as e:
                sc = sru_dict_parser.get_sru_configuration_from_explain_response()

    def test_bad_explain_response_alma_raises_exception(self):
        with open(TestFiles.alma_bad_explain_response, "rb") as f:
            bad_response_dict = xmltodict.parse(f.read())

            sru_dict_parser = SRUExplainAutoParser(bad_response_dict)

            with self.assertRaises(NoExplainResponseException) as e:
                sc = sru_dict_parser.get_sru_configuration_from_explain_response()

    def test_construct_sru_configuration_integration_alma(self):
        with open(TestFiles.explain_response_alma, "rb") as f:
            xml_dict = xmltodict.parse(f.read())
            sru_dict_parser = SRUExplainAutoParser(xml_dict)
            configuration = sru_dict_parser.get_sru_configuration_from_explain_response()

            # Check if each record schema is in the parsed record schemas
            # (The test_available_record_schemas are a subset of what's included in 
            # explain_response_alma)
            for record_schema_name in test_available_record_schemas.keys():
                self.assertTrue(record_schema_name in configuration.available_record_schemas.keys(), "Parsed record schemas are missing an expected record schema.")
                self.assertDictEqual(test_available_record_schemas[record_schema_name], configuration.available_record_schemas[record_schema_name], "An expected record schema does not match an actual record schema.")

            self.assertListEqual(configuration.supported_relation_modifiers, [])
            self.assertEqual(configuration.default_context_set, None)
            self.assertEqual(configuration.default_index, None)
            self.assertEqual(configuration.default_relation, None)
            self.assertEqual(configuration.default_record_schema, None)
            self.assertEqual(configuration.default_sort_schema, None)
            self.assertEqual(configuration.default_records_returned, 10)
            self.assertEqual(configuration.max_records_supported, 50)
            self.assertEqual(configuration.sru_version, "1.2")

            with open(TestFiles.alma_available_context_sets_and_indexes, "r") as f2:
                expected_indexes = json.loads(f2.read())

                self.assertDictEqual(configuration.available_context_sets_and_indexes, expected_indexes)

    def test_construct_sru_configuration_integration_gapines(self):
        with open(TestFiles.explain_response_gapines, "rb") as f:
            with open(TestFiles.gapines_available_context_sets_and_indexes, "r") as f2:
                expected_indexes = json.loads(f2.read())

                xml_dict = xmltodict.parse(f.read())
                sru_dict_parser = SRUExplainAutoParser(xml_dict)
                configuration = sru_dict_parser.get_sru_configuration_from_explain_response()

                self.assertDictEqual({'marcxml': {'sort': True, "identifier": "info:srw/schema/1/marcxml-v1.1"}}, configuration.available_record_schemas)
                self.assertDictEqual(configuration.available_context_sets_and_indexes, expected_indexes)
                self.assertListEqual(configuration.supported_relation_modifiers, ["relevant", "stem", "fuzzy", "word"])
                self.assertEqual(configuration.default_context_set, "eg")
                self.assertEqual(configuration.default_index, "keyword")
                self.assertEqual(configuration.default_relation, "all")
                self.assertEqual(configuration.default_record_schema, "marcxml")
                self.assertEqual(configuration.default_sort_schema, "marcxml")
                self.assertEqual(configuration.default_records_returned, 10)
                self.assertEqual(configuration.max_records_supported, 50)
                self.assertEqual(configuration.sru_version, "1.1")

    def test_construct_sru_configuration_integration_loc(self):
        with open(TestFiles.explain_response_loc, "rb") as f:
            xml_dict = xmltodict.parse(f.read())
            sru_dict_parser = SRUExplainAutoParser(xml_dict)
            configuration = sru_dict_parser.get_sru_configuration_from_explain_response()


            self.assertTrue("marcxml" in configuration.available_record_schemas.keys(), "Parsed record schemas are missing an expected record schema.")
            self.assertDictEqual({"sort": False, "identifier": "http://www.loc.gov/MARC21/slim"}, configuration.available_record_schemas["marcxml"], "An expected record schema does not match an actual record schema.")

            self.assertListEqual(configuration.supported_relation_modifiers, [])
            self.assertEqual(configuration.default_context_set, None)
            self.assertEqual(configuration.default_index, None)
            self.assertEqual(configuration.default_relation, None)
            self.assertEqual(configuration.default_record_schema, None)
            self.assertEqual(configuration.default_sort_schema, None)
            self.assertEqual(configuration.default_records_returned, None)
            self.assertEqual(configuration.max_records_supported, None)
            self.assertEqual(configuration.sru_version, "1.1")

            with open (TestFiles.loc_available_context_sets_and_indexes, "r") as f:
                expected_indexes = json.loads(f.read())

                self.assertEqual(configuration.available_context_sets_and_indexes, expected_indexes)

    def test_construct_sru_configuration_no_schema_info(self):
        """Not all SRU responses contain schema info. Here, we are verifying that responses without schema info can be
        parsed properly."""
        with open(TestFiles.sru_no_schema, "rb") as f:
            response_dict = xmltodict.parse(f.read())

            sru_dict_parser = SRUExplainAutoParser(response_dict)

            sru_configuration = sru_dict_parser.get_sru_configuration_from_explain_response()

            self.assertIsNone(sru_configuration.available_record_schemas)


