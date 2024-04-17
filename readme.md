# USMAI SRU Queryer

Welcome to SRU Queryer, a library for working with Search/Retrieval via URL (SRU) created by the USMAI Library Consortium. This package is designed to make working with SRU simple and accurate!

Using this utility has a few big benefits, such as:

1. It handles validating much of the searchRetrieve request. This is particularly helpful because many SRU servers don't have good error messages.
2. It handles formatting the searchRetrieve request for you. This makes queries much less prone to human mistakes.
3. It provides functions to see which indexes are available to search in the SRU server.

## TABLE OF CONTENTS

1. [Setting Up The Environment](#setting-up-the-environment)
2. [Basic Usage](#basic-usage)
3. [Quick Overview of Important Components](#quick-overview-of-important-components)
   1. [Initializing SRU Functionality](#initializing-sru-functionality)
   2. [Basic Query Component](#basic-query-component-indexquery)
   3. [Configuration Service](#configuration-service-sruutil)
   4. [Query class](#creating-queries---the-query-class)
   5. [Boolean Operators for Queries](#constructing-more-advanced-queries-boolean-operators)
4. [Full Overview of Different Components](#full-overview-of-different-components)
   1. [IndexQuery](#basic-query-component-indexquery-1)
   2. [SRUUtil](#sruutil)
   3. [Boolean Operators (AND, OR, NOT, PROX)](#constructing-more-advanced-queries-boolean-operators-1)
   4. [Query](#query-class)
   5. [LITERAL](#custom-queries-literal)
   6. [Modifiers](#modifiying-operators---modifiers)
   7. [Sorting in v1.2](#sorting-in-12-sortby-clauses)
   8. [Sorting in v1.1](#sorting-in-11-SortKey)

## Setting Up The Environment

This python script was developed using python 3.10 and tested on python 3.11.1.

To install sru-queryer, just run `pip install sru-queryer`

## Basic Usage

Here's just a basic usage example:

```
# Create a configuration object for the SRU server, allowing you to validate and send queries.
sru_configuration = SRUUtil.create_configuration_for_server("https://path-to-sru-server-base", "https://path-to-sru-server-base", "1.2")

# Configure a query - in this case, find records where the creator includes Abraham, sorted alphabetically & ascending.
query_obj = Query(sru_configuration, IndexQuery(
        "alma", "creator", "=", "Abraham"), sort_queries=[{
            "index_set": "alma",
            "index_name": "creator",
            "sort_order": "ascending"
        }])

# Validate the query to see whether it's valid
query_obj.validate()

# Construct the request (just a python PreparedRequest object)
request = query_obj.construct_request()

s = Session()
response = s.send(request)
```

This code will send the following query:
https://path-to-sru-server-base/?version=1.2&operation=searchRetrieve&recordSchema=marcxml&maximumRecords=10&query=alma.creator=%22Abraham%22%20sortBy%20alma.creator/sort.ascending

You can also create a query with boolean conditions:

```
# Find records where the creator includes Abraham AND the material type is 'book'
query_obj = Query(sru_configuration, AND(IndexQuery("alma", "creator", "=", "Abraham"), IndexQuery("alma", "materialType", "==", "BOOK")))
```

## Quick Overview of Important Components:

### Initializing SRU functionality

Before you can validate or send searchRetrieve requests, you must create an SRU configuration for your server. The configuration of this server will be in the form of an SRUConfiguration class.

An instance is created through the SRUUtil.create_configuration_for_server() function, and all you have to do is to pass the created instance to the functions that need it. You can read information from it if you want to integrate SRU querying more deeply into your application.

```
from sru_queryer.drivers import alma_driver
sru_configuration = SRUUtil.create_configuration_for_server("https://path-to-sru-server-base", "https://path-to-sru-server-base", "1.2", driver=alma_driver)
```

This is the most basic way to create a configuration object. The first argument is the SRU explain URL, the second is the searchRetrieve URL, the third is the SRU version, and the final one is the driver. This function takes many other optional arguments, which can do things like configure the default record schemas, default context sets, change validation settings, etc.

A very important argument is 'driver'. This takes a dict which tells the program how to parse explainResponses. This program already includes drivers for ExLibris Alma, LOC, and gapines SRU servers. The default is set to 'alma' (ExLibris Alma), which is why you won't see it in some examples. The drivers are straightforward - you can follow the template of the included drivers to create one for your own server. Drivers serve to tell the program where to find the information it needs in the SRU explainResponse and which information is available.

### Basic Query Component: IndexQuery

`from sru_queryer import IndexQuery`

This would more officially be known as a 'CQL search clause': https://www.loc.gov/standards/sru/cql/spec.html.\
A standard CQL search clause looks like: `alma.title="Harry Potter"`. This same query with the IndexQuery class would look like: `IndexQuery("alma", "title", "=", "Harry Potter")`

https://www.loc.gov/standards/sru/cql/spec.html

### Creating queries - the Query class

`from sru_queryer import Query`

Use the Query class to actually construct and validate a query.\
This class takes the SRU configuration as an argument, followed by the actual CQL query made up of boolean operators, Literals, and IndexQueries. You can also set certain values that you might want to change between queries while keeping the same SRUConfiguration - record format, start record, maximum records, etc. It also takes sort queries.

```
query_obj = Query(sru_configuration, IndexQuery(
        "alma", "creator", "=", "Abraham"), sort_queries=[{
            "index_set": "alma",
            "index_name": "creator",
            "sort_order": "ascending"
        }])
```

### Constructing more advanced queries: Boolean Operators

`from sru_queryer.cql import AND, OR, NOT, PROX`

Boolean Operators are used to construct queries with one or more IndexQueries. Their usage is extrememly simply by design, and should be familiar to people working with logic-based programming.

For example, the query:
`OR(IndexQuery("alma", "title", "=", "Harry"), IndexQuery("alma", "title", "=", "Potter"))`
will produce the following string, when formatted:
`alma.title="Harry" or alma.title="Potter"` (except spaces will be replaced with '%20')

---

## Full Overview of Different Components

This section will give a deep dive on each different component in sru_queryer. Check here if you can't figure something out!

### Basic Query Component: IndexQuery

`from sru_queryer import IndexQuery`

A SRU query, written in CQL, is made up of one or more queries on Indexes - here called an IndexQuery. Formatted, an index query looks like:

`alma.title="Harry Potter"`

The four components of this query are the context_set (`alma`), the index (`title`), the operation(`=`, called 'relation' officially), and the value (`Harry Potter`, called 'search term' officially). For more information, please see https://www.loc.gov/standards/sru/cql/spec.html. I won't explain the nuances of SRU/CQL here, just my implementation of it.

#### USAGE

All of the options for initializing an IndexQuery are keyword arguments, but are listed in an order that's the same as a standard index query (aside from modifiers).
This means you can initialize an IndexQuery in a human-readable way without including any keywords:
`IndexQuery("alma", "title", "=", "Harry Potter")`
which looks like the formatted query:
`alma.title="Harry Potter"`.

For queries without all options, you have to include the option name for each option OR include 'None' where the option would be.
Query with only a value:
`IndexQuery(value="Harry Potter")` or `IndexQuery(None, None, None, "Harry Potter")`
Query without a context_set:
`IndexQuery(index_name="title", operation="=", value="Harry Potter")` or
`IndexQuery(None, "title", "=", "Harry Potter")`

Keep in mind, if a context_set or index_name is not provided, the defaults must be set manually though SRUUtil for validation to work. This is because the explainResponse does not include the default context set or index. If you do not know them, there are options to disable validation for IndexQueries that use defaults.

#### AVAILABLE FUNCTIONS

You don't need to use any functions on an IndexQuery as a general user. For instance, the Query.validate() function will also run the validate() function for all included IndexQueries.

#### INITIALIZATION OPTIONS

Internal variables are private once initialized - if you change them, you will bypass some validation and likely cause errors. It's easy to create a new instance of IndexQuery if you need different options, so do that instead of modifying an existing one.

| Option      | Data Type                 | Mandatory | Description                                                                          |
| ----------- | ------------------------- | --------- | ------------------------------------------------------------------------------------ |
| context_set | string / None             | No        | The context set to search in.                                                        |
| index_name  | string / None             | No        | The index you want to search.                                                        |
| operation   | string / None             | No        | The operator ("=", ">", etc) you want to search with.                                |
| value       | string                    | Yes       | The value you're looking for.                                                        |
| modifiers   | list of RelationModifiers | No        | A list of relation modifiers for the operation. More information on modifiers below. |

COMBINATIONS OF INITIALIZATION PROPERTIES (according to LOC standards):
You MUST include either:

1. a value,
2. an index_name, operation, and value,
3. a context_set, index_name, operation, and value.

- RelationModifiers can be set for all combinations, but will only added to the final query on combinations with an operation.

### SRUUtil

`from sru_queryer import SRUUtil`

The SRUUtil static class handles core configuration for this utility, as well as providing an interface for reading the configuration information.

#### AVAILABLE FUNCTIONS:

There are two functions that the general user would want to use:

1. `format_available_indexes` - This function nicely formats all the indexes availabe for an SRU server, as well as their information. It then prints this information to the console, to a text file, or both. It only prints to the console by default. You can filter the indexes based on their human-readable title.

`format_available_indexes(sru_configuration, filename: str | None = None, print_to_console: bool = True, title_filter: str | None = None)`

2. `create_configuration_for_server` - This function creates an SRUConfiguration object by reading you provide as arguments to the function, pulling values found by contacting the SRU server, and reconciling them. Many arguments are optional and are used for improved validation of the SRU queries. Be aware that any option you specify manually will override the corresponding value returned by the explainResponse, if the explainResponse contains this value.

Arguments for create_configuration_for_server:

`explain_url`
| Mandatory | Data Type | Description |
| ---------- | --------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Yes | url string | The base URL for the explainResponse. This must not include any query params - they will be added by the utility. |

`search_retrieve_url`
| Mandatory | Data Type | Description |
| ---------- | --------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Yes | url string | The base URL for the searchRetrieve query. This must not include any query params - they will be added by the utility. |

`sru_version`
| Mandatory | Data Type | Description |
| ---------- | --------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Yes, but defaults to 1.2 | string | The SRU version to use.|

`driver`
| Mandatory | Data Type | Description |
| --- | --- | --- |
| Yes, but defaults to Alma driver | dict | The driver for parsing the xml explainResponse. This is needed because different SRU servers have their data located in different XML paths. The driver tells the program where to look. The drivers are arrays of strings, each string representing a key in a higherarchical dictionary. The drivers will be run on the explainResponse AFTER it's been parsed by the xmltodict library. Additional drivers can be imported from `sru_queryer.drivers` |

`username`
| Mandatory | Data Type | Description |
| ---------- | --------- | ------------------------------------------------------------------------------------------------------------------------------- |
| No | string | The username for the SRU server, if the server requires authentication. This is sent in Basic Access Authentication format. |

`password`
| Mandatory | Data Type | Description |
| ---------- | --------- | ------------------------------------------------------------------------------------------------------------------------------- |
| No (unless there's a username) | string | The password for the SRU server, if the server requires authentication. This is sent in Basic Access Authentication format. |

`default_cql_context_set`
| Mandatory | Data Type | Description |
| ---------- | --------- | ------------------------------------------------------------------------------------------------------------------------------- |
| No | string | The default context set for indexes if one is not provided. Adding a default enables validation for IndexQueries without context sets. For example, if the default context set is set to 'alma', this will validate the query `title="Harry Potter"` as if it were `alma.title="Harry Potter"`. The default MUST be the same as the default context set for your SRU server. Some SRU servers return this information in the explainResponse; others don't.|

`default_cql_index`
| Mandatory | Data Type | Description |
| ---------- | --------- | ------------------------------------------------------------------------------------------------------------------------------- |
| No | string |The default index for an IndexQuery if only a value is provided. If you have a default_cql_index, you must also have a default_cql_context_set. For example, if the default context set is 'alma' and the default index is 'title', the query `"Harry Potter"` will be validated as `alma.title "Harry Potter"`. |

`default_cql_relation`
| Mandatory | Data Type | Description |
| ---------- | --------- | ------------------------------------------------------------------------------------------------------------------------------- |
| No | string |The default relation for an IndexQuery if only a value is provided. If you have a default_cql_relation, you must also have a default_cql_context_set and index. For example, if the default context set is 'alma' and the default index is 'title', the query `"Harry Potter"` will be validated as `alma.title="Harry Potter"`. Not all SRU servers list valid relations for index queries, so this is ONLY NECCESARY when validating defaults for servers that do. If you server does not, you can safely ignore this even if you don't disable validation for cql defaults.|

`disable_validation_for_cql_defaults`
| Mandatory | Data Type | Description |
| ---------- | --------- | ------------------------------------------------------------------------------------------------------------------------------- |
| No | boolean | If you don't know the default context set, index, and relation (if relation information for indexes is specified) for your SRU server, yet you still want to send IndexQueries with default values, this setting will allow for that. It will disable any validation for indexQuery defaults, but allow validation for non-defaults. |

`max_records_supported`
| Mandatory | Data Type | Description |
| ---------- | --------- | ------------------------------------------------------------------------------------------------------------------------------- |
| No | int | This indicates the maximum number of records a searchRetrieve response is capable of returning. This is often returned by the explainResponse. If your server's maximum is not included in its explainResponse, it is recommended to include this value. Without it, the number of records requested in a query will not be validated correctly. |

`default_records_returned`
| Mandatory | Data Type | Description |
| ---------- | --------- | ------------------------------------------------------------------------------------------------------------------------------- |
| No | int | This indicates the default maximum number of records that the searchRetrieve will return. It must be equal to or less than the max_records_supported. If set, every query will return a maximum of this number of records. By default, it is set to whatever SRUUtil finds in the explainResponse OR, if not specified in the explainResponse, will not be included. |

`default_record_schema`
| Mandatory | Data Type | Description |
| ---------- | --------- | ------------------------------------------------------------------------------------------------------------------------------- |
| No | string | The default record schema that's returned by the searchRetrieve operation. If you don't specify what record schema you want in an individual query, the default record schema (if set) will be used in that query. If the explainResponse includes a default record schema and you don't specify one, the explainResponse's record schema will be included in all queries. |

`default_sort_schema`
| Mandatory | Data Type | Description |
| ---------- | --------- | ------------------------------------------------------------------------------------------------------------------------------- |
| No | string | The default schema that sort operations are run on. I don't know too much about this. I use it for validating sortKeys, which are only for version 1.1. If the sort schema is not included in a sort key, this value will be used to validate the sort key (not all schemas can sort).|

### Constructing more advanced queries: Boolean Operators

`from sru_queryer.cql import AND, OR, NOT, PROX`

Boolean Operators are used to construct queries with one or more IndexQueries. Their usage is extrememly simply by design, and should be familiar to people working with logic-based programming.

#### USAGE

Each operator takes an unlimited quantity of arguments, each of which represents a logical condition. Each condition can be an IndexQuery, a Literal (discussed below), or another nested Boolean Operator.

For example, the query:
`OR(IndexQuery("alma", "title", "=", "Harry"), IndexQuery("alma", "title", "=", "Potter"))`
will produce the following string, when formatted:
`alma.title="Harry" or alma.title="Potter"` (except spaces will be replaced with '%20')

If you nest one Boolean Operator within another, the resultant behavior will depend on whether the nested boolean operator has one condition or whether it has multiple conditions.

1. If the nested operator has one condition, it will REPLACE the preceeding boolean operator of the parent. This allows you to create a long query with alternating boolean operators:
   `AND(IndexQuery("alma", "title", "=", "Maryland"), OR(IndexQuery("alma", "materialType", "==", "BOOK")), IndexQuery("alma", "main_pub_date", ">", "1975"))`
   Procduces:
   `alma.title="Maryland" or alma.materialType=="BOOK" and alma.main_pub_date>"1975"` (again, spaces replaced with '%20')

   \*\* KEEP IN MIND that you can't have an operator with one condition as the first condition of a parent operator (or as the top condition). This wouldn't make sense because all operators require 2 conditions (none are unary operators, even NOT. Not is treated as 'and-not'). Here, I allow operators with one conditions so that a parent's operator can be overridden - this makes formatting simpler.

2. If the nested operator has more than one condition, it will be surrounded by parenthesis and the parent's operator will be placed before the parenthesis:
   `AND(IndexQuery("alma", "title", "=", "Maryland"), OR(IndexQuery("alma", "materialType", "==", "BOOK"), IndexQuery("alma", "materialType", "==", "DVD")))`
   Produces:
   `alma.title="Maryland" and (alma.materialType=="BOOK" or alma.materialType=="DVD")`

You may add modifiers to the Boolean Operator with the 'modifiers' keyword argument. Please use the correct modifier type for the boolean operator you've chosen - for example, the PROX modifier should use ProxModifier, whereas AND, OR, and NOT should use the AndOrNotModifier. You may create custom modifiers by extending the CQLModifierBase class. More on Modifiers later.

#### AVAILABLE FUNCTIONS

As with the IndexQuery, the functions on the CQL Boolean Operators are not indended to be used by the general person. For example, Query.construct_request() will call format() for all boolean operators.

#### INITIALIZATION OPTIONS

Any options not marked as MANDATORY are optional. It is not recommended to change any options manually after initializing a CQL Boolean Operator, as this will bypass some validation. It's easy to create a new instance of CQL Boolean Operator if you need different options.

| Option                   | Data Type                                                      | Mandatory | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| ------------------------ | -------------------------------------------------------------- | --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Positional arguments 1-n | IndexQuery, class extending CQLBooleanOperatorBase, or LITERAL | Yes       | Search clauses, which will be joined by the boolean operator. Must have at least one, or two if it is the outermost condition or first condition in a parent operator.                                                                                                                                                                                                                                                                                                                                                                                                                  |
| modifiers                | list[Class extending CQLModifierBase]                          | No        | A list of modifiers for the boolean operator, which will be tacked on to the end of the operator. Keep in mind that modifiers will be added to each instance of the formatted operator - if there's 3 conditions in the operator, leading to two 'and' conditions, this list will be included for both 'and's. To get around this, you may use a nested Boolean Operator with one condition and add the modifiers to that operator. In this case, it will replace the parent's operator with its own, which has the modifiers. The rest of the parent's operators will not be affected. |

Note: Literals may work in place of modifiers, however, this has not been tested.

### Query class

`from sru_queryer import Query`

Now, for the class which you'll likely use the most - the Query class. Whereas SRUUtil deals with configuration, Query only deals with one specific query. It takes an instance of SRUUtil for the purposes of validation.

#### USAGE

Use the Query class to construct your request.
Instantiate the SRUUtil class:
`configuration = SRUUtil.construct_configuration_for_server(...)`
Create the query class with the desired request:
`query_util = Query(configuration, OR(IndexQuery("alma", "title", "=", "Harry"), IndexQuery("alma", "title", "=", "Potter")), record_schema="marcxml")`

There are additional options to you can set to modify the request. They will be discussed below.

You can then validate the request with the validate() function, which will throw an error for the first issue it finds:
`query_util.validate()`

After this, you can get a PreparedRequest and send it:
`from requests import Session`
`request_to_send = query_util.construct_request()`
`s = Session()`
`response = s.send(request_to_send)`

This will return an XML response, which might be a searchRetrieve response, or might be an error.

#### AVAILABLE FUNCTIONS

validate: Validates all components of the searchRetrieve request that can be validated. For the query itself, this is a recursive function that validates all CQLBooleanOperators / IndexQueries and their children. It will throw a ValueError an error for the first issue it finds. It returns nothing when successful.

construct_request: Uses all components of the query to construct a searchRetrieve request. It pulls some of the information from the SRUConfiguration, including the base URL, username, password, and version, as well as other defaults that have been specified. Returns a requests.PreparedRequest object.

#### INITIALIZATION OPTIONS

Unlike many other classes, it is safe to modify variables after instantiating. This is because no validation occurs in the constructor. If you do change something, you'd just have to remember to run validate() again.

| Option            | Data Type                                                      | Mandatory | Description                                                                                                                                                                                                                                                           |
| ----------------- | -------------------------------------------------------------- | --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| sru_configuration | SRUConfiguration                                               | Yes       | The configuration of the SRU server, which is used to construct and validate queries. Create a configuration with SRUUtil's create_configuration_for_server()                                                                                                         |
| index_search      | IndexQuery, class extending CQLBooleanOperatorBase, or LITERAL | Yes       | The CQL query you wish to execute.                                                                                                                                                                                                                                    |
| start_record      | int                                                            | No        | An offset - Every search produces a set on the server, but not all will be returned. This determines the first record in that set that will be returned (offset).                                                                                                     |
| maximum_records   | int                                                            | No        | Set maximum amount of records that will be returned. The default for this, if not included, can be set through SRUUtil.create_configuration_for_server, by the explainResponse, or is set to 5.                                                                       |
| record_schema     | string                                                         | No        | The format in which the searchRetrieveRessponse will return records. Default is 'marcxml.' Any value set here will be validated against the available record schemas listed in the explainResponse. REQUIRED if the default is not returned with the explainResponse. |
| sort_queries      | list[dict] or list[SortKey]                                    | No        | A list of sortBy dictionaries, which add sort clauses to the dictionary. See below for more information.                                                                                                                                                              |
| record_packing    | string                                                         | No        | The record packing that the record will be returned in (either xml or string)                                                                                                                                                                                         |

### Custom queries: LITERAL

`from sru_queryer.cql import LITERAL`

USE ONLY WHEN NEEDED! The LITERAL class allows you to pass a string directly to the SRU query. THE STRING WILL NOT BE VALIDATED.

Literals are intended for cases in which this library does not support a certain SRU feature OR to bypass a bugged output format.

Using a literal allows you to insert whatever search condition you need, while still validating the rest of the query. You can use a literal to replace the entire search query, replace a boolean conditional, or replace an IndexQuery.

You don't have to worry about creating the string in exact URL notation (e.g., replacing ' ' with %20 or '"' with %22). Characters will be encoded automatically by Query.construct_request().

#### USAGE

Use a literal in place of an IndexQuery or class extending CQLBooleanOperatorBase (AND, OR, NOT, PROX).

Here's an example of a literal being used instead of an IndexQuery in an AND boolean operator:
`AND(IndexQuery("alma", "title", "=", "Maryland"), LITERAL("alma.materialType==BOOK"))`

Here's an example of a literal replacing a CQLBooleanOperator and its IndexQueries:
`LITERAL('alma.title="Maryland" and (alma.materialType=="BOOK" or alma.materialType=="DVD")')`

You can't pass an IndexQuery or a CQLBooleanOperator to a literal and have them be nested inside of it, in the way you can nest CQLBooleanOperators/IndexQueries inside CQLBooleanOperators. You COULD format them in when constructing the literal using string formatting:
`LITERAL(f'{index_query_1.format()} and {cql_boolean_operator.format()}')`
...where index_query_1 and cql_boolean_operator are instantiated IndexQuery and CQLBooleanOperatorBase objects.

However, keep in mind that this will disable validation for those inner objects.

#### AVAILABLE FUNCTIONS

There's nothing here that you would want to use. This class is essentially a wrapper around a string which allows it to be interchangable with IndexQueries and CQLBooleanOperators.

#### INITIALIZATION OPTIONS

| Option         | Data Type              | Mandatory | Description                                                                                                                                                                                                                           |
| -------------- | ---------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| literal_string | string (should be CQL) | Yes       | The string that you want to be executed. Again, you don't have to provide it in a url-exact format, spaces and other special characters will be replaced by their compability characters later on if you're using the provided tools. |
| add_padding    | boolean                | No        | Whether or not to add a space (%20) before and after the string upon formatting. Set to false by default.                                                                                                                             |

### Modifiying operators - Modifiers

Modifiers are conditions which modify the search query operators (AND, "all", OR, etc). As indicated above, in version 1.2, they can either modify IndexQuery operators or Boolean Operators.

Each modifier is preceeded by a '/' and optional spacing. One or many modifiers may be included. Modifiers must include a base_name, but MAY include a context_set, operator, and value.

From the LOC website, a modifier on a Boolean Operator looks like: `dc.title any fish or/rel.combine=sum dc.creator any sanderson`.
A modifier on an IndexQuery looks like `any /relevant /cql.string`

One thought of interest - it may be possible to include a LITERAL instead of a modifier for custom modifiers / modifier formats not available through this program. I've not tested it, but it's likely to work.

#### USAGE

This utility comes with 3 standard modifiers - AndOrNotModifier (for CQL Boolean Operators AND, OR, and NOT), ProxModifier (for CQL Boolean Operator PROX), and RelationModifier (for any IndexQuery relation).

These modifiers differ mainly in validation. The ProxModifier limits the base_name to either 'unit' or 'distance', as these are the base names used by prox, and limits the values for the 'unit' base name in the CQL context set to the values specified in the LOC documentation. Upon validation, an error will be raised if these values are not correct.

This program will NOT validate modifiers in relation to one another - e.g., even though a prox must have one 'unit' and one 'distance' modifier, this is not enforced through validation. You could extend the CQLBooleanOperatorBase or PROX class to create this custom validation, if desired.

Example prox modifier:
`ProxModifier('unit', "=", "sentence", context_set="cql")`
\*Using the keyword for context set here is optional. I'm just showing it to make the order clear - it's rearranged slightly as compared to an IndexQuery.

The RelationModifier works in the same way.

Modifiers are added as an array to either IndexQueries or CQLBooleanOperatorBase classes.

#### AVAILABLE FUNCTIONS

There are no functions here that the general user should need to use.

#### INITIALIZATION OPTIONS

It is not recommended to change any options manually after initializing a Modifier, as this will bypass some validation. It's easy and not resource intensive to create a new instance of a modifier if you need different options.

| Option      | Data Type      | Mandatory | Description                                                                                                             |
| ----------- | -------------- | --------- | ----------------------------------------------------------------------------------------------------------------------- |
| base_name   | string         | Yes       | The base name of the modifier (e.g, 'relevant' in `/relevant`). Validated against the whitelist 'supported_base_names'. |
| operator    | string or None | No        | The operator used in the modifier condition.                                                                            |
| value       | string or None | No        | The value used in the modifier condition.                                                                               |
| context_set | string or None | No        | The context set that the base_name should be pulled from.                                                               |

COMBINATIONS OF INITIALIZATION PROPERTIES (implied from LOC standards):
You MUST include either:

1. a base_name,
2. a context_set, base_name
3. a base_name, operation, and value,
4. a context_set, base_name, operation, and value.

### Sorting in 1.2: SortBy clauses

sortBy clauses are simply Python dictionaries with the form:
`{ "index_set": "alma", "index_name": "creator", "sort_order": "ascending" }`
Which will be formatted to:
`sortBy%20alma.creator/sort.ascending`

All values are required. The sort_order can either be "ascending" or "descending."

You should add all desired sortBy clauses to the Query object in an array with the keyword argument 'sort_queries='

### Sorting in 1.1: SortKey

`from sru_queryer.sru import SortKey`

SortKeys are used to sort results returned by a searchRetrieve request ins SRU version 1.1. SRU 1.1 doesn't specify whether sorting is allow per-index like 1.2 does; rather, it specifies this per record schema.

Note that this isn't imported from CQL. It's actually not part of the CQL query - it's another URL query string parameter.

#### USAGE

Simply include a list of SortKeys in the 'sort_queries' parameter of your Query object. They will be automatically validated and formatted.

#### AVAILABLE FUNCTIONS

There's nothing here that you would need to use; the built-in functions are used by other parts of the SRUUtil program.

#### INITIALIZATION OPTIONS

| Option         | Data Type | Mandatory | Description                                                                                            |
| -------------- | --------- | --------- | ------------------------------------------------------------------------------------------------------ |
| xpath          | string    | Yes       | The xpath of the index you want to sort by. It's just the index name prefixed by the context set.      |
| schema         | string    | No        | The record schema you want to search by                                                                |
| ascending      | boolean   | No        | Whether you want the results to be ascending. Default is True, False will set results to be descending |
| case_sensitive | boolean   | No        | If case should be important during the search. Default is False.                                       |
