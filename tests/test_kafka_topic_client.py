import json
import logging
from dotenv import load_dotenv
import os
import pytest

from cc_clients_python_lib.kafka_topic_client import KafkaTopicClient, KAFKA_CONFIG
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
    """Load the Kafka Cluster configuration and Kafka test topic from the environment variables."""
    load_dotenv()
 
    global config
    global kafka_topic_name

    # Set the Kafka test topic.
    kafka_topic_name = os.getenv("KAFKA_TOPIC_NAME")

    # Set the Kafka Cluster configuration.
    config[KAFKA_CONFIG["kafka_cluster_id"]] = os.getenv("KAFKA_CLUSTER_ID")
    config[KAFKA_CONFIG["bootstrap_server_id"]] = os.getenv("BOOTSTRAP_SERVER_ID")
    config[KAFKA_CONFIG["bootstrap_server_cloud_region"]] = os.getenv("BOOTSTRAP_SERVER_CLOUD_REGION")
    config[KAFKA_CONFIG["bootstrap_server_cloud_provider"]] = os.getenv("BOOTSTRAP_SERVER_CLOUD_PROVIDER")
    config[KAFKA_CONFIG["kafka_api_key"]] = os.getenv("KAFKA_API_KEY")
    config[KAFKA_CONFIG["kafka_api_secret"]] = os.getenv("KAFKA_API_SECRET")


def test_delete_kafka_topic():
    """Test the delete_kafka_topic() function."""

    # Instantiate the KafkaClient class.
    kafka_topic_client = KafkaTopicClient(config)

    http_status_code, error_message = kafka_topic_client.delete_kafka_topic(kafka_topic_name)

    try:
        assert http_status_code == HttpStatus.NO_CONTENT, f"HTTP Status Code: {http_status_code}"
    except AssertionError as e:
        logger.info("HTTP Status Code: %d, and the Error Message: %s", http_status_code, error_message)
        logger.error(e)


def test_kafka_topic_exist():
    """Test the kafka_topic_exist() function."""

    # Instantiate the KafkaClient class.
    kafka_topic_client = KafkaTopicClient(config)

    http_status_code, error_message, exist = kafka_topic_client.kafka_topic_exist(kafka_topic_name)

    try:
        assert exist, f"HTTP Status Code: {http_status_code}"
    except AssertionError as e:
        logger.info("HTTP Status Code: %d, and the Error Message: %s", http_status_code, error_message)
        logger.error(e)


def test_kafka_get_topic():
    """Test the kafka_get_topic() function."""

    # Instantiate the KafkaClient class.
    kafka_topic_client = KafkaTopicClient(config)

    http_status_code, error_message, topic_details = kafka_topic_client.kafka_get_topic(kafka_topic_name)

    try:
        assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"
        beautified = json.dumps(topic_details, indent=4, sort_keys=True)
        logger.info("HTTP Status Code: %d, Error Message: %s, Topic Details: %s", http_status_code, error_message, beautified)
    except AssertionError as e:
        logger.info("HTTP Status Code: %d, and the Error Message: %s", http_status_code, error_message)
        logger.error(e)