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
- [**2.0 Unit Tests**](#20-unit-tests)
    * [**2.1 Flink Client**](#21-flink-client)
- [**3.0 Installation**](#30-installation)
+ [**4.0 Resources**](#40-resources)
    * [**4.1 API Documentation**](#41-api-documentation)
    * [**4.2 Flink Resources**](#42-flink-resources)
    * [**4.3 Other Resources**](#43-other-resources)
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
    > _**Note:**  "Confluent Cloud for Apache Flink enforces a **30-day** retention for statements in terminal states."_
- `submit_statement`
- `update_statement`
- `update_all_sink_statements`

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

## **2.0 Unit Tests**
The library includes unit tests for each client. The tests are located in the `tests` directory.  To use them, you must clone the repo locally:

```bash
git clone https://github.com/j3-signalroom/cc-clients-python_lib.git
```

 Since this project was built using [**`uv`**](https://docs.astral.sh/uv/), please install it, and then run the following command to install all the project dependencies:

```bash
 uv sync
 ```

Then within the `tests` directory, create the `.env` file and add the following environment variables, filling them with your Confluent Cloud credentials and other required values:

```bash
SCHEMA_REGISTRY_URL=<SCHEMA_REGISTRY_URL>
SCHEMA_REGISTRY_API_KEY=<SCHEMA_REGISTRY_API_KEY>
SCHEMA_REGISTRY_API_SECRET=<SCHEMA_REGISTRY_API_SECRET>
KAFKA_TOPIC_NAME=<KAFKA_TOPIC_NAME>
FLINK_API_KEY=<FLINK_API_KEY>
FLINK_API_SECRET=<FLINK_API_SECRET>
ORGANIZATION_ID=<ORGANIZATION_ID>
ENVIRONMENT_ID=<ENVIRONMENT_ID>
CLOUD_PROVIDER=<CLOUD_PROVIDER>
CLOUD_REGION=<CLOUD_REGION>
COMPUTE_POOL_ID=<COMPUTE_POOL_ID>
PRINCIPAL_ID=<PRINCIPAL_ID>
FLINK_STATEMENT_NAME=<FLINK_STATEMENT_NAME>
FLINK_CATALOG_NAME=<FLINK_CATALOG_NAME>
FLINK_DATABASE_NAME=<FLINK_DATABASE_NAME>
BOOTSTRAP_SERVER_ID=<BOOTSTRAP_SERVER_ID>
BOOTSTRAP_SERVER_CLOUD_PROVIDER=<BOOTSTRAP_SERVER_CLOUD_PROVIDER>
BOOTSTRAP_SERVER_CLOUD_REGION=<BOOTSTRAP_SERVER_CLOUD_REGION>
KAFKA_CLUSTER_ID=<BOOTSTRAP_SERVER_ID>
KAFKA_API_KEY=<BOOTSTRAP_SERVER_ID>
KAFKA_API_SECRET=<BOOTSTRAP_SERVER_ID>
CONFLUENT_CLOUD_API_KEY=<CONFLUENT_CLOUD_API_KEY>
CONFLUENT_CLOUD_API_SECRET=<CONFLUENT_CLOUD_API_SECRET>
```

### **2.1 Flink Client**
To run a specific test, use one of the following commands:

Unit Test|Command
-|-
Get list of the all the Statements|`pytest -s tests/test_flink_client.py::test_get_statement_list`
Update all the Sink Statements|`pytest -s tests/test_flink_client.py::test_update_all_sink_statements`

Otherwise, to run all the tests, use the following command:
```bash
pytest -s tests/test_flink_client.py
```

> **Note:** _The tests are designed to be run in a specific order.  If you run them out of order, you may encounter errors.  The tests are also designed to be run against a Confluent Cloud environment.  If you run them against a local environment, you may encounter errors._

## **3.0 Installation**
Install the Confluent Cloud Clients Python Library using **`pip`**:
```bash
pip install cc-clients-python-lib
```

Or, using [**`uv`**](https://docs.astral.sh/uv/):
```bash
uv add cc-clients-python-lib
```

## **4.0 Resources**

### **4.1 API Documentation**
* [Flink SQL REST API for Confluent Cloud for Apache Flink](https://docs.confluent.io/cloud/current/flink/operate-and-deploy/flink-rest-api.html)
* [Kafka REST APIs for Confluent Cloud](https://docs.confluent.io/cloud/current/kafka-rest/kafka-rest-cc.html)
* [Confluent Cloud APIs - Topic (v3)](https://docs.confluent.io/cloud/current/api.html#tag/Topic-(v3))
* [Confluent Cloud Schema Registry REST API Usage](https://docs.confluent.io/cloud/current/sr/sr-rest-apis.html)

### **4.2 Flink Resources**
* [CCAF State management](https://docs.confluent.io/cloud/current/flink/concepts/overview.html#state-management)

### **4.3 Other Resources**
* [How to programmatically pause and resume a Flink statement](.blog/how-to-programmatically-pause-and-resume-a-flink-statement.md)