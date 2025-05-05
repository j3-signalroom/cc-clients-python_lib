import logging
from dotenv import load_dotenv
import os
import pytest
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

# Initialize the global variables.
config = {}
kafka_topic_name = ""


@pytest.fixture(autouse=True)
def load_configurations():
    """Load the Schema Registry Cluster configuration and Kafka test topic from the environment variables."""
    load_dotenv()
 
    global config
    global kafka_topic_name

    # Set the Kafka test topic.
    kafka_topic_name = os.getenv("KAFKA_TOPIC_NAME")

    # Set the Schema Registry Cluster configuration.
    config[SCHEMA_REGISTRY_CONFIG["url"]] = os.getenv("SCHEMA_REGISTRY_URL")
    config[SCHEMA_REGISTRY_CONFIG["api_key"]] = os.getenv("SCHEMA_REGISTRY_API_KEY")
    config[SCHEMA_REGISTRY_CONFIG["api_secret"]] = os.getenv("SCHEMA_REGISTRY_API_SECRET")


def test_get_subject_compatibility_level():
    """Test the get_topic_subject_compatibility_level() function."""

    # Set the Kafka topic subject name.
    kafka_topic_subject = f"{kafka_topic_name}-value"
 
    # Instantiate the SchemaRegistryClient class.
    sr_client = SchemaRegistryClient(config)

    http_status_code, error_message, response = sr_client.get_topic_subject_compatibility_level(kafka_topic_subject)
 
    try:
        assert http_status_code == HttpStatus.OK, error_message
    except AssertionError as e:
        logger.error(e)

    try:
        assert CompatibilityLevel.FULL.value == response.value, f"Expected: {CompatibilityLevel.FULL.value}, Actual: {response.value}"
    except AssertionError as e:
        logger.error(e)


def test_delete_kafka_topic_key_schema_subject():
    """Test the delete_kafka_topic_key_schema_subject() function."""

    # Instantiate the SchemaRegistryClient class.
    sr_client = SchemaRegistryClient(config)

    http_status_code, error_message = sr_client.delete_kafka_topic_key_schema_subject(kafka_topic_name)
 
    try:
        assert http_status_code == HttpStatus.OK, error_message
    except AssertionError as e:
        logger.error(e)
        logger.error("Error Message: %s", error_message)


def test_delete_kafka_topic_value_schema_subject():
    """Test the delete_kafka_topic_value_schema_subject() function."""

    # Instantiate the SchemaRegistryClient class.
    sr_client = SchemaRegistryClient(config)

    http_status_code, error_message = sr_client.delete_kafka_topic_value_schema_subject(kafka_topic_name)
 
    try:
        assert http_status_code == HttpStatus.OK, error_message
    except AssertionError as e:
        logger.error(e)
        logger.error("Error Message: %s", error_message)
