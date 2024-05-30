from __future__ import annotations

from ._sru_configuration import SRUConfiguration
from ._sru_validator import SRUValidator
from ._cql_modifiers import CQLModifierBase, RelationModifier

class SearchClause:
    """A CQL clause.

    Supports validation of context set, index_name, relation, and whether 
    or not an empty string is allowed as a search_term for a particular index.

    To create a valid search clause, you must use:\n
        a search_term,\n
        index_name + relation + search_term,\n
        OR context_set + index_name + relation + search_term.\n

    Modifiers will only be included if there's an relation.
        """

    def __init__(self, context_set: str | None = None, index_name: str | None = None, relation: str | None = None, search_term: str | None = None, modifiers: list[RelationModifier] | None = None, from_dict: dict | None = None):
        self._context_set: str = context_set
        self._index_name: str = index_name
        self._relation: str = relation
        self._search_term: str = search_term
        self._modifiers = modifiers

        if from_dict:
            try:
                if from_dict["type"] != "searchClause":
                    raise KeyError()
                self._context_set: str = from_dict["context_set"]
                self._index_name: str = from_dict["index_name"]
                self._relation: str = from_dict["relation"]
                self._search_term: str = from_dict["search_term"]
            except KeyError:
                raise ValueError(f"Invalid dictionary for creating a search clause: '{from_dict.__str__()}'")

        search_term_exists = self._search_term != None
        if not search_term_exists:
            raise ValueError("You must provide a search term (search_term)")

        if self._index_name and not self._relation:
            raise ValueError(
                "If you include an index, you must include an relation")
        if self._relation and not self._index_name:
            raise ValueError(
                "If you include an relation, you must include an index")
        if self._context_set and not self._index_name:
            raise ValueError(
                "If you have a context set, you must include an index.")

    def get_index_name(self):
        return self._index_name

    def get_relation(self):
        return self._relation

    def format(self):
        return self._format()

    def _format_relation(self) -> str:
        """Formats the relational relation

        append a space before and AFTER IF there's no modifiers:\n
            %20any%20 (no modifiers)\n
            %20and    (with modifiers)\n
        """
        formatted_relation = ""

        if self._relation:
            formatted_relation = self._relation
            formatted_relation = f'%20{formatted_relation}'

            # add padding for the relations that are words
            if not self._modifiers:
                formatted_relation += "%20"

        return formatted_relation

    def _format(self, **kwargs):
        formatted_search_clause = ""

        if self._context_set:
            formatted_search_clause += f'{self._context_set}.'

        if self._index_name:
            formatted_search_clause += f'{self._index_name}{self._format_relation()}'

        # Format the modifiers
        formatted_search_clause += CQLModifierBase.format_modifier_array(
            self._modifiers)

        # The index search_term will always be added
        formatted_search_clause += f'"{self._search_term}"'

        return formatted_search_clause

    def validate(self, sru_configuration: SRUConfiguration):
        SRUValidator.validate_cql(sru_configuration, self._context_set,
            self._index_name, self._relation, self._search_term)

        if self._modifiers:
            for modifier in self._modifiers:
                modifier.validate(sru_configuration)