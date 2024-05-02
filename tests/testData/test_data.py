import json

from src.sru_queryer.sru import SortKey
from src.sru_queryer.sru import SRUConfiguration

mock_searchable_indexes_and_descriptions_loc_data = {
  "cql": {
    "anywhere": {
      "id": "1016",
      "title": "Keyword Anywhere",
      "sort": None,
      "supported_relations": [],
      "empty_term_supported": None
    }
  },
  "dc": {
    "title": {
      "id": "4",
      "title": "Title",
      "sort": None,
      "supported_relations": [],
      "empty_term_supported": None
    },
    "creator": {
      "id": "1003",
      "title": "Creator",
      "sort": None,
      "supported_relations": [],
      "empty_term_supported": None
    },
    "author": {
      "id": "1003",
      "title": "Creator",
      "sort": None,
      "supported_relations": [],
      "empty_term_supported": None
    },
    "subject": {
      "id": "21",
      "title": "Subject",
      "sort": None,
      "supported_relations": [],
      "empty_term_supported": None
    }
  },
  "bath": {
    "name": {
      "id": "1002",
      "title": "Name",
      "sort": None,
      "supported_relations": [],
      "empty_term_supported": None
    },
    "personalName": {
      "id": "1",
      "title": "Personal Name",
      "sort": None,
      "supported_relations": [],
      "empty_term_supported": None
    },
    "corporateName": {
      "id": "2",
      "title": "Corporate Name",
      "sort": None,
      "supported_relations": [],
      "empty_term_supported": None
    },
    "conferenceName": {
      "id": "3",
      "title": "Conference Name",
      "sort": None,
      "supported_relations": [],
      "empty_term_supported": None
    },
    "geographicName": {
      "id": "58",
      "title": "Geographic Name",
      "sort": None,
      "supported_relations": [],
      "empty_term_supported": None
    },
    "isbn": {
      "id": "7",
      "title": "ISBN",
      "sort": None,
      "supported_relations": [],
      "empty_term_supported": None
    },
    "issn": {
      "id": "8",
      "title": "ISSN",
      "sort": None,
      "supported_relations": [],
      "empty_term_supported": None
    },
    "lccn": {
      "id": "9",
      "title": "LC Control Number",
      "sort": None,
      "supported_relations": [],
      "empty_term_supported": None
    },
    "standardIdentifier": {
      "id": "1007",
      "title": "Standard Identifier",
      "sort": None,
      "supported_relations": [],
      "empty_term_supported": None
    }
  }
}

test_available_record_schemas = {
    "marcxml": {
        "identifier": "http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd",
        "sort": True
    }, "dc": {
       "identifier": "info:srw/schema/1/dc-v1.1",
       "sort": True
    }, "mods": {
       "identifier": "info:srw/schema/1/mods-v3.5",
       "sort": True
    }, "dcx": {
       "identifier": "info:srw/schema/1/dcx-v1.0",
       "sort": True
    }, "unimarcxml": {
       "identifier": "info:srw/schema/8/unimarcxml-v0.1",
       "sort": True
    }, "kormarcxml": {
       "identifier": "http://www.nl.go.kr/kormarc/",
       "sort": True
    }, "cnmarcxml": {
       "identifier": "http://www.nlc.cn/",
       "sort": True
    }, "isohold": {
       "identifier": "http://www.loc.gov/standards/iso20775/",
       "sort": True
    }
}

test_available_record_schemas_gapines = {
    "marcxml": {
        "identifier": "http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd",
        "sort": True
    }, "dc": {
       "identifier": "info:srw/schema/1/dc-v1.1",
       "sort": True
    }, "mods": {
       "identifier": "info:srw/schema/1/mods-v3.5",
       "sort": True
    }, "dcx": {
       "identifier": "info:srw/schema/1/dcx-v1.0",
       "sort": True
    }, "unimarcxml": {
       "identifier": "info:srw/schema/8/unimarcxml-v0.1",
       "sort": True
    }, "kormarcxml": {
       "identifier": "http://www.nl.go.kr/kormarc/",
       "sort": True
    }, "cnmarcxml": {
       "identifier": "http://www.nlc.cn/",
       "sort": True
    }, "isohold": {
       "identifier": "http://www.loc.gov/standards/iso20775/",
       "sort": True
    }
}

mock_searchable_indexes_and_descriptions = {
    "alma": {
        "bib_holding_count": {
            "id": None,
            "title": "Bib Holding Count (Alma)",
            "sort": True,
            "supported_relations": [">", ">=", "==", "<", "<="],
            "empty_term_supported": True
        },
        "general_note": {
            "id": None,
            "title": "Public Note (Title)",
            "sort": False,
            "supported_relations": ["all", "=", "=="],
            "empty_term_supported": False
        },
        "library": {
            "id": None,
            "title": "Library Code",
            "sort": False,
            "supported_relations": ["==", "all"],
            "empty_term_supported": True
        },
        "library_status": {
            "id": None,
            "title": "Library Status",
            "sort": False,
            "supported_relations": ["==", "all"],
            "empty_term_supported": True
        },
        "unique_serial_title": {
            "id": None,
            "title": "Serial Title",
            "sort": False,
            "supported_relations": ["all", "=", "=="],
            "empty_term_supported": False
        },
        "title": {
            "id": None,
            "title": "Title",
            "sort": True,
            "supported_relations": ["all", "=", "=="],
            "empty_term_supported": True
        },
    },
    "rec": {
            "mms_id": {
                "id": None,
                "title": "Bib MMS ID",
                "sort": False,
                "supported_relations": ["==", "all"],
                "empty_term_supported": True
            }
        }
}

