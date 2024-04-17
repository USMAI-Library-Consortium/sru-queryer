import unittest

from src.sru_queryer.cql import IndexQuery
from src.sru_queryer.cql import RelationModifier
from tests.testData.test_data import get_alma_sru_configuration

class TestIndexQuery(unittest.TestCase):

    def test_format_with_all_query(self):
        search_index_config = IndexQuery("alma", "test_attribute", "all", "")

        formatted_search_index_config = search_index_config.format()

        self.assertEqual(formatted_search_index_config,
                         'alma.test_attribute%20all%20""')

    def test_create_index_query_index_no_operator_throws_error(self):
        with self.assertRaises(ValueError):
            IndexQuery(value="", index_name="test_attribute",
                       context_set="alma")

    def test_create_index_query_operator_no_index_throws_error(self):
        with self.assertRaises(ValueError):
            IndexQuery(value="", operation="=", context_set="alma")

    def test_create_index_query_context_set_no_index_name_throws_error(self):
        with self.assertRaises(ValueError):
            IndexQuery(value="", context_set="alma")

    def test_create_index_query_value_none_throws_error(self):
        with self.assertRaises(ValueError):
            IndexQuery(value=None, index_name="test_attribute",
                       operation="all", context_set="alma")

    def test_format_with_all_query_2(self):
        search_index_config = IndexQuery(
            context_set="alma", index_name="test_attribute", operation="all", value="hello*")

        formatted_search_index_config = search_index_config.format()

        self.assertEqual(formatted_search_index_config,
                         'alma.test_attribute%20all%20"hello*"')

    def test_format_with_default_context(self):
        search_index_config = IndexQuery(
            value="10", index_name="bib_count", operation="==")

        formatted_search_index_config = search_index_config.format()

        self.assertEqual(formatted_search_index_config, 'bib_count=="10"')

    def test_format_with_only_value(self):
        search_index_config = IndexQuery(value="10")

        formatted_search_index_config = search_index_config.format()

        self.assertEqual(formatted_search_index_config, '"10"')

    def test_validate_invalid_set(self):
        sru_configuration = get_alma_sru_configuration()

        with self.assertRaises(ValueError) as ve:
            IndexQuery("puma", "bib_holding_count", ">", "15").validate(sru_configuration)

        self.assertIn("'puma'", ve.exception.__str__())
        self.assertIn("not available", ve.exception.__str__())

    def test_validate_unsupported_index(self):
        sru_configuration = get_alma_sru_configuration()
        with self.assertRaises(ValueError) as ve:
            IndexQuery("alma", "bib_count", "==", "10").validate(sru_configuration)
            
    def test_validate_unsupported_operation(self):
        sru_configuration = get_alma_sru_configuration()

        with self.assertRaises(ValueError) as ve:
            IndexQuery("alma", "mms_id", "?", "10").validate(sru_configuration)
        
        self.assertIn("relation '?'", ve.exception.__str__().lower())

    def test_format_with_simple_modifier(self):
        search_index_config = IndexQuery("alma", "test_attribute", "all", "hello", [RelationModifier("relevant")])

        formatted_search_index_config = search_index_config.format()

        self.assertEqual(formatted_search_index_config, 'alma.test_attribute%20all/relevant%20"hello"')

    def test_validate_with_valid_modifier_integration(self):
        """Integration test."""
        sru_configuration = get_alma_sru_configuration()

        search_index_config = IndexQuery("alma", "title", "all", "hello", [RelationModifier("relevant", context_set="alma")])

        search_index_config.validate(sru_configuration)

    def test_validate_with_invalid_modifier_raises_error_integration(self):
        """Integration test."""
        sru_configuration = get_alma_sru_configuration()
        with self.assertRaises(ValueError) as ve:
            search_index_config = IndexQuery("alma", "title", "all", "hello", [
                                                RelationModifier("relevant", context_set="invalid_set_on_modifier")])
            search_index_config.validate(sru_configuration)

        self.assertIn("'invalid_set_on_modifier'", ve.exception.__str__())
        self.assertIn("not available", ve.exception.__str__())
