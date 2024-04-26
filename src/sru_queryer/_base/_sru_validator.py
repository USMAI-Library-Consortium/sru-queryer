from __future__ import annotations

from abc import ABC, abstractmethod

from ._sru_configuration import SRUConfiguration
from ._sort_key import SortKey

class SRUValidatorAbstract(ABC):
    @staticmethod
    @abstractmethod
    def validate_defaults(sru_configuration: SRUConfiguration, default_context_set: str | None, default_index: str | None, default_relation: str | None, default_record_schema: str | None, default_sort_schema: str | None):
        pass

    @staticmethod
    @abstractmethod
    def validate_cql(sru_configuration: SRUConfiguration, context_set: str | None = None, index_name: str | None = None, relation: str | None = None, value: str | None = None, evaluate_can_sort: bool = False) -> None:
        pass

    @staticmethod
    @abstractmethod
    def validate_base_query(sru_configuration: SRUConfiguration, start_record: str | None, maximum_record: str | None, record_schema: str | None, record_packing: str | None) -> None:
        pass 

    @staticmethod
    @abstractmethod
    def validate_context_set(sru_configuration: SRUConfiguration, context_set: str) -> None:
        pass

    @staticmethod
    @abstractmethod
    def validate_sort(sru_configuration: SRUConfiguration, sort_queries: list[dict] | list[SortKey], record_schema: str | None = None) -> None:
        pass

