import unittest
from unittest.mock import patch

from tests.test_cql_boolean_operators import mock_search_clause_format, test_search_clause_1, test_search_clause_1_formatted
from src.sru_queryer.cql import AND
from src.sru_queryer.cql import SearchClause
from src.sru_queryer.cql import RawCQL


@patch.object(SearchClause, "_format", new=mock_search_clause_format)
class TestRawCQL(unittest.TestCase):

    def test_basic_raw_cql_no_padding(self):
        operator_condition = AND(test_search_clause_1, RawCQL(
            "%20alma.bib_count=2/combine=sum"))

        expected_format = f'{test_search_clause_1_formatted}%20and%20%20alma.bib_count=2/combine=sum'

        self.assertEqual(operator_condition.format(), expected_format)

    def test_basic_raw_cql_with_padding(self):
        operator_condition = AND(test_search_clause_1, RawCQL(
            "alma.bib_count=2/combine=sum", add_padding=True))

        expected_format = f'{test_search_clause_1_formatted}%20and%20%20alma.bib_count=2/combine=sum%20'

        self.assertEqual(operator_condition.format(), expected_format)

    def test_basic_raw_cql_from_dict(self):
        """The padding is added automatically from dicts."""
        raw_cql_dict = {
            "type": "rawCQL",
            "cql": "alma.bib_count=2/combine=sum"
        }
        raw_cql = RawCQL(from_dict=raw_cql_dict)

        expected_format = f'alma.bib_count=2/combine=sum'

        self.assertEqual(raw_cql.raw_cql_string, expected_format)

    def test_basic_raw_cql_from_dict_format_adds_padding(self):
        """The padding is added automatically from dicts."""
        raw_cql_dict = {
            "type": "rawCQL",
            "cql": "alma.bib_count=2/combine=sum"
        }
        raw_cql = RawCQL(from_dict=raw_cql_dict)

        expected_format = f'%20alma.bib_count=2/combine=sum%20'

        self.assertEqual(raw_cql.format(), expected_format)

    def test_basic_raw_cql_from_dict_incorrect_format_raises_error(self):
        """The padding is added automatically from dicts."""
        raw_cql_dict = {
            "type": "rawCQL",
            "cqlsq": "alma.bib_count=2/combine=sum"
        }
        with self.assertRaises(ValueError) as ve:
            RawCQL(from_dict=raw_cql_dict)

        self.assertEqual(ve.exception.__str__(), "Dict is not the correct format to instantiate RawCQL: {'type': 'rawCQL', 'cqlsq': 'alma.bib_count=2/combine=sum'}")
