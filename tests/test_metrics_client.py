import logging
from dotenv import load_dotenv
import os
import pytest
from datetime import datetime

from cc_clients_python_lib.http_status import HttpStatus
from cc_clients_python_lib.metrics_client import MetricsClient, METRICS_CONFIG, KafkaMetric


__copyright__  = "Copyright (c) 2025 Jeffrey Jonathan Jennings"
__credits__    = ["Jeffrey Jonathan Jennings (J3)"]
__maintainer__ = "Jeffrey Jonathan Jennings (J3)"
__email__      = "j3@thej3.com"
__status__     = "dev"
 

# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Initialize the global variables.
metrics_config = {}
kafka_cluster_id = ""
kafka_topic_name = ""
query_start_time = ""
query_end_time = ""


@pytest.fixture(autouse=True)
def load_configurations():
    """Load the Metrics configuration and Kafka test topic from the environment variables."""
    load_dotenv()
 
    
    # Set the Metrics configuration.
    global metrics_config
    metrics_config[METRICS_CONFIG["confluent_cloud_api_key"]] = os.getenv("CONFLUENT_CLOUD_API_KEY")
    metrics_config[METRICS_CONFIG["confluent_cloud_api_secret"]] = os.getenv("CONFLUENT_CLOUD_API_SECRET")

    global kafka_cluster_id
    global kafka_topic_name
    global query_start_time
    global query_end_time

    # Set the Kafka test topic.
    kafka_topic_name = os.getenv("KAFKA_TOPIC_NAME")
    kafka_cluster_id = os.getenv("KAFKA_CLUSTER_ID")
    query_start_time =  datetime.fromisoformat(os.getenv("QUERY_START_TIME").replace('Z', '+00:00'))
    query_end_time = datetime.fromisoformat(os.getenv("QUERY_END_TIME").replace('Z', '+00:00'))


def test_get_topic_total_bytes():
    """Test the get_topic_total() function for getting the total bytes."""

    # Instantiate the MetricsClient class.
    metrics_client = MetricsClient(metrics_config)

    http_status_code, error_message, query_result = metrics_client.get_topic_total(KafkaMetric.RECEIVED_BYTES, kafka_cluster_id, kafka_topic_name, query_start_time, query_end_time)
 
    try:
        logger.info("HTTP Status Code: %d, Error Message: %s, Query Result: %s", http_status_code, error_message, query_result)
        assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"
    except AssertionError as e:
        logger.error(e)
        logger.error("HTTP Status Code: %d, Error Message: %s, Query Result: %s", http_status_code, error_message, query_result)
    

def test_get_topic_total_records():
    """Test the get_topic_total() function for getting the total records."""

    # Instantiate the MetricsClient class.
    metrics_client = MetricsClient(metrics_config)

    http_status_code, error_message, query_result = metrics_client.get_topic_total(KafkaMetric.RECEIVED_RECORDS, kafka_cluster_id, kafka_topic_name, query_start_time, query_end_time)
 
    try:
        logger.info("HTTP Status Code: %d, Error Message: %s, Query Result: %s", http_status_code, error_message, query_result)
        assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"
    except AssertionError as e:
        logger.error(e)
        logger.error("HTTP Status Code: %d, Error Message: %s, Query Result: %s", http_status_code, error_message, query_result)