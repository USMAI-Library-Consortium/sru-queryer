import unittest

from src.sru_queryer.sru import SortKey
from tests.testData.test_data import MockSortKeyOne, MockSortKeyTwo

class TestSortKey(unittest.TestCase):

    def test_initialize_sort_key(self):
        sort_key = SortKey(xpath = "title", schema="", ascending=True, case_sensitive=False, missing_value="abort")

        self.assertEqual(sort_key._xpath, "title")
        self.assertEqual(sort_key._schema, "")
        self.assertEqual(sort_key._ascending, True)
        self.assertEqual(sort_key._case_sensitive, False)
        self.assertEqual(sort_key._missing_value, "abort")


    def test_initialize_sort_key_invalid_missing_value(self):
        with self.assertRaises(ValueError) as ve:
            SortKey(xpath="title", missing_value="invalidval")

        self.assertEqual(ve.exception.__str__(), "Value 'invalidval' is not a valid option for 'missing value.'")

    def test_initialize_sort_key_valid_constant_missing_value(self):
        sort_key = SortKey(xpath="title", missing_value='"constant"')

        self.assertEqual(sort_key._missing_value, '"constant"')

    def test_format_sort_key_only_xpath(self):
        sort_key = SortKey("test_path")

        formatted_sort_key = sort_key.format()

        self.assertEqual(formatted_sort_key, "test_path")

    def test_format_sort_key_with_schema(self):
        sort_key = SortKey("test_path", schema="test_schema")

        formatted_sort_key = sort_key.format()

        self.assertEqual(formatted_sort_key, "test_path,test_schema")

    def test_format_sort_key_with_schema_and_ascending(self):
        sort_key = SortKey("test_path", schema="test_schema", ascending=False)

        formatted_sort_key = sort_key.format()

        self.assertEqual(formatted_sort_key, "test_path,test_schema,0")

    def test_format_sort_key_with_schema_and_ascending_and_case_sensitive(self):
        sort_key = SortKey("test_path", schema="test_schema", ascending=False, case_sensitive=False)

        formatted_sort_key = sort_key.format()

        self.assertEqual(formatted_sort_key, "test_path,test_schema,0,0")

    def test_format_sort_key_with_schema_and_ascending_and_case_sensitive_and_missing_value(self):
        sort_key = SortKey("test_path", schema="test_schema", ascending=False, case_sensitive=False, missing_value="omit")

        formatted_sort_key = sort_key.format()

        self.assertEqual(formatted_sort_key, "test_path,test_schema,0,0,omit")

    def test_format_sort_key_only_missing_value(self):
        sort_key = SortKey("test_path", missing_value="omit")

        formatted_sort_key = sort_key.format()

        self.assertEqual(formatted_sort_key, "test_path,,,,omit")

    def test_format_sort_key_only_ascending(self):
        sort_key = SortKey("test_path", ascending=True)

        formatted_sort_key = sort_key.format()

        self.assertEqual(formatted_sort_key, "test_path,,1")

    def test_format_sort_key_ascending_case_sensitive(self):
        sort_key = SortKey("test_path", ascending=True, case_sensitive=True)

        formatted_sort_key = sort_key.format()

        self.assertEqual(formatted_sort_key, "test_path,,1,1")

    def test_format_array_of_sort_keys(self):
        sort_keys = [MockSortKeyOne("title", "dc", False), MockSortKeyTwo("name", "bath", missing_value="abort")]

        formatted_sort_keys = SortKey.format_array(sort_keys)

        self.assertEqual(formatted_sort_keys, "title,dc,0%20name,bath,,,abort")

