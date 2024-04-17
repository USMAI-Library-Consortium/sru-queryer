import unittest

from src.sru_queryer._base._sru_validator import SRUValidator
from tests.testData.test_data import get_gapines_sru_configuration, get_alma_sru_configuration, get_test_sru_configuration_no_sort_or_supported_operations_or_config, test_available_record_schemas_one_false
from src.sru_queryer.sru import SortKey

class TestSRUValidator(unittest.TestCase):

    def test_validate_context_set_invalid_set_throws_error(self):
        sru_configuration = get_gapines_sru_configuration()

        with self.assertRaises(ValueError) as ve:
            SRUValidator.validate_context_set(sru_configuration, "invalid_set")

        self.assertIn("invalid_set", ve.exception.__str__())

    def test_validate_context_set_valid_set_no_error(self):
        sru_configuration = get_gapines_sru_configuration()

        SRUValidator.validate_context_set(sru_configuration, "eg")

    def test_validate_index_invalid_set_raises_error(self):
        sru_configuration = get_alma_sru_configuration()

        with self.assertRaises(ValueError) as ve:
            SRUValidator.validate_cql(sru_configuration, "invalid_set", "all_for_ui", "=")

        self.assertIn("invalid_set", ve.exception.__str__())

    def test_validate_index_invalid_index_raises_error(self):
        sru_configuration = get_alma_sru_configuration()

        with self.assertRaises(ValueError) as ve:
            SRUValidator.validate_cql(sru_configuration, "alma", "invalid_index", "=")

        self.assertIn("invalid_index", ve.exception.__str__())

    def test_validate_index_valid_index_no_error(self):
        sru_configuration = get_gapines_sru_configuration()

        SRUValidator.validate_cql(sru_configuration, "eg", "keyword")

    def test_validate_index_relation_invalid_relation_raises_error(self):
        sru_configuration = get_alma_sru_configuration()

        with self.assertRaises(ValueError) as ve:
            SRUValidator.validate_cql(sru_configuration, "alma", "all_for_ui", relation="***")

        self.assertIn("***", ve.exception.__str__())

    def test_validate_index_invalid_value_raises_error(self):
        sru_configuration = get_alma_sru_configuration()

        with self.assertRaises(ValueError) as ve:
            SRUValidator.validate_cql(sru_configuration, "alma", "alternate_complete_edition", "=", value="")

        self.assertIn("empty", ve.exception.__str__())

    def test_validate_index_can_sort_invalid_sort_raises_error(self):
        sru_configuration = get_alma_sru_configuration()
        sru_configuration.disable_validation_for_cql_defaults = True

        with self.assertRaises(ValueError) as ve:
            SRUValidator.validate_cql(sru_configuration, "alma", "alternate_complete_edition", "=", evaluate_can_sort=True)

        self.assertIn("sort", ve.exception.__str__())

    def test_validate_index_no_value_sort_or_supported_operations_info(self):
        sru_configuration = get_test_sru_configuration_no_sort_or_supported_operations_or_config()

        SRUValidator.validate_cql(sru_configuration, "dc", "title", "all", "", evaluate_can_sort=True)

    def test_validate_index_with_default_context_set(self):
        sru_configuration = get_gapines_sru_configuration()

        SRUValidator.validate_cql(sru_configuration, index_name="keyword")

    def test_validate_invalid_index_with_default_context_set_throws_error(self):
        sru_configuration = get_gapines_sru_configuration()

        with self.assertRaises(ValueError) as ve:
            SRUValidator.validate_cql(sru_configuration, index_name="invalid_index")

        self.assertIn("'eg'", ve.exception.__str__())
        self.assertIn("invalid_index", ve.exception.__str__())

    def test_validate_invalid_index_with_no_context_set_and_no_default_context_set_throws_error(self):
        sru_configuration = get_alma_sru_configuration()

        with self.assertRaises(ValueError) as ve:
            SRUValidator.validate_cql(sru_configuration, index_name="all_for_ui")

        self.assertIn("ensure", ve.exception.__str__())

    def test_validate_value_with_all_defaults_set_no_error(self):
        sru_configuration = get_alma_sru_configuration()
        sru_configuration.default_context_set = "alma"
        sru_configuration.default_index = "all_for_ui"
        sru_configuration.default_relation = "=="

        SRUValidator.validate_cql(sru_configuration, value="hello")

    def test_validate_invalid_value_with_all_defaults_set_throws_error(self):
        sru_configuration = get_alma_sru_configuration()
        sru_configuration.default_context_set = "alma"
        sru_configuration.default_index = "alternate_complete_edition"
        sru_configuration.default_relation = "=="

        with self.assertRaises(ValueError) as ve:
            SRUValidator.validate_cql(sru_configuration, value="")

        self.assertIn("empty", ve.exception.__str__())

    def test_validate_all_defaults_set_no_error(self):
        sru_configuration = get_alma_sru_configuration()
        sru_configuration.default_context_set = "alma"
        sru_configuration.default_index = "alternate_complete_edition"
        sru_configuration.default_relation = "=="

        SRUValidator.validate_cql(sru_configuration)

    def test_validate_default_index_and_context_set_and_relation_relation_info_included_throws_error(self):
        sru_configuration = get_alma_sru_configuration()
        sru_configuration.default_context_set = "alma"
        sru_configuration.default_index = "alternate_complete_edition"

        with self.assertRaises(ValueError) as ve:
            SRUValidator.validate_cql(sru_configuration)

        self.assertIn("relation", ve.exception.__str__())

    def test_validate_default_index_and_context_set_no_default_relation_relation_info_not_included_no_error(self):
        sru_configuration = get_gapines_sru_configuration()
        sru_configuration.default_relation = None

        SRUValidator.validate_cql(sru_configuration)

    def test_validate_invalid_index_with_no_context_set_and_no_default_context_set_and_disabled_validation_no_error(self):
        sru_configuration = get_alma_sru_configuration()
        sru_configuration.disable_validation_for_cql_defaults = True

        SRUValidator.validate_cql(sru_configuration, index_name="all_for_ui")

    def test_validate_configuration_defaults_throws_error_invalid_context_set(self):
        """Integration"""
        sru_configuration = get_gapines_sru_configuration()
        sru_configuration.default_context_set="invalid_set"

        with self.assertRaises(ValueError) as ve:
            SRUValidator.validate_defaults(sru_configuration)

        self.assertIn("invalid_set", ve.exception.__str__())

    def test_validate_configuration_defaults_throws_error_invalid_index(self):
        """Integration"""
        sru_configuration = get_gapines_sru_configuration()
        sru_configuration.default_index="invalid_index"

        with self.assertRaises(ValueError) as ve:
            SRUValidator.validate_defaults(sru_configuration)

        self.assertIn("invalid_index", ve.exception.__str__())

    def test_validate_configuration_defaults_no_error_valid_index(self):
        """Integration"""
        sru_configuration = get_gapines_sru_configuration()

        SRUValidator.validate_defaults(sru_configuration)

    def test_validate_configuration_defaults_throws_error_invalid_relation(self):
        """Integration"""
        sru_configuration = get_alma_sru_configuration()
        sru_configuration.default_context_set = "alma"
        sru_configuration.default_index = "all_for_ui"
        sru_configuration.default_relation="invalid_relation"

        with self.assertRaises(ValueError) as ve:
            SRUValidator.validate_defaults(sru_configuration)

        self.assertIn("invalid_relation", ve.exception.__str__())

    def test_validate_configuration_defaults_throws_error_invalid_record_schema(self):
        sru_configuration = get_alma_sru_configuration()
        sru_configuration.default_record_schema = "invalid_record_schema"

        with self.assertRaises(ValueError) as ve:
            SRUValidator.validate_defaults(sru_configuration)

        self.assertIn("invalid_record_schema", ve.exception.__str__())

    def test_validate_configuration_defaults_throws_error_invalid_sort_schema(self):
        sru_configuration = get_alma_sru_configuration()
        sru_configuration.default_record_schema = "invalid_sort_schema"

        with self.assertRaises(ValueError) as ve:
            SRUValidator.validate_defaults(sru_configuration)

        self.assertIn("invalid_sort_schema", ve.exception.__str__())

    def test_validate_configuration_defaults_throws_error_schema_cannot_sort(self):
        sru_configuration = get_alma_sru_configuration()
        sru_configuration.default_sort_schema = "cnmarcxml"
        sru_configuration.available_record_schemas = test_available_record_schemas_one_false

        with self.assertRaises(ValueError) as ve:
            SRUValidator.validate_defaults(sru_configuration)

        self.assertIn("cannot sort", ve.exception.__str__())

    def test_validate_sort_integration(self):
        sru_configuration = get_alma_sru_configuration()

        with self.assertRaises(ValueError) as e:
            SRUValidator.validate_sort(sru_configuration, [{"index_set": "alma", "index_name": "bib_holding_count", "sort_order": "boom"}])

        self.assertIn("'boom'", e.exception.__str__())
        self.assertIn("invalid", e.exception.__str__())
                
    def test_validate_sort_key_schema_no_sort_raises_error(self):
        sru_configuration = get_alma_sru_configuration()
        sru_configuration.available_record_schemas = test_available_record_schemas_one_false

        with self.assertRaises(ValueError) as ve:
            SRUValidator.validate_sort(sru_configuration, [SortKey("", schema="cnmarcxml")])

        self.assertIn("'cnmarcxml'", ve.exception.__str__())
        self.assertIn("not available", ve.exception.__str__())

    def test_validate_sort_base_title_repeated_throws_error(self):
        sru_configuration = get_alma_sru_configuration()
        with self.assertRaises(ValueError) as ve:
                    SRUValidator.validate_sort(sru_configuration,
                        sort_queries=[{"index_set": "alma", "index_name": "title", "sort_order": "ascending"}, {"index_set": "alma", "index_name": "title", "sort_order": "descending"}])

        self.assertIn("repeat", ve.exception.__str__())