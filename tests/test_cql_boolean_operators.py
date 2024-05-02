import unittest
from unittest.mock import patch, call

from src.sru_queryer.cql import AND, OR, NOT
from src.sru_queryer.cql import CQLBooleanOperatorBase
from src.sru_queryer.cql import SearchClause
from src.sru_queryer.cql import AndOrNotModifier
from tests.testData.test_data import get_alma_sru_configuration

def mock_search_clause_format(self, **kwargs):
    """Mock the SearchClause '_format' method so the tests will pass even if 
    I want to change how the formatting looks"""
    if self._relation in ["all"]:
        return f'{self._context_set}.{self._index_name}%20{self._relation}%20"{self._search_term}"'
    else:
        return f'{self._context_set}.{self._index_name}{self._relation}"{self._search_term}"'


test_search_clause_1 = SearchClause("alma", "inventory_count", "=", "100")
test_search_clause_1_formatted = 'alma.inventory_count="100"'
test_search_clause_2 = SearchClause("alma", "library_code", "==", "umcp")
test_search_clause_2_formatted = 'alma.library_code=="umcp"'
test_search_clause_3 = SearchClause("alma", "public_note", "=", "Hello")
test_search_clause_3_formatted = 'alma.public_note="Hello"'
test_search_clause_4 = SearchClause("alma", "item_pid", "<", "12")
test_search_clause_4_formatted = 'alma.item_pid<"12"'
test_search_clause_5 = SearchClause("alma", "issueYear", "<=", "1998")
test_search_clause_5_formatted = 'alma.issueYear<="1998"'

unary_operator_error = CQLBooleanOperatorBase.unary_operator_error


