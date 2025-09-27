import json
import logging
import time
from dotenv import load_dotenv
import os
import pytest

from cc_clients_python_lib.environment_client import EnvironmentClient, ENVIRONMENT_CONFIG
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
environment_config = {}
kafka_cluster_id = ""
principal_id = ""


@pytest.fixture(autouse=True)
def load_configurations():
    """Load the Environment configuration from the environment variables."""
    load_dotenv()
 
    # Set the Flink configuration.
    global environment_config
    environment_config[ENVIRONMENT_CONFIG["confluent_cloud_api_key"]] = os.getenv("CONFLUENT_CLOUD_API_KEY")
    environment_config[ENVIRONMENT_CONFIG["confluent_cloud_api_secret"]] = os.getenv("CONFLUENT_CLOUD_API_SECRET")
    environment_config[ENVIRONMENT_CONFIG["environment_id"]] = os.getenv("ENVIRONMENT_ID")

    global kafka_cluster_id
    global principal_id

    # Set the Kafka cluster ID and owner ID.
    kafka_cluster_id = os.getenv("KAFKA_CLUSTER_ID")
    principal_id = os.getenv("PRINCIPAL_ID")

def test_create_kafka_api_key():
    """Test the create_kafka_api_key() function."""

    # Instantiate the EnvironmentClient class.
    environment_client = EnvironmentClient(environment_config=environment_config)

    http_status_code, error_message, api_key_pair = environment_client.create_kafka_api_key(kafka_cluster_id=kafka_cluster_id, principal_id=principal_id)
 
    try:
        assert http_status_code == HttpStatus.ACCEPTED, f"HTTP Status Code: {http_status_code}"

        beautified = json.dumps(api_key_pair, indent=4, sort_keys=True)
        logger.info(f"Kafka API Key Pair: {beautified}")
    except AssertionError as e:
        logger.error(e)
        logger.error("HTTP Status Code: %d, Error Message: %s, Kafka API Key Pair: %s", http_status_code, error_message, api_key_pair)
        return
    
def test_delete_kafka_api_key():
    """Test the delete_kafka_api_key() function."""

    # Instantiate the EnvironmentClient class.
    environment_client = EnvironmentClient(environment_config=environment_config)

    http_status_code, error_message, api_key_pair = environment_client.create_kafka_api_key(kafka_cluster_id=kafka_cluster_id, principal_id=principal_id)
 
    try:
        assert http_status_code == HttpStatus.ACCEPTED, f"HTTP Status Code: {http_status_code}"

        beautified = json.dumps(api_key_pair, indent=4, sort_keys=True)
        logger.info(f"Kafka API Key Pair: {beautified}")
    except AssertionError as e:
        logger.error(e)
        logger.error("HTTP Status Code: %d, Error Message: %s, Kafka API Key Pair: %s", http_status_code, error_message, api_key_pair)
        return

    time.sleep(10)  # Wait for 10 seconds before deleting the API key.

    http_status_code, error_message = environment_client.delete_kafka_api_key(api_key=api_key_pair["key"])
 
    try:
        assert http_status_code == HttpStatus.NO_CONTENT, f"HTTP Status Code: {http_status_code}"

        logger.info(f"Successfully deleted Kafka API Key: {api_key_pair['key']}")
    except AssertionError as e:
        logger.error(e)
        logger.error("HTTP Status Code: %d, Error Message: %s", http_status_code, error_message)
        return  
    
def test_get_environment_list():
    """Test the get_environment_list() function."""

    # Instantiate the EnvironmentClient class.
    environment_client = EnvironmentClient(environment_config=environment_config)

    http_status_code, error_message, environments = environment_client.get_environment_list()
 
    try:
        assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"

        logger.info(f"Environments: {len(environments)}")

        for environment in environments:
            beautified = json.dumps(environment, indent=4, sort_keys=True)
            logger.info(beautified)
    except AssertionError as e:
        logger.error(e)
        logger.error("HTTP Status Code: %d, Error Message: %s, Environments: %s", http_status_code, error_message, environments)
        return
    
def test_get_kafka_cluster_list():
    """Test the get_kafka_cluster_list() function."""

    # Instantiate the EnvironmentClient class.
    environment_client = EnvironmentClient(environment_config=environment_config)

    http_status_code, error_message, kafka_clusters = environment_client.get_kafka_cluster_list()
 
    try:
        assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"

        logger.info(f"Kafka Clusters: {len(kafka_clusters)}")

        for kafka_cluster in kafka_clusters:
            beautified = json.dumps(kafka_cluster, indent=4, sort_keys=True)
            logger.info(beautified)
    except AssertionError as e:
        logger.error(e)
        logger.error("HTTP Status Code: %d, Error Message: %s, Kafka Clusters: %s", http_status_code, error_message, kafka_clusters)
        return