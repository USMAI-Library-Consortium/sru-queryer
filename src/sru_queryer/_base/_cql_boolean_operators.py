from __future__ import annotations

from ._search_clause import SearchClause
from ._raw_cql import RawCQL
from ._cql_modifiers import AndOrNotModifier, CQLModifierBase


class CQLBooleanOperatorBase:
    operator = None
    unary_operator_error = "Error during formatting: Operator cannot have one argument AND the first condition of a parent operator (including if it's used by itself). No operators are unary, even NOT."

    def __init__(self, *args, modifiers: list[AndOrNotModifier] = None, from_dict: dict | None = None):
        self.conditions = []

        conditions_to_loop_through = []
        if from_dict:
            try:
                self.operator = from_dict["operator"]
            except KeyError:
                ValueError(f"Operator dict is invalid: {from_dict.__str__()}")
            for condition in from_dict["conditions"]:
                try:
                    if condition["type"] == "searchClause":
                        conditions_to_loop_through.append(SearchClause(from_dict=condition))
                    elif condition["type"] == "booleanOperator":
                        conditions_to_loop_through.append(CQLBooleanOperatorBase(from_dict=condition))
                    elif condition["type"] == "rawCQL":
                        conditions_to_loop_through.append(RawCQL(from_dict=condition))
                    else:
                        raise KeyError()
                except KeyError:
                    ValueError(f"Condition is invalid: {condition.__str__()}")
        else:
            conditions_to_loop_through = args

        for condition in conditions_to_loop_through:
            if isinstance(condition, SearchClause) or isinstance(condition, CQLBooleanOperatorBase) or isinstance(condition, RawCQL):
                self.conditions.append(condition)
            else:
                raise ValueError(
                    f"Condition '{condition.__str__()}' is not valid")

        if not self.conditions:
            raise ValueError(
                "An operator must have a minimum of one condition.")

        self.modifiers = modifiers

    def format(self) -> str:
        return self._format(nested_condition=False)

    def _format(self, nested_condition, is_first_condition_of_parent=True):
        is_unary_operator = len(self.conditions) == 1

        if is_first_condition_of_parent and is_unary_operator:
            raise ValueError(self.unary_operator_error)

        formatted_conditional = ""
        is_first_condition_of_conditions = True
        for operator_is_index_or_raw_cql in self.conditions:

            parent_is_first_condition_of_parent = is_first_condition_of_parent
            # For clarity, I've set this variable name here. This means,
            # "the parent of this condition is the first condition in its
            # parent operator."

            parent_is_unary_operator = is_unary_operator
            # Same deal as above. Now referring to the parent of this conditional in
            # the loop, which is 'self'

            condition_is_operator = isinstance(
                operator_is_index_or_raw_cql, CQLBooleanOperatorBase)
            condition_is_index_or_raw_cql = isinstance(
                operator_is_index_or_raw_cql, SearchClause) or isinstance(operator_is_index_or_raw_cql, RawCQL)

            if condition_is_operator:
                operator = operator_is_index_or_raw_cql
                # Renaming to operator because we checked above whether it's an operator.

                condition_is_unary_operator = len(
                    operator.conditions) == 1

                # Different conditions we're testing for, varies whether the operator is included or not.

                operator_is_unary_and_parent_is_not_first_condition = (
                    not parent_is_first_condition_of_parent) and condition_is_unary_operator
                # Uses the boolean operator of the parent, not self
                # This checks if 'self' is NOT the first condition of the parent and if the current operator
                # in the loop is a unary operator. If that's the case, we should include self's boolean
                # operator name beforehand

                operator_has_multiple_conditions_and_is_not_first_condition_of_conditions = (
                    not is_first_condition_of_conditions and not condition_is_unary_operator)
                # If the operator has multiple conditions (which means it's surrounded by parenthesis),
                # and it isn't the first condition of this (self)'s conditions, we should add self's
                # boolean operator beforehand

                if operator_is_unary_and_parent_is_not_first_condition or operator_has_multiple_conditions_and_is_not_first_condition_of_conditions:
                    formatted_conditional += self.format_operator()

            elif condition_is_index_or_raw_cql:
                # Now we check whether we should append self's operator given the condition is an index

                is_first_condition_and_parent_is_unary_operator_and_parent_not_first_condition = (
                    not parent_is_first_condition_of_parent and is_first_condition_of_conditions and parent_is_unary_operator)

                if not is_first_condition_of_conditions or is_first_condition_and_parent_is_unary_operator_and_parent_not_first_condition:
                    formatted_conditional += self.format_operator()

            formatted_conditional += f"{operator_is_index_or_raw_cql._format(nested_condition=True, is_first_condition_of_parent=is_first_condition_of_conditions)}"
            is_first_condition_of_conditions = False

        if nested_condition and not is_unary_operator:
            formatted_conditional = f"({formatted_conditional})"
        return formatted_conditional

    def format_operator(self):
        formatted_operator = f"%20{self.operator}%20"
        formatted_operator += CQLModifierBase.format_modifier_array(
            self.modifiers)
        return formatted_operator

    def validate(self, sru_configuration):
        """Validates itself, its nested conditions, and its modifiers."""
        for condition in self.conditions:
            condition.validate(sru_configuration)

        if self.modifiers:
            for modifier in self.modifiers:
                modifier.validate(sru_configuration)

    


class AND(CQLBooleanOperatorBase):
    operator = "and"


class OR(CQLBooleanOperatorBase):
    operator = "or"


class NOT(CQLBooleanOperatorBase):
    operator = "not"


class PROX(CQLBooleanOperatorBase):
    operator = "prox"
