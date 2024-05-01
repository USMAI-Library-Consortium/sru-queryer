import unittest

from src.sru_queryer.cql import SearchClause
from src.sru_queryer.cql import RelationModifier
from tests.testData.test_data import get_alma_sru_configuration

class TestSearchClause(unittest.TestCase):

    def test_format_with_all_query(self):
        search_index_config = SearchClause("alma", "test_attribute", "all", "")

        formatted_search_clause = search_index_config.format()

        self.assertEqual(formatted_search_clause,
                         'alma.test_attribute%20all%20""')

    def test_create_search_clause_index_no_operator_throws_error(self):
        with self.assertRaises(ValueError):
            SearchClause(search_term="", index_name="test_attribute",
                       context_set="alma")

    def test_create_search_clause_operator_no_index_throws_error(self):
        with self.assertRaises(ValueError):
            SearchClause(search_term="", relation="=", context_set="alma")

    def test_create_search_clause_context_set_no_index_name_throws_error(self):
        with self.assertRaises(ValueError):
            SearchClause(search_term="", context_set="alma")

    def test_create_search_clause_no_search_term_throws_error(self):
        with self.assertRaises(ValueError):
            SearchClause(search_term=None, index_name="test_attribute",
                       relation="all", context_set="alma")

    def test_format_with_all_query_2(self):
        search_index_config = SearchClause(
            context_set="alma", index_name="test_attribute", relation="all", search_term="hello*")

        formatted_search_clause = search_index_config.format()

        self.assertEqual(formatted_search_clause,
                         'alma.test_attribute%20all%20"hello*"')

    def test_format_with_default_context(self):
        search_index_config = SearchClause(
            search_term="10", index_name="bib_count", relation="==")

        formatted_search_clause = search_index_config.format()

        self.assertEqual(formatted_search_clause, 'bib_count=="10"')

    def test_format_with_only_search_term(self):
        search_index_config = SearchClause(search_term="10")

        formatted_search_clause = search_index_config.format()

        self.assertEqual(formatted_search_clause, '"10"')

    def test_validate_invalid_set(self):
        sru_configuration = get_alma_sru_configuration()

        with self.assertRaises(ValueError) as ve:
            SearchClause("puma", "bib_holding_count", ">", "15").validate(sru_configuration)

        self.assertIn("'puma'", ve.exception.__str__())
        self.assertIn("not available", ve.exception.__str__())

    def test_validate_unsupported_index(self):
        sru_configuration = get_alma_sru_configuration()
        with self.assertRaises(ValueError) as ve:
            SearchClause("alma", "bib_count", "==", "10").validate(sru_configuration)
            
    def test_validate_unsupported_relation(self):
        sru_configuration = get_alma_sru_configuration()

        with self.assertRaises(ValueError) as ve:
            SearchClause("alma", "mms_id", "?", "10").validate(sru_configuration)
        
        self.assertIn("relation '?'", ve.exception.__str__().lower())

    def test_format_with_simple_modifier(self):
        search_index_config = SearchClause("alma", "test_attribute", "all", "hello", [RelationModifier("relevant")])

        formatted_search_clause = search_index_config.format()

        self.assertEqual(formatted_search_clause, 'alma.test_attribute%20all/relevant%20"hello"')

    def test_validate_with_valid_modifier_integration(self):
        """Integration test."""
        sru_configuration = get_alma_sru_configuration()

        search_index_config = SearchClause("alma", "title", "all", "hello", [RelationModifier("relevant", context_set="alma")])

        search_index_config.validate(sru_configuration)

    def test_validate_with_invalid_modifier_raises_error_integration(self):
        """Integration test."""
        sru_configuration = get_alma_sru_configuration()
        with self.assertRaises(ValueError) as ve:
            search_index_config = SearchClause("alma", "title", "all", "hello", [
                                                RelationModifier("relevant", context_set="invalid_set_on_modifier")])
            search_index_config.validate(sru_configuration)

        self.assertIn("'invalid_set_on_modifier'", ve.exception.__str__())
        self.assertIn("not available", ve.exception.__str__())
