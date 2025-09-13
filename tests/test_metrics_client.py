import logging
from dotenv import load_dotenv
import os
import pytest

from cc_clients_python_lib.http_status import HttpStatus
from cc_clients_python_lib.metrics_client import MetricsClient, METRICS_CONFIG


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
    """Load the Metrics configuration and Kafka test topic from the environment variables."""
    load_dotenv()
 
    global metrics_config
    global kafka_cluster_id
    global kafka_topic_name
    global start_time
    global end_time

    # Set the Kafka test topic.
    kafka_topic_name = os.getenv("KAFKA_TOPIC_NAME")
    kafka_cluster_id = os.getenv("KAFKA_CLUSTER_ID")
    start_time = os.getenv("START_TIME")
    end_time = os.getenv("END_TIME")

    # Set the Metrics configuration.
    metrics_config[METRICS_CONFIG["cloud_api_key"]] = os.getenv("CLOUD_API_KEY")
    metrics_config[METRICS_CONFIG["cloud_api_secret"]] = os.getenv("CLOUD_API_SECRET")


def test_get_topic_bytes():
    """Test the get_topic_bytes() function."""

    # Instantiate the MetricsClient class.
    metrics_client = MetricsClient(metrics_config)

    http_status_code, error_message, query_result = metrics_client.get_topic_bytes(kafka_cluster_id, kafka_topic_name, start_time, end_time)
 
    try:
        logger.info("HTTP Status Code: %d, Error Message: %s, Query Result: %s", http_status_code, error_message, query_result)
        assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"
    except AssertionError as e:
        logger.error(e)
        logger.error("HTTP Status Code: %d, Error Message: %s, Query Result: %s", http_status_code, error_message, query_result)