# test_available_record_schemas = {'marcxml': {'sort': True}, 'dc': {'sort': True}, 'mods': {'sort': True}, 'dcx': {'sort': True}, 'unimarcxml': {'sort': True}, 'kormarcxml': {'sort': True}, 'cnmarcxml': {'sort': True}, 'isohold': {'sort': True}}
test_available_record_schemas_one_false = {
    "marcxml": {
        "identifier": "http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd",
        "sort": True
    }, "dc": {
       "identifier": "info:srw/schema/1/dc-v1.1",
       "sort": True
    }, "mods": {
       "identifier": "info:srw/schema/1/mods-v3.5",
       "sort": True
    }, "dcx": {
       "identifier": "info:srw/schema/1/dcx-v1.0",
       "sort": True
    }, "unimarcxml": {
       "identifier": "info:srw/schema/8/unimarcxml-v0.1",
       "sort": True
    }, "kormarcxml": {
       "identifier": "http://www.nl.go.kr/kormarc/",
       "sort": True
    }, "cnmarcxml": {
       "identifier": "http://www.nlc.cn/",
       "sort": False
    }, "isohold": {
       "identifier": "http://www.loc.gov/standards/iso20775/",
       "sort": True
    }
}

class MockSortKeyOne(SortKey):
  def __init__(*args, **kwargs):
      pass
  def format(*args):
      return "title,dc,0"
            
class MockSortKeyTwo(SortKey):
  def __init__(*args, **kwargs):
      pass
  def format(*args):
      return "name,bath,,,abort"
  
def get_alma_sru_configuration() -> SRUConfiguration:
    sru_configuration = SRUConfiguration()

    with open (TestFiles.alma_available_context_sets_and_indexes, "r") as f:  
        sru_configuration.available_context_sets_and_indexes = json.loads(f.read())
    
    sru_configuration.available_record_schemas = test_available_record_schemas

    sru_configuration.default_context_set = None
    sru_configuration.default_record_schema = None
    sru_configuration.default_relation = None
    sru_configuration.default_sort_schema = None
    sru_configuration.default_index = None
    sru_configuration.max_records_supported = 50
    sru_configuration.default_records_returned = 10
    sru_configuration.sru_version = "1.2"

    return sru_configuration

def get_gapines_sru_configuration() -> SRUConfiguration:
    sru_configuration = SRUConfiguration()

    with open (TestFiles.gapines_available_context_sets_and_indexes, "r") as f:  
        sru_configuration.available_context_sets_and_indexes = json.loads(f.read())
    
    sru_configuration.available_record_schemas = test_available_record_schemas

    sru_configuration.default_context_set = "eg"
    sru_configuration.default_record_schema = "marcxml"
    sru_configuration.default_relation = "all"
    sru_configuration.default_sort_schema = "marcxml"
    sru_configuration.default_index = "keyword"
    sru_configuration.max_records_supported = 50
    sru_configuration.default_records_returned = 10
    sru_configuration.sru_version = "1.1"

    return sru_configuration

def get_test_sru_configuration_no_sort_or_supported_relations_or_config() -> SRUConfiguration:
    sru_configuration = SRUConfiguration()

    with open (TestFiles.loc_available_context_sets_and_indexes, "r") as f:  
        sru_configuration.available_context_sets_and_indexes = json.loads(f.read())
    
    sru_configuration.available_record_schemas = test_available_record_schemas

    sru_configuration.default_context_set = None
    sru_configuration.default_record_schema = None
    sru_configuration.default_relation = None
    sru_configuration.default_sort_schema = None
    sru_configuration.default_index = None
    sru_configuration.max_records_supported = None
    sru_configuration.default_records_returned = None
    sru_configuration.sru_version = "1.1"

    return sru_configuration

class TestFiles:
  explain_response_alma = "./tests/testData/alma_explain_response.xml"
  alma_bad_explain_response = "tests/testData/alma_bad_explain_response.xml"
  alma_raw_indexes = "./tests/testData/alma_raw_indexes.json"
  alma_raw_schemas = "./tests/testData/alma_raw_schemas.json"
  alma_raw_config_info = "./tests/testData/alma_raw_config_info.json"
  alma_available_context_sets_and_indexes = "./tests/testData/alma_available_context_sets_and_indexes.json"

  explain_response_loc = "./tests/testData/loc_explain_response.xml"
  loc_bad_explain_response = "tests/testData/loc_bad_explain_response.xml"
  loc_raw_indexes = "./tests/testData/loc_raw_indexes.json"
  loc_raw_schemas = "./tests/testData/loc_raw_schemas.json"
  loc_available_context_sets_and_indexes = "./tests/testData/loc_available_context_sets_and_indexes.json"

  explain_response_gapines = "./tests/testData/gapines_explain_response.xml"
  gapines_html_response = "./tests/testData/gapines_html_response.html"
  gapines_raw_indexes = "./tests/testData/gapines_raw_indexes.json"
  gapines_raw_config_info = "./tests/testData/gapines_raw_config_info.json"
  gapines_available_context_sets_and_indexes= "./tests/testData/gapines_available_context_sets_and_indexes.json"