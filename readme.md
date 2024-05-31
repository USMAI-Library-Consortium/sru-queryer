# USMAI SRU Queryer

Welcome to SRU Queryer, a library for working with Search/Retrieval via URL (SRU) created by the USMAI Library Consortium. This package is designed to make working with SRU simple and accurate!

Using this utility has a few big benefits, such as:

1. It handles validating much of the searchRetrieve request. This is particularly helpful because many SRU servers don't have good error messages.
2. It handles formatting the searchRetrieve request for you. This makes queries much less prone to human mistakes.
3. Programmatically access the capabilities of the SRU server in your program.

## TABLE OF CONTENTS

1. [Setting Up The Environment](#setting-up-the-environment)
2. [Basic Usage](#basic-usage)
3. [Quick Overview of Important Components](#quick-overview-of-important-components)
   1. [Initializing SRU Functionality](#initializing-sru-functionality)
   2. [Basic Query Component](#basic-query-component-searchclause)
   3. [Searching using SRUQueryer](#searching-using-sruqueryer)
   4. [Boolean Operators for Queries](#constructing-more-advanced-queries-boolean-operators)
4. [Full Overview of Different Components](#full-overview-of-different-components)
   1. [SearchClause](#basic-query-component-searchclause-1)
   2. [SRUQueryer](#sruqueryer)
   3. [Boolean Operators (AND, OR, NOT, PROX)](#boolean-operators)
   4. [RawCQL](#custom-queries-rawcql)
   5. [Modifiers](#modifiying-operators---modifiers)
   6. [Sorting in v1.2](#sorting-in-12-sortby-clauses)
   7. [Sorting in v1.1](#sorting-in-11-SortKey)
5. [Integrating with APIs](#integrating-with-apis)
6. [Known Incompatibilities](#known-incompatibilities)

## Setting Up The Environment

To install sru-queryer, just run `pip install sru-queryer`

Note that you may have to specify pip3 if you have python2 installed. The install will fail if you try to use python2's PIP.

## Basic Usage

Here's just a basic usage example:

```
# Create a configuration object for the SRU server, allowing you to validate and send queries.
queryer = SRUQueryer("https://path-to-sru-server-base")

# Configure a SearchRetrieve query - in this case, find records where the creator includes Abraham, sorted alphabetically & ascending.
response_content = queryer.search_retrieve(SearchClause("alma", "creator", "=", "Abraham"),
                     sort_queries=[{
                           "index_set": "alma",
                           "index_name": "creator",
                           "sort_order": "ascending"
                     }])
```

This code will send the following query:
https://path-to-sru-server-base/?version=1.2&operation=searchRetrieve&recordSchema=marcxml&maximumRecords=10&query=alma.creator=%22Abraham%22%20sortBy%20alma.creator/sort.ascending

You can also create a query with boolean conditions:

```
# Find records where the creator includes Abraham AND the material type is 'book'
queryer.search_retrieve(sru_configuration, AND(SearchClause("alma", "creator", "=", "Abraham"), SearchClause("alma", "materialType", "==", "BOOK")))
```

## Quick Overview of Important Components:

### Initializing SRU functionality

Before you can validate or send searchRetrieve requests, you must create a queryer. Upon initialization, the queryer will contact your SRU server and set up everything it needs to validate and format your SRU queries.

```
queryer = SRUQueryer("https://path-to-sru-server-base")
```

This is the most basic way to create a queryer. This function takes many other optional arguments, which can do things like configure the default record schemas, default context sets, change validation settings, etc.

### Basic Query Component: SearchClause

`from sru_queryer.cql import SearchClause`

This is officially known as a 'CQL search clause': https://www.loc.gov/standards/sru/cql/spec.html <br>
A standard CQL search clause looks like: `alma.title="Harry Potter"`. This same query with the SearchClause class would look like: `SearchClause("alma", "title", "=", "Harry Potter")`. Pretty straightforward! See more in the extended SearchClause section below - there's rules for which of these arguments are required.

### Searching using SRUQueryer

`from sru_queryer import SRUQueryer`

There's two options for conducting searchRetrieve requests with the SRUQueryer class. <br>

First, you can have the queryer send the request for you and return the content. Once the querier is initialized, you can do so in this way (this is only an example search, it doesn't have to look exactly like this):

```
response_content = queryer.search_retrieve(SearchClause("alma", "creator", "=", "Abraham"),
         sort_queries=[{
            "index_set": "alma",
            "index_name": "creator",
            "sort_order": "ascending"
        }])
```

Alternately, you can construct a requests.Request object that you can then send yourself. This allows for a bit more flexibility, like adding a custom authentication header:

```
request = queryer.construct_search_retrieve_request(SearchClause(
        "alma", "creator", "=", "Abraham"), sort_queries=[{
            "index_set": "alma",
            "index_name": "creator",
            "sort_order": "ascending"
        }])
```

Both of these options take the same arguments. The first is the CQL query made up of boolean operators, RawCQL classes, and/or SearchClauses. You can also set certain values that you might want to change between queries while keeping the same queryer - record format, start record, maximum records, etc. It also takes sort queries.

### Constructing more advanced queries: Boolean Operators

`from sru_queryer.cql import AND, OR, NOT, PROX`

Boolean Operators are used to construct queries with one or more SearchClauses. Their usage is extrememly simply by design, and should be familiar to people working with logic-based programming.

For example, the query:
`OR(SearchClause("alma", "title", "=", "Harry"), SearchClause("alma", "title", "=", "Potter"))`
will produce the following string, when formatted:
`alma.title="Harry" or alma.title="Potter"` (except spaces will be replaced with '%20')

<br>
<br>

---

## Full Overview of Different Components

This section will give a deep dive on each different component in sru_queryer. Check here if you can't figure something out!

<br>

### Basic Query Component: SearchClause

`from sru_queryer import SearchClause`

A SRU query, written in CQL, is made up of one or more search clauses. Formatted, a search clause looks like:

`alma.title="Harry Potter"`

The four components of this query are the context_set (`alma`), the index (`title`), the relation(`=`), and the search term (`Harry Potter`). For more information, please see https://www.loc.gov/standards/sru/cql/spec.html. I won't explain the nuances of SRU/CQL here, just my implementation of it.

#### USAGE

All of the options for initializing a SearchClause are keyword arguments, but are listed in order.
This means you can initialize a SearchClause in a human-readable way without including any keywords:
`SearchClause("alma", "title", "=", "Harry Potter")`
which looks like the formatted query:
`alma.title="Harry Potter"`.

For SearchClauses without all options, you have to include the option name for each option OR include 'None' where the option would be.<br>
SearchClause with only a search term:<br>
`SearchClause(search_term="Harry Potter")` or `SearchClause(None, None, None, "Harry Potter")`<br>
SearchClause without a context_set:<br>
`SearchClause(index_name="title", relation="=", search_term="Harry Potter")` or <br>
`SearchClause(None, "title", "=", "Harry Potter")`

Keep in mind, if a context_set or index_name is not provided, the defaults must be set manually during initialization of SRUQueryer for validation to work. This is because the explainResponse does not always include the default context set or index. If you do not know them, there are options to disable validation for SearchClauses that use defaults.

#### AVAILABLE FUNCTIONS

You don't need to use any functions on a SearchClause as a general user. For instance, SRUQueryer will run the validate() function for all included SearchClauses.

#### INITIALIZATION OPTIONS

Internal variables are private once initialized - if you change them, you will bypass some validation and likely cause errors. It's easy to create a new instance of SearchClause if you need different options, so do that instead of modifying an existing one.

| Option      | Data Type                 | Mandatory | Description                                                                         |
| ----------- | ------------------------- | --------- | ----------------------------------------------------------------------------------- |
| context_set | string / None             | No        | The context set to search in.                                                       |
| index_name  | string / None             | No        | The index you want to search.                                                       |
| relation    | string / None             | No        | The operator ("=", ">", etc) you want to search with.                               |
| search_term | string                    | Yes       | The value you're looking for.                                                       |
| modifiers   | list of RelationModifiers | No        | A list of relation modifiers for the relation. More information on modifiers below. |

COMBINATIONS OF INITIALIZATION PROPERTIES (according to LOC standards):<br>
You MUST include either:

1. a search term,
2. an index_name, relation, and search term,
3. a context_set, index_name, relation, and search term.

- RelationModifiers can be set for all combinations, but will only added to the final query on combinations with an relation.

#### JSON / Dict representation

As part of the 'Integrating with APIs' functionality (The second-to-last section), this class has a corresponding dict representation. Internally, the library will use this dict to create a SearchClause object. Keep in mind that these are validated the same as the SearchClause class.

You MUST include 'type' for this to be recognized as a SearchClause. The same 'COMBINATIONS OF INITIALIZATION PROPERTIES' exist for this dict, and you don't need to include keys that you aren't specifying.

The format is as follows:

In JSON

```json
{
  "type": "searchClause",
  "context_set": "alma",
  "index_name": "title",
  "relation": "=",
  "search_term": "Maryland"
}
```

In Python

```python
{
  "type": "searchClause",
  "context_set": "alma",
  "index_name": "title",
  "relation": "=",
  "search_term": "Maryland"
}
```

<br>
<br>

### SRUQueryer

`from sru_queryer import SRUQueryer`

The SRUQueryer is the most important class of this library, as it handles configuring the utility as well as constructing, validating, and sending requests.

The SRUQueryer stores all its configuration information in an SRUConfiguration object in the property sru_configuration. If you want your program to know the capabilites of the SRU server, it can read the properties of queryer.sru_configuration. For instance, you can access the available record schemas with:<br>

`queryer.sru_configuration.available_record_schemas`<br>

It is HIGHLY recommended not to change any of these values.

#### INITIALIZATION OPTIONS

This function configures settings (stored in an SRUConfiguration object) by reading the arguments you provide, pulling values from the SRU server, and reconciling them. Many arguments are optional and are used for improved validation of the SRU queries. Be aware that any option you specify manually will override the corresponding value returned by the explainResponse, if the explainResponse contains this value.

If the SRU server returns a different SRU version than you the one you specify, the library will use that version. If you do not provide a version, it will default to version 1.2 or whatever the server is capable of.

`server_url`
| Mandatory | Data Type | Description |
| ---------- | --------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Yes | url string | The base URL for the server. This must not include any query params - they will be added by the utility. |

`sru_version`
| Mandatory | Data Type | Description |
| ---------- | --------- | ------------------------------------------------------------------------------------------------------------------------------- |
| No - defaults to 1.2 | string | The SRU version to use. If the SRU server returns a different SRU version than you specify, the tool will use that version. If you do not provide a version, it will default to version 1.2. |

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
| No | string | The default context set for indexes if one is not provided. Adding a default enables validation for SearchClauses without context sets. For example, if the default context set is set to 'alma', this will validate the query `title="Harry Potter"` as if it were `alma.title="Harry Potter"`. The default MUST be the same as the default context set for your SRU server. Some SRU servers return this information in the explainResponse; others don't.|

`default_cql_index`
| Mandatory | Data Type | Description |
| ---------- | --------- | ------------------------------------------------------------------------------------------------------------------------------- |
| No | string |The default index for a SearchClause if only a search term is provided. If you have a default_cql_index, you must also have a default_cql_context_set. For example, if the default context set is 'alma' and the default index is 'title', the query `"Harry Potter"` will be validated as `alma.title "Harry Potter"`. |

`default_cql_relation`
| Mandatory | Data Type | Description |
| ---------- | --------- | ------------------------------------------------------------------------------------------------------------------------------- |
| No | string |The default relation for a SearchClause if only a search term is provided. If you have a default_cql_relation, you must also have a default_cql_context_set and index. For example, if the default context set is 'alma' and the default index is 'title', the query `"Harry Potter"` will be validated as `alma.title="Harry Potter"`. Not all SRU servers list valid relations for SearchClauses, so this is ONLY NECCESARY when validating defaults for servers that do. If you server does not, you can safely ignore this even if you don't disable validation for cql defaults.|

`disable_validation_for_cql_defaults`
| Mandatory | Data Type | Description |
| ---------- | --------- | ------------------------------------------------------------------------------------------------------------------------------- |
| No | boolean | If you don't know the default context set, index, and relation (if relation information for indexes is specified) for your SRU server, yet you still want to send SearchClauses with defaults, this setting will allow for that. It will disable any validation for SearchClause defaults, but allow validation for non-defaults. |

`max_records_supported`
| Mandatory | Data Type | Description |
| ---------- | --------- | ------------------------------------------------------------------------------------------------------------------------------- |
| No | int | This indicates the maximum number of records a searchRetrieve response is capable of returning. This is often returned by the explainResponse. If your server's maximum is not included in its explainResponse, it is recommended to include this value. Without it, the number of records requested in a query will not be validated correctly. |

`default_records_returned`
| Mandatory | Data Type | Description |
| ---------- | --------- | ------------------------------------------------------------------------------------------------------------------------------- |
| No | int | This indicates the default maximum number of records that the searchRetrieve will return. It must be equal to or less than the max_records_supported. If set, every query will return a maximum of this number of records. By default, it is set to whatever is in the explainResponse OR, if not specified in the explainResponse, will not be included. |

`default_record_schema`
| Mandatory | Data Type | Description |
| ---------- | --------- | ------------------------------------------------------------------------------------------------------------------------------- |
| No | string | The default record schema that's returned by the searchRetrieve operation. If you don't specify what record schema you want in an individual query, the default record schema (if set) will be used in that query. If the explainResponse includes a default record schema and you don't specify one, the explainResponse's record schema will be included in all queries. |

`default_sort_schema`
| Mandatory | Data Type | Description |
| ---------- | --------- | ------------------------------------------------------------------------------------------------------------------------------- |
| No | string | The default schema that sort operations are run on. I don't know too much about this. I use it for validating sortKeys, which are only for version 1.1. If the sort schema is not included in a sort key, this value will be used to validate the sort key (not all schemas can sort).|

`from_dict`
| Mandatory | Data Type | Description |
| ---------- | --------- | ------------------------------------------------------------------------------------------------------------------------------- |
| No | dict | A python dictionary representing an SRU Configuration, which will be used INSTEAD of the above options + contacting the SRU server. Do not create this dictionary yourself; it is meant to re-load a saved configuration which is created with the get_configuration() function.|

#### AVAILABLE FUNCTIONS:

There are four functions that the general user would want to use:

##### `search_retrieve`

This function sends a search retrieve request, using the values you provide and the information parsed from the SRU ExplainResponse.

##### USAGE

After initializing your SRUQueryer class: <br>
`response_content = queryer.search_retrieve(OR(SearchClause("alma", "title", "=", "Harry"), SearchClause("alma", "title", "=", "Potter")), record_schema="marcxml")`

There are additional options to you can set to modify the request. They will be discussed below.

This will validate and send the request. You will receive whatever content the SRU server sends back - it may be a searchRetrieveResponse, or it might be an error. This library does not currently validate or parse the response.

##### INPUT PARAMETERS

| Option          | Data Type                                                       | Mandatory | Description                                                                                                                                                                                                                                                                                                                      |
| --------------- | --------------------------------------------------------------- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| cql_query       | SearchClause, class extending CQLBooleanOperatorBase, or RawCQL | Yes       | The CQL query you wish to execute.                                                                                                                                                                                                                                                                                               |
| start_record    | int                                                             | No        | An offset - Every search produces a set on the server, but not all will be returned. This determines the first record in that set that will be returned (offset).                                                                                                                                                                |
| maximum_records | int                                                             | No        | Set maximum amount of records that will be returned. The default for this, if not included, can be set through SRUQueryer initialization.create_configuration_for_server, by the explainResponse, or is set to 5.                                                                                                                |
| record_schema   | string                                                          | No        | The format in which the searchRetrieveRessponse will return records. Default is 'marcxml.' Any value set here will be validated against the available record schemas listed in the explainResponse. REQUIRED if the default is not returned with the explainResponse.                                                            |
| sort_queries    | list[dict] or list[SortKey]                                     | No        | A list of sortBy dictionaries, which add sort clauses to the dictionary. See below for more information.                                                                                                                                                                                                                         |
| record_packing  | string                                                          | No        | The record packing that the record will be returned in (either xml or string)                                                                                                                                                                                                                                                    |
| validate        | boolean (default True)                                          | No        | Whether or not to validate the query before sending it. You can disable validation if you think the library is falsely failing a query.                                                                                                                                                                                          |
| from_dict       | dict                                                            | No        | Use a dict representation of the query instead of the built-in CQL classes. This is useful for APIs in particular. See the 'Integrating with APIs' section for more info. You can still include any of the previous parameters aside from cql_query - they will apply but be overwritten by any values in the dict (if included) |

<br>

##### `construct_search_retrieve_request`

This does the same thing as the previous function, however instead of running request.prepare() and sending the request, it returns the requests.Request object. This allows you to be more flexible by modifying the request - for instance, if you want to use a shared requests.Session between multiple requests, or add a custom authentication header.

##### USAGE

After initializing your SRUQueryer class: <br>
`request = queryer.construct_search_retrieve_request(OR(SearchClause("alma", "title", "=", "Harry"), SearchClause("alma", "title", "=", "Potter")), record_schema="marcxml")`

This will validate the request and return a requests.Request object.

##### INPUT PARAMETERS

| Option          | Data Type                                                       | Mandatory | Description                                                                                                                                                                                                                                                                                                                      |
| --------------- | --------------------------------------------------------------- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| cql_query       | SearchClause, class extending CQLBooleanOperatorBase, or RawCQL | Yes       | The CQL query you wish to execute.                                                                                                                                                                                                                                                                                               |
| start_record    | int                                                             | No        | An offset - Every search produces a set on the server, but not all will be returned. This determines the first record in that set that will be returned (offset).                                                                                                                                                                |
| maximum_records | int                                                             | No        | Set maximum amount of records that will be returned. The default for this, if not included, can be set through SRUQueryer initialization.create_configuration_for_server, by the explainResponse, or is set to 5.                                                                                                                |
| record_schema   | string                                                          | No        | The format in which the searchRetrieveRessponse will return records. Default is 'marcxml.' Any value set here will be validated against the available record schemas listed in the explainResponse. REQUIRED if the default is not returned with the explainResponse.                                                            |
| sort_queries    | list[dict] or list[SortKey]                                     | No        | A list of sortBy dictionaries, which add sort clauses to the dictionary. See below for more information.                                                                                                                                                                                                                         |
| record_packing  | string                                                          | No        | The record packing that the record will be returned in (either xml or string)                                                                                                                                                                                                                                                    |
| validate        | boolean (default True)                                          | No        | Whether or not to validate the query before returning the requests.Request object. You can disable validation if you think the library is falsely failing a query.                                                                                                                                                               |
| from_dict       | dict                                                            | No        | Use a dict representation of the query instead of the built-in CQL classes. This is useful for APIs in particular. See the 'Integrating with APIs' section for more info. You can still include any of the previous parameters aside from cql_query - they will apply but be overwritten by any values in the dict (if included) |

##### `format_available_indexes`

This function nicely formats all the indexes availabe for an SRU server, as well as their information. It then prints this information to the console, to a text file, or both. It only prints to the console by default. You can filter the indexes based on their human-readable title.

`format_available_indexes(sru_configuration, filename: str | None = None, print_to_console: bool = True, title_filter: str | None = None)`

##### `get_configuration`

Gets a python dict representing the SRUQueryer. This allows saving the SRU queryer and allows you to re-create it without contacting the SRU server or setting the options again.

<br>
<br>

### Boolean Operators

`from sru_queryer.cql import AND, OR, NOT, PROX`

Boolean Operators are used to construct queries with one or more SearchClauses. Their usage is extrememly simply by design, and should be familiar to people working with logic-based programming.

#### USAGE

Each operator takes an unlimited quantity of arguments, each of which represents a logical condition. Each condition can be a SearchClause, a RawCQL class (discussed below), or another nested Boolean Operator.

For example, the query:
`OR(SearchClause("alma", "title", "=", "Harry"), SearchClause("alma", "title", "=", "Potter"))`
will produce the following string, when formatted:
`alma.title="Harry" or alma.title="Potter"` (except spaces will be replaced with '%20')

If you nest one Boolean Operator within another, the resultant behavior will depend on whether the nested boolean operator has one condition or whether it has multiple conditions.

1. If the nested operator has one condition, it will REPLACE the preceeding boolean operator of the parent. This allows you to create a long query with alternating boolean operators:
   `AND(SearchClause("alma", "title", "=", "Maryland"), OR(SearchClause("alma", "materialType", "==", "BOOK")), SearchClause("alma", "main_pub_date", ">", "1975"))`
   Procduces:
   `alma.title="Maryland" or alma.materialType=="BOOK" and alma.main_pub_date>"1975"` (again, spaces replaced with '%20')

   \*\* KEEP IN MIND that you can't have an operator with one condition as the first condition of a parent operator (or as the top condition). This wouldn't make sense because all operators require 2 conditions (none are unary operators, even NOT. Not is treated as 'and-not'). Here, I allow operators with one conditions so that a parent's operator can be overridden - this makes formatting simpler.

2. If the nested operator has more than one condition, it will be surrounded by parenthesis and the parent's operator will be placed before the parenthesis:
   `AND(SearchClause("alma", "title", "=", "Maryland"), OR(SearchClause("alma", "materialType", "==", "BOOK"), SearchClause("alma", "materialType", "==", "DVD")))`
   Produces:
   `alma.title="Maryland" and (alma.materialType=="BOOK" or alma.materialType=="DVD")`

You may add modifiers to the Boolean Operator with the 'modifiers' keyword argument. Please use the correct modifier type for the boolean operator you've chosen - for example, the PROX modifier should use ProxModifier, whereas AND, OR, and NOT should use the AndOrNotModifier. You may create custom modifiers by extending the CQLModifierBase class. More on Modifiers later.

#### AVAILABLE FUNCTIONS

As with the SearchClause, the functions on the CQL Boolean Operators are not indended to be used by the general person. For example, SRUQueryer.search_retrieve will call format() for all boolean operators.

#### INITIALIZATION OPTIONS

Any options not marked as MANDATORY are optional. It is not recommended to change any options manually after initializing a CQL Boolean Operator, as this will bypass some validation. It's easy to create a new instance of CQL Boolean Operator if you need different options.

| Option                   | Data Type                                                       | Mandatory | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| ------------------------ | --------------------------------------------------------------- | --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Positional arguments 1-n | SearchClause, class extending CQLBooleanOperatorBase, or RawCQL | Yes       | Search clauses, which will be joined by the boolean operator. Must have at least one, or two if it is the outermost condition or first condition in a parent operator.                                                                                                                                                                                                                                                                                                                                                                                                                  |
| modifiers                | list[Class extending CQLModifierBase]                           | No        | A list of modifiers for the boolean operator, which will be tacked on to the end of the operator. Keep in mind that modifiers will be added to each instance of the formatted operator - if there's 3 conditions in the operator, leading to two 'and' conditions, this list will be included for both 'and's. To get around this, you may use a nested Boolean Operator with one condition and add the modifiers to that operator. In this case, it will replace the parent's operator with its own, which has the modifiers. The rest of the parent's operators will not be affected. |

Note: RawCQL classes may work in place of modifiers, however, this has not been tested.

#### JSON / Dict representation

As part of the 'Integrating with APIs' functionality (The second-to-last section), this class has a corresponding dict representation. Internally, the library will use this dict to create a boolean operator object. Keep in mind that these are validated the same as the Boolean Operator class, so the requirements are all the same. This will NOT work with a custom boolean operator that extends the functionality of CQLBooleanOperatorBase.

You MUST include 'type' and 'operator' for a dict to be recognized as a Boolean Operator. The 'conditions' array, just like above, is required can contain SearchClause dicts, Boolean Operator dicts, or RawCQL dicts.

The format is as follows:

In JSON

```json
{
  "type": "booleanOperator",
  "operator": "AND",
  "conditions": []
}
```

In Python

```python
{
  "type": "booleanOperator",
  "operator": "AND",
  "conditions": []
}
```

<br>
<br>

### Custom queries: RawCQL

`from sru_queryer.cql import RawCQL`

USE ONLY WHEN NEEDED! The RawCQL class allows you to pass a string directly to the CQL query. THE STRING WILL NOT BE VALIDATED.

RawCQL is intended for cases in which this library does not support a certain SRU feature OR to bypass a bugged output format.

Using raw cql allows you to insert whatever search condition you need, while still validating the rest of the query. You can use a RawCQL class to replace the entire search query, replace a boolean conditional, or replace a SearchClause.

You don't have to worry about creating the string in exact URL notation (e.g., replacing ' ' with %20 or '"' with %22). Characters will be encoded automatically by SRUQueryer.search_retrieve().

#### USAGE

Use a RawCQL class in place of a SearchClause or class extending CQLBooleanOperatorBase (AND, OR, NOT, PROX).

Here's an example of a RawCQL class being used instead of a SearchClause in an AND boolean operator:
`AND(SearchClause("alma", "title", "=", "Maryland"), RawCQL("alma.materialType==BOOK"))`

Here's an example of a RawCQL class replacing a CQLBooleanOperator and its SearchClauses:
`RawCQL('alma.title="Maryland" and (alma.materialType=="BOOK" or alma.materialType=="DVD")')`

You can't pass a SearchClause or a CQLBooleanOperator to a RawCQL class and have them be nested inside of it, in the way you can nest CQLBooleanOperators/SearchClauses inside CQLBooleanOperators. You COULD format them in when constructing the RawCQL class using string formatting:
`RawCQL(f'{search_clause_1.format()} and {cql_boolean_operator.format()}')`
...where search_clause_1 and cql_boolean_operator are instantiated SearchClause and CQLBooleanOperatorBase objects.

However, keep in mind that this will disable validation for those inner objects.

#### AVAILABLE FUNCTIONS

There's nothing here that you would want to use. This class is essentially a wrapper around a string which allows it to be interchangable with SearchClauses and CQLBooleanOperators.

#### INITIALIZATION OPTIONS

| Option         | Data Type              | Mandatory | Description                                                                                                                                                                                                           |
| -------------- | ---------------------- | --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| raw_cql_string | string (should be CQL) | Yes       | A CQL query as a string. Again, you don't have to provide it in a url-exact format, spaces and other special characters will be replaced by their compability characters later on if you're using the provided tools. |
| add_padding    | boolean                | No        | Whether or not to add a space (%20) before and after the string upon formatting. Set to false by default.                                                                                                             |

#### JSON / Dict representation

As part of the 'Integrating with APIs' functionality (The second-to-last section), this class has a corresponding dict representation. Internally, the library will use this dict to create a RawCQL object. Keep in mind that this works the same as the above object EXCEPT that padding is automatically added.

You MUST include 'type' for this dict to be recognized as RawCQL. Both keys are required.

The format is as follows:

In JSON

```json
{
  "type": "rawCQL",
  "cql": "alma.title=Maryland"
}
```

In Python

```python
{
   "type": "rawCQL",
   "cql": "alma.title=Maryland"
}
```

<br>
<br>

### Modifiying operators - Modifiers

Modifiers are conditions which modify the search query operators (AND, "all", OR, etc). As indicated above, in version 1.2, they can either modify SearchClause relations or Boolean Operators.

Each modifier is preceeded by a '/' and optional spacing. One or many modifiers may be included. Modifiers must include a base_name, but MAY include a context_set, comparison symbol, and value.

From the LOC website, a modifier on a Boolean Operator looks like: <br>
`dc.title=fish or[/rel.combine=sum] dc.creator=sanderson`.<br>
A modifier on a SearchClause relation looks like:<br> `any /relevant /cql.string`

One thought of interest - it may be possible to include a RawCQL instead of a modifier if you want to create custom modifiers or modifier formats not available through this program. I've not tested it, but it's likely to work.

#### USAGE

This utility comes with 3 standard modifiers - AndOrNotModifier (for CQL Boolean Operators AND, OR, and NOT), ProxModifier (for CQL Boolean Operator PROX), and RelationModifier (for any SearchClause relation).

These modifiers differ mainly in validation. The ProxModifier limits the base_name to either 'unit' or 'distance', as these are the base names used by prox, and limits the values for the 'unit' base name in the CQL context set to the values specified in the LOC documentation. Upon validation, an error will be raised if these values are not correct.

This program will NOT validate combinations of modifiers - e.g., even though a 'PROX' boolean operator must have one 'unit' and one 'distance' modifier, this is not enforced through validation. You could extend the CQLBooleanOperatorBase or PROX class to create this custom validation, if desired.

Example prox modifier:
`ProxModifier('cql', 'unit', "=", "sentence")`
\*Using the keyword for context set here is optional. I'm just showing it to make the order clear - it's rearranged slightly as compared to a SearchClause.

The RelationModifier works in the same way.

Modifiers are added as an array to either SearchClauses or CQLBooleanOperatorBase classes.

#### AVAILABLE FUNCTIONS

There are no functions here that the general user should need to use.

#### INITIALIZATION OPTIONS

It is not recommended to change any options manually after initializing a Modifier, as this will bypass some validation. It's easy and not resource intensive to create a new instance of a modifier if you need different options.

| Option            | Data Type      | Mandatory | Description                                                     |
| ----------------- | -------------- | --------- | --------------------------------------------------------------- |
| context_set       | string or None | No        | The context set that the base_name should be pulled from.       |
| base_name         | string         | Yes       | The base name of the modifier (e.g, 'relevant' in `/relevant`). |
| comparison_symbol | string or None | No        | The comparison symbol used in the modifier condition.           |
| value             | string or None | No        | The value used in the modifier condition.                       |

COMBINATIONS OF INITIALIZATION PROPERTIES (implied from LOC standards):<br>
You MUST include either:

1. a base_name,
2. a context_set and base_name
3. a base_name, comparison_symbol, and value,
4. a context_set, base_name, comparison_symbol, and value.

<br>
<br>

### Sorting in 1.2: SortBy clauses

sortBy clauses are simply Python dictionaries with the form:
`{ "index_set": "alma", "index_name": "creator", "sort_order": "ascending" }`
Which will be formatted to:
`sortBy%20alma.creator/sort.ascending`

All values are required. The sort_order can either be "ascending" or "descending."

You should add all desired sortBy clauses to the SRUQueryer.search_retrieve or SRUQueryer.construct_search_retrieve_request in an array with the keyword argument 'sort_queries='

#### JSON / Dict representation

As part of the 'Integrating with APIs' functionality (The second-to-last section), this class has a unique dict representation for use with the from_dict option for searches. It's the same as the above, but with the addition of a 'type' key which tells the library what this dict should be treated as.

You MUST include 'type' for this dict to be recognized as a sortBy clause. As with the SortBy dict, all keys are required.

The format is as follows:

In JSON

```json
{
  "type": "sort",
  "index_set": "alma",
  "index_name": "creator",
  "sort_order": "ascending"
}
```

In Python

```python
{
   "type": "sort",
   "index_set": "alma",
   "index_name": "creator",
   "sort_order": "ascending"
}
```

<br>
<br>

### Sorting in 1.1: SortKey

`from sru_queryer.sru import SortKey`

SortKeys are used to sort results returned by a searchRetrieve request in SRU version 1.1. SRU 1.1 doesn't specify whether sorting is allow per-index like 1.2 does; rather, it specifies this per record schema.

Note that this isn't imported from sru_queryer.cql but rather sru_queryer.sru. This is because it's actually not part of the CQL query.

#### USAGE

Simply include a list of SortKeys in the 'sort_queries' parameter of your SearchRetrieve object. They will be automatically validated and formatted.

#### AVAILABLE FUNCTIONS

There's nothing here that you would need to use; the built-in functions are used by other parts of the sru_queryer library.

#### INITIALIZATION OPTIONS

| Option         | Data Type | Mandatory | Description                                                                                            |
| -------------- | --------- | --------- | ------------------------------------------------------------------------------------------------------ |
| xpath          | string    | Yes       | The xpath of the index you want to sort by. It's just the index name prefixed by the context set.      |
| schema         | string    | No        | The record schema you want to search by                                                                |
| ascending      | boolean   | No        | Whether you want the results to be ascending. Default is True, False will set results to be descending |
| case_sensitive | boolean   | No        | If case should be important during the search. Default is False.                                       |

#### JSON / Dict representation

As part of the 'Integrating with APIs' functionality (The second-to-last section), this class has a corresponding dict representation. Internally, the library will use this dict to create a SortKey object, so this dict will be used and validated in the same way as the SortKey object.

You MUST include 'type' for this dict to be recognized as a SortKey. The other options are the same as the SortKey class (only xpath is required). You don't need to include the keys you aren't specifying.

The format is as follows:

In JSON

```json
{
  "type": "sortKey",
  "xpath": "cql.author",
  "schema": "marcxml",
  "ascending": false,
  "case_sensitive": true,
  "missing_value": null
}
```

In Python

```python
{
   "type": "sortKey",
   "xpath": "cql.author",
   "schema": "marcxml",
   "ascending": False,
   "case_sensitive": True,
   "missing_value": None
}
```

<br>
<br>

---

## Integrating with APIs

New in version 2.1.0, this library has been significantly expanded to work with APIs. This includes:

1. The capability to import/export SRU configurations from JSON.
2. The ability for the queryer to accept a dictionary (parsed from JSON with json.loads() or created directly in Python) instead of the python objects mentioned above.

### Importing/Exporting SRU Configurations

This allows your application - particularly a web API - to easily save SRU configurations and use them between requests.

Exporting an SRU Configuration: `sru_configuration_dict = queryer.get_configuration()`<br>
Creating a queryer from a saved SRU configuration (Importing): `queryer = SRUQueryer(from_dict=sru_configuration_dict)`

### Conducting a SearchRetrieve Request with JSON

This makes creating dynamic queries a lot easier, particularly if you are using this library on a backend API. Just pass it the properly-formatted JSON dictionary, and it will validate the query just as if you have created it with the python objects mentioned above. Note that the required keys are the same for the dicts as the objects, so you can safely omit the ones you don't need.

Note - Modifiers are not supported with this method of interaction at this time.

#### Usage

Say you have some JSON, either from a file or coming in from an API. This is an example of a properly-formatted JSON dictionary that can be used by the library (SRU version 1.2):

```json
{
  "start_record": 4,
  "maximum_records": 3,
  "record_schema": "dc",
  "record_packing": null,
  "cql_query": {
    "type": "booleanOperator",
    "operator": "AND",
    "conditions": [
      {
        "type": "searchClause",
        "context_set": "alma",
        "index_name": "title",
        "relation": "=",
        "search_term": "Maryland"
      },
      {
        "type": "searchClause",
        "context_set": "alma",
        "index_name": "item_createDate",
        "relation": ">",
        "search_term": "1950"
      }
    ]
  },
  "sort_queries": [
    {
      "type": "sort",
      "index_set": "alma",
      "index_name": "creator",
      "sort_order": "ascending"
    }
  ]
}
```

Note that 'type' is the same for each instace of a 'type' of resource. For example, boolean operators will always have 'type' = 'booleanOperator'. Boolean Operators must also have an operator string, which should be 'AND', 'OR', 'NOT', or 'PROX'.

First, if this JSON is not automatically converted into a python dictionary, use json.loads() to get it into a python dictionary.

Next, simply pass this dictionary into either of the SearchRetrieve functions in your queryer!

queryer.search_retrieve(from_dict=parsed_json_dict)<br>
or <br>
request = queryer.construct_search_retrieve_request(from_dict=parsed_json_dict)

For version 1.1, the sort_queries will look different due to them being SortKeys instead. SortKey JSON format looks like:

```json
{
  "type": "sortKey",
  "xpath": "cql.author",
  "schema": "marcxml",
  "ascending": false,
  "case_sensitive": true,
  "missing_value": null
}
```

Any of these values can be null except 'type' and 'xpath'
<br>
<br>

---

## Known Incompatibilities

Different SRU servers have quirks to their default behaviors, and don't all fully implement the Library of Congress standard on SRU.

Additionally, I haven't been able to test some of the more advanced features of this library, namely the PROX modifier, relation modifiers, and boolean operator modifiers successfully on an SRU server. I've tried to test with 3 SRU servers, and I've never gotten the queries to work properly, even when trying them by hand in the browser URL bar. Even when I use the exact sample from the Library of Congress SRU documentation on the Library of Congress SRU server, it returns errors. However, all the queries that this library creates meet up to the documentation, so I'm hopeful that these features will work if there's a SRU server that supports them. Thankfully, I've been able to test most of the core functionality of the library.

If you know of a valid RelationModifier, BooleanOperatorModifier, or PROX request and have the capability to test it, it would be much appreciated! Part of my issue simply comes from the fact that I don't really know all the use cases for these features, which limits my testing to only one or two. We also need the SRU version 1.1 SortKey functionality to be tested, but again don't have the capability.

Below are a few of the issues I've found.

<br>

### ExLibris Alma SRU server

❌ PROX boolean operator <br>
❌ NOT boolean operator <br>
❌ Multiple sort queries (only one supported)

❓ Boolean Operator Modifiers <br>
❓ RelationModifiers

### Library of Congress SRU server

❌ PROX boolean operator <br>
❌ Sorting (in either version 1.1 or 1.2) <br>
❌ Default context set

⚠️ You must include maximum_records in a searchRetrieve query to get any records in return <br>
⚠️ This server lists BIBFRAME as an available record schema, but fails when requesting it

❓ RelationModifiers <br>
❓ Boolean Operator Modifiers

### Georgia Public Library 'Public Information Network for Electronic Services' (GAPINES)

⚠️ PROX boolean operator doesn't return an error, but doesn't seem to affect results <br>
⚠️ Sorting doesn't return an error, but doesn't seem to affect results

❓ RelationModifiers <br>
❓ Boolean Operator Modifiers
