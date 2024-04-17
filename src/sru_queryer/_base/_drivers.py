# The drivers for parsing the xml explainResponse. These are the higherachy of the key names in the explainResponse
# once it has been parsed by xmltodict

loc_driver = {
    "name": "LOC driver",
    "indexInfo": {
        'indexInfoLocation': ['zs:explainResponse', 'zs:record', 'zs:recordData', 'explain', 'indexInfo', 'index'],
        # Relative to the index info location above
        "sortLocation": None,
        "idLocation": ["@id"], 
        "titleLocation": ["title"],
        "supportedOperationsLocation": None,
        # Relative to map location (hard-coded to ...indexInfoLocation["map"])
        "nameLocation": ["name", "#text"],
        "setLocation": ["name", "@set"]
    },
    "schemaInfo": {
        "schemaInfoLocation": ["zs:explainResponse", "zs:record", "zs:recordData", "explain", "schemaInfo", "schema"]
    },
    "configInfo": {
        "configInfoLocation": None,
        # Relative to config info location. LOC does not need it because it
        # has no config info.
        "defaultsLocation": None,
        "settingsLocation": None,
        "supportsLocation": None
    }
}

alma_driver = {
    "name": "Alma Driver",
    "indexInfo": {
        'indexInfoLocation': ["explainResponse", "record", "recordData", "explain", "indexInfo", "index"],
        # Relative to the index info location above
        "sortLocation": ["@sort"],
        "idLocation": None, 
        "titleLocation": ["ns:title"],
        "supportedOperationsLocation": ["configInfo", "supports"],
        # Relative to map location (hard-coded to ...indexInfoLocation["map"])
        "nameLocation": ["name", "#text"],
        "setLocation": ["name", "@set"]
    },
    "schemaInfo": {
        "schemaInfoLocation": ["explainResponse", "record", "recordData", "explain", "schemaInfo", "schema"]
    },
    "configInfo": {
        "configInfoLocation": ["explainResponse", "record", "recordData", "explain", "configInfo"],
        # Relative to config info location. 
        "defaultsLocation": ["ns:default"],
        "settingsLocation": ["ns:setting"],
        "supportsLocation": ["ns:supports"]
    }
}

gapines_driver = {
    "name": "Gapines Driver",
    "indexInfo": {
        'indexInfoLocation': ['explainResponse', 'record', 'recordData', 'explain', 'indexInfo', 'index'],
        # Relative to the index info location above
        "sortLocation": None,
        "idLocation": ["@id"], 
        "titleLocation": ["title"],
        "supportedOperationsLocation": ["configInfo", "supports"],
        # Relative to map location (hard-coded to ...indexInfoLocation["map"])
        "nameLocation": ["name", "#text"],
        "setLocation": ["name", "@set"]
    },
    "schemaInfo": {
        "schemaInfoLocation": ["explainResponse", "record", "recordData", "explain", "schemaInfo", "schema"]
    },
    "configInfo": {
        "configInfoLocation": ["explainResponse", "record", "recordData", "explain", "configInfo"],
        # Relative to config info location. 
        "defaultsLocation": ["default"],
        "settingsLocation": ["setting"],
        "supportsLocation": ["supports"]
    }
}