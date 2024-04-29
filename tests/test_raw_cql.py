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
