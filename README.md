# Confluent Cloud Clients Python Library

The Confluent Cloud Clients Python Library provides a set of clients for interacting with Confluent Cloud REST APIs. The library includes clients for:
+ **Flink**
+ **Kafka**
+ **Schema Registry**

> **Note:** _This library is in active development and is subject to change.  It covers only the methods I have needed so far.  If you need a method that is not covered, please feel free to open an issue or submit a pull request._

**Table of Contents**

<!-- toc -->
- [**1.0 Library Clients**](#10-library-clients)
    * [**1.1 Flink Client**](#11-flink-client)
    * [**1.2 Kafka Client**](#12-kafka-client)
    * [**1.3 Schema Registry Client**](#13-schema-registry-client)
- [**2.0 Installation**](#20-installation)
+ [**3.0 Resources**](#30-resources)
    * [**3.1 API Documentation**](#31-api-documentation)
    * [**3.2 Flink Resources**](#32-flink-resources)
<!-- tocstop -->

## **1.0 Library Clients**

### **1.1 Flink Client**
The **Flink Client** provides the following methods:
- `delete_statement`
- `delete_statements_by_phase`
- `get_compute_pool`
- `get_compute_pool_list`
- `get_statement_list`
- `stop_statement`
- `submit_statement`

### **1.2 Kafka Client**
The **Kafka Client** provides the following methods:
- `delete_kafka_topic`
- `kafka_topic_exist`

### **1.3 Schema Registry Client**
The **Schema Registry Client** provides the following methods:
- `convert_avro_schema_into_string`
- `delete_kafka_topic_key_schema_subject`
- `delete_kafka_topic_value_schema_subject`
- `get_global_topic_subject_compatibility_level`
- `get_topic_subject_compatibility_level`
- `get_topic_subject_latest_schema`
- `register_topic_subject_schema`
- `set_topic_subject_compatibility_level`

## **2.0 Installation**
Install the Confluent Cloud Clients Python Library using **`pip`**:
```bash
pip install cc-clients-python-lib
```

Or, using [**`uv`**](https://docs.astral.sh/uv/):
```bash
uv add cc-clients-python-lib
```

## **3.0 Resources**

### **3.1 API Documentation**
* [Flink SQL REST API for Confluent Cloud for Apache Flink](https://docs.confluent.io/cloud/current/flink/operate-and-deploy/flink-rest-api.html)
* [Kafka REST APIs for Confluent Cloud](https://docs.confluent.io/cloud/current/kafka-rest/kafka-rest-cc.html)
* [Confluent Cloud APIs - Topic (v3)](https://docs.confluent.io/cloud/current/api.html#tag/Topic-(v3))
* [Confluent Cloud Schema Registry REST API Usage](https://docs.confluent.io/cloud/current/sr/sr-rest-apis.html)

### **3.2 Flink Resources**
* [CCAF State management](https://docs.confluent.io/cloud/current/flink/concepts/overview.html#state-management)
* [Update a statement](https://docs.confluent.io/cloud/current/flink/reference/flink-sql-cli.html#update-a-statement)
