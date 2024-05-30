from unittest import TestCase

from src.sru_queryer._base._sru_configuration import SRUConfiguration
from tests.testData.test_data import get_gapines_sru_configuration

class TestSRUConfiguration(TestCase):

    def test_configuration_to_dict(self):
        configuration = get_gapines_sru_configuration()

        configuration_dict = configuration.__dict__

        self.assertDictEqual(configuration_dict, {
            "available_context_sets_and_indexes": configuration.available_context_sets_and_indexes,
            "available_record_schemas": configuration.available_record_schemas,
            "supported_relation_modifiers": configuration.supported_relation_modifiers,
            "default_context_set": configuration.default_context_set,
            "disable_validation_for_cql_defaults": configuration.disable_validation_for_cql_defaults,
            "default_relation": configuration.default_relation,
            "default_index": configuration.default_index,
            "default_record_schema": configuration.default_record_schema,
            "default_sort_schema": configuration.default_sort_schema,
            "default_records_returned": configuration.default_records_returned,
            "max_records_supported": configuration.max_records_supported,
            "available_record_packing_values": configuration.available_record_packing_values,
            "server_url": configuration.server_url,
            "sru_version": configuration.sru_version,
            "username": configuration.username,
            "password": configuration.password,
        })

    def test_configuration_from_dict(self):
        configuration = get_gapines_sru_configuration()
        saved_dict = {
            "available_context_sets_and_indexes": configuration.available_context_sets_and_indexes,
            "available_record_schemas": configuration.available_record_schemas,
            "supported_relation_modifiers": configuration.supported_relation_modifiers,
            "default_context_set": configuration.default_context_set,
            "disable_validation_for_cql_defaults": configuration.disable_validation_for_cql_defaults,
            "default_relation": configuration.default_relation,
            "default_index": configuration.default_index,
            "default_record_schema": configuration.default_record_schema,
            "default_sort_schema": configuration.default_sort_schema,
            "default_records_returned": configuration.default_records_returned,
            "max_records_supported": configuration.max_records_supported,
            "available_record_packing_values": configuration.available_record_packing_values,
            "server_url": configuration.server_url,
            "sru_version": configuration.sru_version,
            "username": configuration.username,
            "password": configuration.password,
        }

        configuration_from_saved_dict = SRUConfiguration(saved_dict)

        self.assertDictEqual(configuration.__dict__, configuration_from_saved_dict.__dict__)