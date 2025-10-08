import json
import logging
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

    global environment_id
    global kafka_cluster_id
    global principal_id

    # Set the Environment ID, Kafka cluster ID and owner ID.
    environment_id = os.getenv("ENVIRONMENT_ID")
    kafka_cluster_id = os.getenv("KAFKA_CLUSTER_ID")
    principal_id = os.getenv("PRINCIPAL_ID")

def test_get_environment_list():
    """Test the get_environment_list() function."""

    # Instantiate the EnvironmentClient class.
    environment_client = EnvironmentClient(environment_config=environment_config)

    http_status_code, error_message, environments = environment_client.get_environment_list()
 
    try:
        assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"

        logger.info("Environments: %d", len(environments))

        beautified = json.dumps(environments, indent=4, sort_keys=True)
        logger.info(beautified)
    except AssertionError as e:
        logger.error(e)
        logger.error("HTTP Status Code: %d, Error Message: %s, Environments: %s", http_status_code, error_message, environments)
        return
    
def test_get_kafka_cluster_list():
    """Test the get_kafka_cluster_list() function."""

    # Instantiate the EnvironmentClient class.
    environment_client = EnvironmentClient(environment_config=environment_config)

    http_status_code, error_message, kafka_clusters = environment_client.get_kafka_cluster_list(environment_id=environment_id)
 
    try:
        assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"

        logger.info("Kafka Clusters: %d", len(kafka_clusters))

        beautified = json.dumps(kafka_clusters, indent=4, sort_keys=True)
        logger.info(beautified)
    except AssertionError as e:
        logger.error(e)
        logger.error("HTTP Status Code: %d, Error Message: %s, Kafka Clusters: %s", http_status_code, error_message, kafka_clusters)
        return