@patch.object(SearchClause, "_format",  new=mock_search_clause_format)
class TestCQLBooleanOperatorClasses(unittest.TestCase):

    def test_invalid_condition_throws_error(self):
        with self.assertRaises(ValueError) as e:
            operator = AND(test_search_clause_1, "fake_data")

        self.assertEqual(
            e.exception.__str__(), "Condition 'fake_data' is not valid")

    def test_simple_format_and(self):
        and_operator_condition = AND(
            test_search_clause_1, test_search_clause_2)
        actual_formatted_and_operator = and_operator_condition.format()
        expected_formatted_and_operator = f'{test_search_clause_1_formatted}%20and%20{test_search_clause_2_formatted}'

        self.assertEqual(actual_formatted_and_operator,
                         expected_formatted_and_operator)

    def test_simple_format_and_reversed_conditions(self):
        and_operator_condition = AND(
            test_search_clause_2, test_search_clause_1)
        actual_formatted_and_operator = and_operator_condition.format()
        expected_formatted_and_operator = f'{test_search_clause_2_formatted}%20and%20{test_search_clause_1_formatted}'

        self.assertEqual(actual_formatted_and_operator,
                         expected_formatted_and_operator)

    def test_simple_format_or(self):
        or_operator_condition = OR(
            test_search_clause_1, test_search_clause_2)
        actual_formatted_or_operator = or_operator_condition.format()
        expected_formatted_or_operator = f'{test_search_clause_1_formatted}%20or%20{test_search_clause_2_formatted}'

        self.assertEqual(actual_formatted_or_operator,
                         expected_formatted_or_operator)

    def test_recursive_format(self):
        and_operator_condition = AND(AND(
            test_search_clause_1, test_search_clause_2), test_search_clause_3)
        actual_formatted_and_operator = and_operator_condition.format()
        expected_formatted_and_operator = f'({test_search_clause_1_formatted}%20and%20{test_search_clause_2_formatted})%20and%20{test_search_clause_3_formatted}'

        self.assertEqual(actual_formatted_and_operator,
                         expected_formatted_and_operator)

    def test_3_operators(self):
        and_operator_condition = AND(
            test_search_clause_1, test_search_clause_2, test_search_clause_3)
        actual_formatted_operator = and_operator_condition.format()
        expected_formatted_operator = f'{test_search_clause_1_formatted}%20and%20{test_search_clause_2_formatted}%20and%20{test_search_clause_3_formatted}'

        self.assertEqual(actual_formatted_operator,
                         expected_formatted_operator)

    def test_mixed_operators(self):
        and_operator_condition = AND(
            test_search_clause_1, test_search_clause_2, test_search_clause_3, OR(test_search_clause_4))
        actual_formatted_operator = and_operator_condition.format()
        expected_formatted_operator = f'{test_search_clause_1_formatted}%20and%20{test_search_clause_2_formatted}%20and%20{test_search_clause_3_formatted}%20or%20{test_search_clause_4_formatted}'

        self.assertEqual(actual_formatted_operator,
                         expected_formatted_operator)

    def test_sub_operator_first_position(self):
        and_operator_condition = AND(OR(test_search_clause_4, test_search_clause_5),
                                     test_search_clause_1, test_search_clause_2, test_search_clause_3)
        actual_formatted_operator = and_operator_condition.format()
        expected_formatted_operator = f'({test_search_clause_4_formatted}%20or%20{test_search_clause_5_formatted})%20and%20{test_search_clause_1_formatted}%20and%20{test_search_clause_2_formatted}%20and%20{test_search_clause_3_formatted}'

        self.assertEqual(actual_formatted_operator,
                         expected_formatted_operator)

    def test_sub_operator_middle_position(self):
        and_operator_condition = AND(test_search_clause_1, OR(
            test_search_clause_4, test_search_clause_5), test_search_clause_3)
        actual_formatted_operator = and_operator_condition.format()
        expected_formatted_operator = f'{test_search_clause_1_formatted}%20and%20({test_search_clause_4_formatted}%20or%20{test_search_clause_5_formatted})%20and%20{test_search_clause_3_formatted}'

        self.assertEqual(actual_formatted_operator,
                         expected_formatted_operator)

    def test_unary_operator_first_position(self):
        operator = AND(OR(test_search_clause_1),
                       test_search_clause_2, test_search_clause_3)

        with self.assertRaises(ValueError) as e:
            actual_formatted_operator = operator.format()

        self.assertEqual(e.exception.__str__(), unary_operator_error)

    def test_unary_operator_middle_position(self):
        and_operator_condition = AND(test_search_clause_1, OR(
            test_search_clause_4), test_search_clause_3)
        actual_formatted_operator = and_operator_condition.format()
        expected_formatted_operator = f'{test_search_clause_1_formatted}%20or%20{test_search_clause_4_formatted}%20and%20{test_search_clause_3_formatted}'

        self.assertEqual(actual_formatted_operator,
                         expected_formatted_operator)

    def test_display_not_operator_middle_position(self):
        operator = OR(test_search_clause_1,
                      NOT(test_search_clause_2), test_search_clause_3)

        actual_formatted_operator = operator.format()

        expected_formatted_operator = f'{test_search_clause_1_formatted}%20not%20{test_search_clause_2_formatted}%20or%20{test_search_clause_3_formatted}'

        self.assertEqual(actual_formatted_operator,
                         expected_formatted_operator)

    def test_not_operator_in_beginning_raises_error(self):
        with self.assertRaises(ValueError) as e:
            operator = OR(NOT(test_search_clause_1),
                          test_search_clause_2)

            operator.format()

        self.assertEqual(e.exception.__str__(),
                         unary_operator_error)

    def test_operator_as_first_condition_of_sub_condition_raises_error(self):
        with self.assertRaises(ValueError) as e:
            operator = OR(test_search_clause_1, AND(
                OR(test_search_clause_2)), test_search_clause_3)

            operator.format()

        self.assertEqual(e.exception.__str__(),
                         unary_operator_error)

    @patch("src.sru_queryer._base._sru_validator.SRUValidator.validate_cql")
    def test_validate_operator_pair_and_index_error_raises_error(self, mock_validate_index_info):
        mock_validate_index_info.side_effect = ValueError("Example Error")

        sru_configuration = get_alma_sru_configuration()

        with self.assertRaises(ValueError) as ve:

            AND(SearchClause("alma", "fake_index", "==", "10"), SearchClause(
                "alma", "fake_index_2", "==", "10")).validate(sru_configuration)

        self.assertEqual(ve.exception.__str__(),
                         "Example Error")

        calls = [call(sru_configuration, "alma", "fake_index", "==", "10")]
        mock_validate_index_info.assert_has_calls(calls)

    @patch("src.sru_queryer._base._sru_validator.SRUValidator.validate_cql")
    def test_validate_operator_pair_with_valid_index_called_twice(self, mock_validate_index_info):

        sru_configuration = get_alma_sru_configuration()

        AND(SearchClause("alma", "valid_index", "==", "10"), SearchClause(
            "alma", "valid_index_2", "==", "10")).validate(sru_configuration)

        calls = [call(sru_configuration, "alma", "valid_index", "==", "10"),
                 call(sru_configuration, "alma", "valid_index_2", "==", "10")]
        mock_validate_index_info.assert_has_calls(calls)

    def test_proper_format_with_simple_modifier(self):
        operator = OR(test_search_clause_1, test_search_clause_2,
                      modifiers=[AndOrNotModifier(base_name="relevant")])

        actual_formatted_operator = operator.format()

        expected_formatted_operator = f'{test_search_clause_1_formatted}%20or%20/relevant%20{test_search_clause_2_formatted}'

        self.assertEqual(actual_formatted_operator,
                         expected_formatted_operator)

    def test_proper_format_with_full_modifier(self):
        operator = OR(test_search_clause_1, test_search_clause_2,
                      modifiers=[AndOrNotModifier("alma", "unit", "=", "street")])

        actual_formatted_operator = operator.format()

        expected_formatted_operator = f'{test_search_clause_1_formatted}%20or%20/alma.unit="street"%20{test_search_clause_2_formatted}'

        self.assertEqual(actual_formatted_operator,
                         expected_formatted_operator)
