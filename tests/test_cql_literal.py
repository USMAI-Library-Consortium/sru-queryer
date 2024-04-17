import unittest
from unittest.mock import patch

from tests.test_cql_boolean_operators import mock_index_query_format, test_search_index_config_1, test_search_index_config_1_formatted
from src.sru_queryer.cql import AND
from src.sru_queryer.cql import IndexQuery
from src.sru_queryer.cql import LITERAL


@patch.object(IndexQuery, "_format", new=mock_index_query_format)
class TestCQLLiteral(unittest.TestCase):

    def test_basic_cql_literal_no_padding(self):
        operator_condition = AND(test_search_index_config_1, LITERAL(
            "%20alma.bib_count=2/combine=sum"))

        expected_format = f'{test_search_index_config_1_formatted}%20and%20%20alma.bib_count=2/combine=sum'

        self.assertEqual(operator_condition.format(), expected_format)

    def test_basic_cql_literal_with_padding(self):
        operator_condition = AND(test_search_index_config_1, LITERAL(
            "alma.bib_count=2/combine=sum", add_padding=True))

        expected_format = f'{test_search_index_config_1_formatted}%20and%20%20alma.bib_count=2/combine=sum%20'

        self.assertEqual(operator_condition.format(), expected_format)
