# Confluent Cloud Clients Python Library

> **Note:** _This library is in active development and is subject to change.  It covers only the methods I have needed so far.  If you need a method that is not covered, please feel free to open an issue or submit a pull request._

This library provides a set of clients for interacting with Confluent Cloud REST APIs. The library includes clients for:

+ **Flink Client** provides the following methods:
    - `delete_statement`
    - `get_statement_list`
    
+ **Schema Registry Client** provides the following methods:
    - `convert_avro_schema_into_string`
    - `get_global_topic_subject_compatibility_level`
    - `get_topic_subject_compatibility_level`
    - `get_topic_subject_latest_schema`
    - `register_topic_subject_schema`
    - `set_topic_subject_compatibility_level`
