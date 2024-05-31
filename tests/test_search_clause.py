import unittest

from src.sru_queryer.cql import SearchClause
from src.sru_queryer.cql import RelationModifier
from tests.testData.test_data import get_alma_sru_configuration

class TestSearchClause(unittest.TestCase):

    def test_format_with_all_query(self):
        search_clause = SearchClause("alma", "test_attribute", "all", "")

        formatted_search_clause = search_clause.format()

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
        search_clause = SearchClause(
            context_set="alma", index_name="test_attribute", relation="all", search_term="hello*")

        formatted_search_clause = search_clause.format()

        self.assertEqual(formatted_search_clause,
                         'alma.test_attribute%20all%20"hello*"')
        
    def test_format_with_any_keyword(self):
        search_clause = SearchClause(
            context_set="alma", index_name="test_attribute", relation="any", search_term="hello*")

        formatted_search_clause = search_clause.format()

        self.assertEqual(formatted_search_clause,
                         'alma.test_attribute%20any%20"hello*"')

    def test_format_with_default_context(self):
        search_clause = SearchClause(
            search_term="10", index_name="bib_count", relation="==")

        formatted_search_clause = search_clause.format()

        self.assertEqual(formatted_search_clause, 'bib_count%20==%20"10"')

    def test_format_with_only_search_term(self):
        search_clause = SearchClause(search_term="10")

        formatted_search_clause = search_clause.format()

        self.assertEqual(formatted_search_clause, '"10"')
    
    def test_create_from_dict(self):
        search_clause_dict = {
          "_context_set": "alma",
          "_index_name": "title",
          "_relation": "=",
          "_search_term": "Frog",
          "_modifiers": None
        }

        search_clause = SearchClause(from_dict={
          "type": "searchClause",
          "context_set": "alma",
          "index_name": "title",
          "relation": "=",
          "search_term": "Frog"
        })

        self.assertEqual(search_clause.__dict__, search_clause_dict)

    def test_create_from_dict_required_values_only(self):
        search_clause_dict = {
          "_context_set": None,
          "_index_name": None,
          "_relation": None,
          "_search_term": "Frog",
          "_modifiers": None
        }

        search_clause = SearchClause(from_dict={
          "type": "searchClause",
          "search_term": "Frog",
        })

        self.assertEqual(search_clause.__dict__, search_clause_dict)

    def test_create_from_dict_wrong_type_value_error(self):
        
        with self.assertRaises(ValueError) as ve:
            SearchClause(from_dict={
                "type": "notSearchClause",
                "context_set": "alma",
                "index_name": "title",
                "relation": "=",
                "search_term": "Frog",
                "modifiers": None
            })

        self.assertIn("notSearchClause", ve.exception.__str__())

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
        search_clause = SearchClause("alma", "test_attribute", "all", "hello", [RelationModifier(base_name="relevant")])

        formatted_search_clause = search_clause.format()

        self.assertEqual(formatted_search_clause, 'alma.test_attribute%20all/relevant%20"hello"')

    def test_validate_with_valid_modifier_integration(self):
        """Integration test."""
        sru_configuration = get_alma_sru_configuration()

        search_clause = SearchClause("alma", "title", "all", "hello", [RelationModifier("alma", "relevant")])

        search_clause.validate(sru_configuration)

    def test_validate_with_invalid_modifier_raises_error_integration(self):
        """Integration test."""
        sru_configuration = get_alma_sru_configuration()
        with self.assertRaises(ValueError) as ve:
            search_clause = SearchClause("alma", "title", "all", "hello", [
                                                RelationModifier("invalid_set_on_modifier", "relevant")])
            search_clause.validate(sru_configuration)

        self.assertIn("'invalid_set_on_modifier'", ve.exception.__str__())
        self.assertIn("not available", ve.exception.__str__())
