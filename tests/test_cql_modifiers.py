import unittest

from src.sru_queryer.cql import AndOrNotModifier, ProxModifier
from src.sru_queryer.cql import CQLModifierBase

from tests.testData.test_data import get_alma_sru_configuration

class TestCQLModifiers(unittest.TestCase):

    def test_format_cql_modifier_base_only(self):
        cql_modifier = CQLModifierBase("relevant")

        self.assertEqual(cql_modifier.format(), "/relevant")

    def test_format_cql_modifier_with_context_set(self):
        cql_modifier = CQLModifierBase("unit", context_set="alma")

        self.assertEqual(cql_modifier.format(), "/alma.unit")

    def test_format_cql_modifier_with_operator_and_value(self):
        cql_modifier = CQLModifierBase("unit", "<>", "street")

        self.assertEqual(cql_modifier.format(), '/unit<>"street"')

    def test_initializing_cql_modifier_operator_no_value_throws_error(self):
        with self.assertRaises(ValueError) as ve:
            cql_modifier = CQLModifierBase("unit", "=")

    def test_initializing_cql_modifier_value_no_operator_throws_error(self):
        with self.assertRaises(ValueError) as ve:
            cql_modifier = CQLModifierBase("unit", value="3")

    def test_initializing_cql_modifier_unsupported_operator(self):
        with self.assertRaises(ValueError) as ve:
            cql_modifier = CQLModifierBase("unit", "+", "Hippo")

        self.assertEqual(ve.exception.__str__(),
                         "Operator '+' is not supported.")

    def test_validate_base_name_invalid_name_raises_error(self):
        with self.assertRaises(ValueError) as ve:
            CQLModifierBase._validate_base_name(
                "not_unit_or_distance", ["unit", "distance"], 'Test')

        self.assertEqual(ve.exception.__str__(),
                         "Base name 'not_unit_or_distance' is not valid for modifier type 'Test.'")

    def test_validate_base_name_no_restriction_no_error(self):
        CQLModifierBase._validate_base_name(
            "not_unit_or_distance", "any", "Boom")

    def test_invalid_operator_raises_error(self):
        with self.assertRaises(ValueError) as ve:
            CQLModifierBase._validate_operator(
                "++", [">", "=="])

        self.assertEqual(ve.exception.__str__(),
                         "Operator '++' is not supported.")

    def test_value_allowed_for_base_name_in_context_set_no_limitations(self):
        CQLModifierBase._check_if_value_allowed_for_base_name_in_context_set(
            "test_set", "base", "ex_val", None)

    def test_value_allowed_for_base_name_invalid_with_limitations_raises_error(self):
        limitations = {
            "test_set": {
                "color": ["red", "blue"]
            }
        }
        with self.assertRaises(ValueError) as ve:
            CQLModifierBase._check_if_value_allowed_for_base_name_in_context_set(
                "test_set", "color", "purple", limitations)

        self.assertEqual(ve.exception.__str__(
        ), "Value 'purple' invalid for base name 'color' in context 'test_set.'")

    def test_value_allowed_for_base_name_set_not_specified_no_error(self):
        limitations = {
            "test_set": {
                "color": ["red", "blue"]
            }
        }
        CQLModifierBase._check_if_value_allowed_for_base_name_in_context_set(
            "different_set", "color", "purple", limitations)

    def test_value_allowed_for_base_name_base_name_not_specified_no_error(self):
        limitations = {
            "test_set": {
                "color": ["red", "blue"]
            }
        }
        CQLModifierBase._check_if_value_allowed_for_base_name_in_context_set(
            "test_set", "texture", "soft", limitations)

    def test_value_allowed_for_only_base_name_no_error(self):
        limitations = {
            "test_set": {
                "color": ["red", "blue"]
            }
        }
        CQLModifierBase._check_if_value_allowed_for_base_name_in_context_set(
            "test_set", "texture", None, limitations)

    def test_prox_modifier_restrict_unit_values_in_default_context_invalid_value_raises_error(self):
        """Integration test"""
        sru_configuration = get_alma_sru_configuration()
        
        prox_modifier = ProxModifier(
            "unit", "=", "invalid value")

        with self.assertRaises(ValueError) as ve:
            prox_modifier.validate(sru_configuration)

        self.assertIn("invalid value", ve.exception.__str__())

    def test_prox_modifier_restrict_unit_values_in_valid_context_not_specified_no_error(self):
        """Integration test"""
        sru_configuration = get_alma_sru_configuration()
        prox_modifier = ProxModifier(
            "unit", "=", "invalid value", "alma")

        prox_modifier.validate(sru_configuration)

    def test_proper_format_two_simple_modifiers(self):
        modifiers = [AndOrNotModifier("relevant"), AndOrNotModifier("simple")]

        actual_formatted_operator = CQLModifierBase.format_modifier_array(
            modifiers)

        expected_formatted_operator = '/relevant%20/simple%20'

        self.assertEqual(actual_formatted_operator,
                         expected_formatted_operator)

    def test_proper_format_two_simple_modifier_with_padding(self):
        modifiers = [AndOrNotModifier("relevant"), AndOrNotModifier("simple")]

        actual_formatted_operator = CQLModifierBase.format_modifier_array(
            modifiers)

        expected_formatted_operator = '/relevant%20/simple%20'

        self.assertEqual(actual_formatted_operator,
                         expected_formatted_operator)
