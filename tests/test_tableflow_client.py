import logging
from dotenv import load_dotenv
import os
import pytest

from cc_clients_python_lib.tableflow_client import TableflowClient, TABLEFLOW_CONFIG
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
tableflow_config = {}
kafka_topic_name = ""
kafka_cluster_id = ""
environment_id = ""


@pytest.fixture(autouse=True)
def load_configurations():
    """Load the Kafka Cluster configuration and Kafka test topic from the environment variables."""
    load_dotenv()
 
    global tableflow_config
    global kafka_topic_name
    global kafka_cluster_id
    global environment_id

    kafka_topic_name = os.getenv("KAFKA_TOPIC_NAME")
    kafka_cluster_id = os.getenv("KAFKA_CLUSTER_ID")
    environment_id = os.getenv("ENVIRONMENT_ID")

    tableflow_config[TABLEFLOW_CONFIG["tableflow_api_key"]] = os.getenv("TABLEFLOW_API_KEY")
    tableflow_config[TABLEFLOW_CONFIG["tableflow_api_secret"]] = os.getenv("TABLEFLOW_API_SECRET")


def test_get_tableflow_topic():
    """Test the get_tableflow_topic() function."""

    # Instantiate the TableflowClient class.
    tableflow_client = TableflowClient(tableflow_config)

    http_status_code, error_message, response = tableflow_client.get_tableflow_topic(kafka_topic_name, environment_id, kafka_cluster_id)
 
    try:
        logger.info(f"Response: {response}")
        logger.info(f"HTTP Status Code: {http_status_code}")

        assert http_status_code == HttpStatus.OK, error_message
    except AssertionError as e:
        logger.error(e)


def test_get_tableflow_topic_table_path():
    """Test the get_tableflow_topic_table_path() function."""

    # Instantiate the TableflowClient class.
    tableflow_client = TableflowClient(tableflow_config)

    http_status_code, error_message, table_path = tableflow_client.get_tableflow_topic_table_path(kafka_topic_name, environment_id, kafka_cluster_id)

    try:
        logger.info(f"table_path: {table_path}")
        logger.info(f"HTTP Status Code: {http_status_code}")

        assert http_status_code == HttpStatus.OK, error_message
    except AssertionError as e:
        logger.error(e)