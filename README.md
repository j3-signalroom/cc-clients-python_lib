# Confluent Cloud Clients Python Library
This library provides a set of clients for interacting with Confluent Cloud REST APIs. The library includes clients for:

+ **Schema Registry Client** provides the following methods:
    - `convert_avro_schema_into_string`
    - `get_global_topic_subject_compatibility_level`
    - `get_topic_subject_compatibility_level`
    - `get_topic_subject_latest_schema`
    - `register_topic_subject_schema`
    - `set_topic_subject_compatibility_level`

+ **Flink Client** provides the following methods:
    - `delete_statement`
    - `get_statement_list`