class SRUValidator(SRUValidatorAbstract):

    @staticmethod
    def validate_defaults(sru_configuration: SRUConfiguration):
        # Validate default index, context set, and relation
        information_exists_for_cql_defaults = sru_configuration.default_context_set != None
        if not sru_configuration.disable_validation_for_cql_defaults and information_exists_for_cql_defaults:
            SRUValidator.validate_cql(sru_configuration, sru_configuration.default_context_set, sru_configuration.default_index, sru_configuration.default_relation)

        # Validate default record schema
        record_schema_valid = SRUValidator._validate_record_schema(sru_configuration.available_record_schemas, sru_configuration.default_record_schema)
        if not record_schema_valid:
            raise ValueError(f"Record schema '{sru_configuration.default_record_schema}' is not available.")
        
        # Validate default sort schema
        default_sort_schema = sru_configuration.default_sort_schema
        sort_schema_valid = SRUValidator._validate_record_schema(sru_configuration.available_record_schemas, default_sort_schema)
        if not sort_schema_valid:
            raise ValueError(f"Sort schema '{default_sort_schema}' is not available.")
        
        if default_sort_schema:
            sort_schema_info = sru_configuration.available_record_schemas[default_sort_schema]
            if sort_schema_info["sort"] is False:
                raise ValueError(f"Schema {default_sort_schema} cannot sort.")

    
    @staticmethod
    def validate_cql(sru_configuration: SRUConfiguration, context_set: str | None = None, index_name: str | None = None, relation: str | None = None, value: str | None = None, evaluate_can_sort: bool = False) -> None:
        no_context_set = context_set is None
        no_index = index_name is None
        no_relation = relation is None
        no_default_context_set = sru_configuration.default_context_set is None
        no_default_index = sru_configuration.default_index is None
        no_default_relation = sru_configuration.default_relation is None
        validation_for_defaults_enabled = sru_configuration.disable_validation_for_cql_defaults is False

        context_set_to_evaluate = context_set
        index_to_evaluate = index_name
        relation_to_evaluate = relation

        no_context_set_info = no_context_set and no_default_context_set
        no_index_info = no_index and no_default_index
        no_relation_info = no_relation and no_default_relation

        if (no_context_set_info or no_index_info) and validation_for_defaults_enabled:
            if no_context_set_info:
                raise ValueError("Cannot validate context set 'None'; ensure you have set a default context set or have disabled validation for cql defaults.")
            
            if no_index_info:
                raise ValueError("Cannot validate index 'None'; ensure you have set a default index or have disabled validation for cql defaults.")

        if no_context_set:
            if not validation_for_defaults_enabled:
                return
            context_set_to_evaluate = sru_configuration.default_context_set
        SRUValidator.validate_context_set(sru_configuration, context_set_to_evaluate)
        
        if no_index:
            if not validation_for_defaults_enabled:
                return
            index_to_evaluate = sru_configuration.default_index
        if index_to_evaluate not in sru_configuration.available_context_sets_and_indexes[context_set_to_evaluate]:
            raise ValueError(f"Index '{index_to_evaluate}' not available on context set '{context_set_to_evaluate}'")
    
        index_info = sru_configuration.available_context_sets_and_indexes[context_set_to_evaluate][index_to_evaluate]

        # Evaluate whether the index can sort.
        if evaluate_can_sort:
            if index_info["sort"] is False:
                raise ValueError(f"Index '{index_to_evaluate}' in context set '{context_set_to_evaluate}' does not support sorting.")
            return
        
        # Evaluate the relation, if specified
        relation_info_included_in_index = index_info["supported_operations"]
        if relation_info_included_in_index and no_relation_info:
            raise ValueError("Cannot validate relation 'None'; ensure you have set a default relation or have disabled validation for cql defaults.")
            
        relation_is_valid = SRUValidator._validate_relation(relation_to_evaluate, index_info)
        if not relation_is_valid:
            raise ValueError(f"Relation '{relation_to_evaluate}' is not supported on index '{index_to_evaluate}' in context set '{context_set_to_evaluate}'")
            
        # Evaluate the value. This checks for 'empty term supported'. So if the value is an empty 
        # string and empty term is not supported, this will raise an error. 
        value_is_valid = SRUValidator._validate_value(value, index_info)
        if not value_is_valid:
            raise ValueError(f"Index '{index_to_evaluate}' in context set '{context_set_to_evaluate}' does not support empty terms.")
                
            
    @staticmethod
    def validate_base_query(sru_configuration: SRUConfiguration, start_record: str | None, maximum_record: str | None, record_schema: str | None, record_packing: str | None) -> None:
        if start_record and start_record < 1:
            raise ValueError("Start record must be greater than 0.")

        if maximum_record and sru_configuration.max_records_supported:
            if maximum_record > sru_configuration.max_records_supported:
                raise ValueError(f"Maximum records returned must be less than {str(sru_configuration.max_records_supported)}.") 
        
        if record_schema:
            if record_schema not in sru_configuration.available_record_schemas:
                raise ValueError(f"Record schema '{record_schema}' is not available.")
            
        if record_packing:
            if record_packing not in sru_configuration.available_record_packing_values:
                raise ValueError(f"Record packing value '{record_packing}' is not available.")

    @staticmethod
    def validate_context_set(sru_configuration: SRUConfiguration, context_set: str) -> None:
        if context_set not in sru_configuration.available_context_sets_and_indexes:
            raise ValueError(f"Context set '{context_set}' is not available.")
    
    @staticmethod
    def validate_sort(sru_configuration: SRUConfiguration, sort_queries: list[dict] | list[SortKey], record_schema: str | None = None) -> None:
        """Validates a sortBy clause."""
        if not sort_queries:
            return
        
        if isinstance(sort_queries[0], SortKey):
            SRUValidator._validate_1_1_sort(sru_configuration.available_record_schemas, sort_queries, record_schema)
            return
        else:
            SRUValidator._validate_1_2_sort(sru_configuration, sort_queries)


    @staticmethod
    def _validate_record_schema(available_record_schemas: dict, schema: str) -> bool:
        if schema:
            if schema not in available_record_schemas:
                return False
        return True
    
    @staticmethod
    def _validate_relation(relation: str | None, index_info: dict) -> bool:
        if relation != None:
            relation_information_included_in_index = index_info["supported_operations"]
            
            if relation_information_included_in_index:
                if relation not in index_info["supported_operations"]:
                    return False
        return True
    
    @staticmethod
    def _validate_value(value: str | None, index_info: dict) -> bool:
        if value != None:
            index_info_contains_value_info = index_info["empty_term_supported"] != None

            if index_info_contains_value_info:
                if value == "" and index_info["empty_term_supported"] is False:
                    return False
        
        return True
    
    @staticmethod
    def _validate_1_1_sort(available_record_schemas: dict, sort_keys: list[SortKey], record_schema: str):
        # Here, we want to see whether the SCHEMA is available to
        # sort, as well as validate the xpath/index

        for sort_key in sort_keys:
            record_schema_to_evaluate = record_schema
            sort_key_schema_is_specified = sort_key._schema != None

            if sort_key_schema_is_specified:
                record_schema_to_evaluate = sort_key._schema
            record_schema_exists = record_schema_to_evaluate in available_record_schemas

            if record_schema_exists:
                record_schema_info = available_record_schemas[record_schema_to_evaluate]
                record_schema_cannot_sort = record_schema_info["sort"] is False
                
                if record_schema_cannot_sort:
                    raise ValueError(f"Record schema '{record_schema_to_evaluate}' is not available to sort!")
            else:
                raise ValueError(f"Record schema '{record_schema_to_evaluate}' is not valid.")

    @staticmethod
    def _validate_1_2_sort(sru_configuration: SRUConfiguration, sort_bys: list[dict]):
        index_names_already_sorted = []

        for i, sort in enumerate(sort_bys):
            index_set = sort["index_set"]
            index_name = sort["index_name"]
            sort_order = sort["sort_order"]

            if sort_order not in ["ascending", "descending"]:
                raise ValueError(
                    f"Sort order '{sort_order}' in sort index {str(i+1)} is invalid!")

            # See whether the index can sort. If not, throw an error.
            SRUValidator.validate_cql(sru_configuration, index_name=index_name, context_set=index_set, evaluate_can_sort=True)

            if index_name in index_names_already_sorted:
                raise ValueError("You cannot repeat index names in a sort.")

            index_names_already_sorted.append(index_name)