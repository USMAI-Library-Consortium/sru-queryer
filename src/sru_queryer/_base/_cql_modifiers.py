from __future__ import annotations

# I know this is bad coupling, but it would take too refactoring work to fix.
from ._sru_validator import SRUValidator

class CQLModifierBase:
    # Pulled from Library of Congress docs.
    supported_comparison_symbols = ["=", "<", "<=", ">", ">=", "<>"]

    # Functions as whitelist. The string "any" will allow any value
    supported_base_names: str | list[str] = "any"

    # Functions as a blacklist. See class 'prox' below for an example.
    base_name_value_limitations_per_context: dict | None = None
    modifier_type = "Generic"

    # Will probably be the same for all modifiers. But override if you want.
    default_context_set_for_modifier = "cql"

    def __init__(self, context_set: str | None = None, base_name: str = None, comparison_symbol: str | None = None, value: str | None = None):
        if not base_name:
            raise ValueError("You must include a base name.")
        self.base_name = base_name
        self.context_set = context_set

        if comparison_symbol and not value:
            raise ValueError(
                "If you include an comparison_symbol, you must include a value.")
        if value and not comparison_symbol:
            raise ValueError(
                "If you include a value, you must include an comparison_symbol.")
        if comparison_symbol and comparison_symbol not in self.supported_comparison_symbols:
            raise ValueError(f"Operator '{comparison_symbol}' is not supported.")
        self.comparison_symbol = comparison_symbol
        self.value = value

        self._validate_base_name(
            base_name, self.supported_base_names, self.modifier_type)
        if comparison_symbol != None:
            self._validate_comparison_symbol(comparison_symbol, self.supported_comparison_symbols)

    def format(self):
        return self._format()

    def _format(self, **kwargs) -> str:
        formatted_modifier = "/"
        if self.context_set:
            formatted_modifier += f'{self.context_set}.'

        formatted_modifier += f'{self.base_name}'

        if self.comparison_symbol and self.value:
            formatted_modifier += f'{self.comparison_symbol}"{self.value}"'

        return formatted_modifier

    @staticmethod
    def format_modifier_array(modifiers):
        """Returns formatted modifiers."""
        formatted_modifiers = ''
        if modifiers:
            for boolean_comparison_symbol_modifier in modifiers:
                formatted_modifiers += f'{boolean_comparison_symbol_modifier.format()}%20'
        return formatted_modifiers

    def validate(self, sru_configuration):

        context_set_to_check = self.context_set
        if context_set_to_check is None:
            context_set_to_check = self.default_context_set_for_modifier

        context_set_to_check = context_set_to_check.lower()

        # TODO - should we have the default modifier context set equal to the context set for
        # the queries, or should we keep it seperate? Right now, it's CQL
        if self.context_set and self.context_set != self.default_context_set_for_modifier:
            SRUValidator.validate_context_set(sru_configuration, self.context_set)

        if self.value != None:
            self._check_if_value_allowed_for_base_name_in_context_set(
                context_set_to_check, self.base_name, self.value, self.base_name_value_limitations_per_context)

    @staticmethod
    def _validate_comparison_symbol(comparison_symbol, supported_comparison_symbols):
        if comparison_symbol not in supported_comparison_symbols:
            raise ValueError(f"Operator '{comparison_symbol}' is not supported.")

    @staticmethod
    def _validate_base_name(base_name: str, supported_base_names: str | list[str], modifier_type):
        if supported_base_names != "any":
            if base_name not in supported_base_names:
                raise ValueError(
                    f"Base name '{base_name}' is not valid for modifier type '{modifier_type}.'")
        return

    @staticmethod
    def _check_if_value_allowed_for_base_name_in_context_set(context_set, base_name, value, limitations):
        if not limitations:
            return

        if context_set not in limitations:
            return

        if base_name not in limitations[context_set]:
            return

        if value not in limitations[context_set][base_name]:
            raise ValueError(
                f"Value '{value}' invalid for base name '{base_name}' in context '{context_set}.'")


class AndOrNotModifier(CQLModifierBase):
    modifier_type = "AndOrNot"


class ProxModifier(CQLModifierBase):
    # Pulled from Library of Congress docs
    supported_base_names = ["unit", "distance"]
    base_name_value_limitations_per_context = {
        "cql": {
            "unit": ['word', 'sentence', 'paragraph', 'element']
        }
    }
    modifier_type = "Prox"


class RelationModifier(CQLModifierBase):
    modifier_type = "Relation"
