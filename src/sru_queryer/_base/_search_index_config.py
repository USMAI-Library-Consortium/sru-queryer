from __future__ import annotations

from ._sru_configuration import SRUConfiguration
from ._sru_validator import SRUValidator
from ._cql_modifiers import CQLModifierBase, RelationModifier

class IndexQuery:
    """A query of an index.

    Supports validation of context set, index_name, operation, and whether 
    or not an empty string is allowed as a value for a particular index.

    To create a valid query, you must use:\n
        a value,\n
        index_name + operation + value,\n
        OR context_set + index_name + operation + value.\n

    Modifiers will only be included if there's an operation.
        """

    def __init__(self, context_set: str | None = None, index_name: str | None = None, operation: str | None = None, value: str | None = None, modifiers: list[RelationModifier] | None = None):
        self._context_set: str = context_set
        self._index_name: str = index_name
        self._operation: str = operation
        self._value: str = value
        self._modifiers = modifiers

        value_exists = value != None
        if not value_exists:
            raise ValueError("You must provide a search term (value)")

        if index_name and not operation:
            raise ValueError(
                "If you include an index, you must include an operation")
        if operation and not index_name:
            raise ValueError(
                "If you include an operation, you must include an index")
        if context_set and not index_name:
            raise ValueError(
                "If you have a context set, you must include an index.")

    def get_index_name(self):
        return self._index_name

    def get_operation(self):
        return self._operation

    def format(self):
        return self._format()

    def _format_operation(self) -> str:
        """Formats the relational operation

        For non-word relational operators (==, >, <>, etc), there should be no spacing, E.G.:\n
            ==\n
        For relational operators that are words (E.G., 'any'), append a space before and AFTER IF THERE'S NO MODIFIERS:\n
            %20any%20 (no modifiers)\n
            %20and    (with modifiers)\n
        """
        formatted_operation = ""

        if self._operation:
            formatted_operation = self._operation
            if formatted_operation in ["all"]:
                formatted_operation = f'%20{formatted_operation}'

                # add padding for the operations that are words
                if not self._modifiers:
                    formatted_operation += "%20"

        return formatted_operation

    def _format(self, **kwargs):
        formatted_index_query = ""

        if self._context_set:
            formatted_index_query += f'{self._context_set}.'

        if self._index_name:
            formatted_index_query += f'{self._index_name}{self._format_operation()}'

        # Format the modifiers
        formatted_index_query += CQLModifierBase.format_modifier_array(
            self._modifiers)

        # The index value will always be added
        formatted_index_query += f'"{self._value}"'

        return formatted_index_query

    def validate(self, sru_configuration: SRUConfiguration):
        SRUValidator.validate_cql(sru_configuration, self._context_set,
            self._index_name, self._operation, self._value)

        if self._modifiers:
            for modifier in self._modifiers:
                modifier.validate(sru_configuration)
