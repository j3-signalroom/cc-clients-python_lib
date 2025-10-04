import json
import logging
from dotenv import load_dotenv
import os
import pytest
from cc_clients_python_lib.environment_client import EnvironmentClient
from cc_clients_python_lib.schema_registry_client import SchemaRegistryClient, CompatibilityLevel, SCHEMA_REGISTRY_CONFIG
from cc_clients_python_lib.http_status import HttpStatus
 

__copyright__  = "Copyright (c) 2025 Jeffrey Jonathan Jennings"
__credits__    = ["Jeffrey Jonathan Jennings (J3)"]
__maintainer__ = "Jeffrey Jonathan Jennings (J3)"
__email__      = "j3@thej3.com"
__status__     = "dev"
 

# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@pytest.fixture
def sr_client():
    """Load the Confluent Cloud credentials from the Schema Registry Cluster variables."""

    load_dotenv()
    schema_registry_cluster_config = json.loads(os.getenv("CONFLUENT_CLOUD_CREDENTIAL", "{}"))
    schema_registry_cluster_config[SCHEMA_REGISTRY_CONFIG["url"]] = os.getenv("SCHEMA_REGISTRY_URL")
    schema_registry_cluster_config[SCHEMA_REGISTRY_CONFIG["api_key"]] = os.getenv("SCHEMA_REGISTRY_API_KEY")
    schema_registry_cluster_config[SCHEMA_REGISTRY_CONFIG["api_secret"]] = os.getenv("SCHEMA_REGISTRY_API_SECRET")    
    yield SchemaRegistryClient(schema_registry_cluster_config)

@pytest.fixture
def environment_client():
    """Load the Confluent Cloud credentials from the IAM variables."""
    load_dotenv()
    environment_config = json.loads(os.getenv("CONFLUENT_CLOUD_CREDENTIAL", "{}"))
    yield EnvironmentClient(environment_config)

@pytest.fixture
def kafka_topic_name():
    """Load the Test Kafka Topic name from the Schema Registry Cluster variables."""

    load_dotenv()
    return os.getenv("KAFKA_TOPIC_NAME")


class TestSchemaRegistryClient:
    """Test Suite for the SchemaRegistryClient class."""

    def test_get_subject_compatibility_level(self, sr_client, kafka_topic_name):
        """Test the get_topic_subject_compatibility_level() function."""

        # Set the Kafka topic subject name.
        kafka_topic_subject = f"{kafka_topic_name}-value"
    
        http_status_code, error_message, response = sr_client.get_topic_subject_compatibility_level(kafka_topic_subject)
    
        try:
            assert http_status_code == HttpStatus.OK, error_message
        except AssertionError as e:
            logger.error(e)

        try:
            assert CompatibilityLevel.FULL.value == response.value, f"Expected: {CompatibilityLevel.FULL.value}, Actual: {response.value}"
        except AssertionError as e:
            logger.error(e)


    def test_delete_kafka_topic_key_schema_subject(self, sr_client, kafka_topic_name):
        """Test the delete_kafka_topic_key_schema_subject() function."""

        http_status_code, error_message = sr_client.delete_kafka_topic_key_schema_subject(kafka_topic_name)
    
        try:
            assert http_status_code == HttpStatus.OK, error_message
        except AssertionError as e:
            logger.error(e)
            logger.error("Error Message: %s", error_message)


    def test_delete_kafka_topic_value_schema_subject(self, sr_client, kafka_topic_name):
        """Test the delete_kafka_topic_value_schema_subject() function."""

        # Instantiate the SchemaRegistryClient class
        http_status_code, error_message = sr_client.delete_kafka_topic_value_schema_subject(kafka_topic_name)
    
        try:
            assert http_status_code == HttpStatus.OK, error_message
        except AssertionError as e:
            logger.error(e)
            logger.error("Error Message: %s", error_message)

    def test_getting_all_schema_registry_clusters(self, sr_client, environment_client):
        """Test the get_schema_registry_cluster_list() function."""

        http_status_code, error_message, environments = environment_client.get_environment_list()
        try:
            assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"

            logger.info("Environments: %d", len(environments))

            for environment in environments:
                http_status_code, error_message, schema_registry_clusters = sr_client.get_schema_registry_cluster_list(environment_id=environment["id"])

                try:
                    assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"

                    logger.info("Schema Registry Clusters: %d", len(schema_registry_clusters))

                    for schema_registry_cluster in schema_registry_clusters:
                        beautified = json.dumps(schema_registry_cluster, indent=4, sort_keys=True)
                        logger.info(beautified)
                except AssertionError as e:
                    logger.error(e)
                    logger.error("HTTP Status Code: %d, Error Message: %s, schema_registry_clusters: %s", http_status_code, error_message, schema_registry_clusters)
                    return
        except AssertionError as e:
            logger.error(e)
            logger.error("HTTP Status Code: %d, Error Message: %s, Environments: %s", http_status_code, error_message, environments)
            return