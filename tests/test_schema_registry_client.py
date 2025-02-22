import logging
from dotenv import load_dotenv
import os
import pytest
from src.cc_clients_lib.schema_registry_client import SchemaRegistryClient, CompatibilityLevel
 

__copyright__  = "Copyright (c) 2025 Jeffrey Jonathan Jennings"
__credits__    = ["Jeffrey Jonathan Jennings (J3)"]
__maintainer__ = "Jeffrey Jonathan Jennings (J3)"
__email__      = "j3@thej3.com"
__status__     = "dev"
 

# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
 
config = {}
kafka_topic = ""


@pytest.fixture(autouse=True)
def load_configurations():
    """Load the Schema Registry Cluster configuration and Kafka test topic from the environment variables."""
    load_dotenv()
 
    global config
    global kafka_topic

    # Set the Kafka test topic.
    kafka_topic = os.getenv("KAFKA_TOPIC")

    # Set the Schema Registry Cluster configuration.
    config['url'] = os.getenv("SCHEMA_REGISTRY_URL")
    config['api_key'] = os.getenv("SCHEMA_REGISTRY_API_KEY")
    config['api_secret'] = os.getenv("SCHEMA_REGISTRY_API_SECRET")


def test_get_subject_compatibility_level():
    """Test the get_topic_subject_compatibility_level() function."""

    # Set the Kafka topic subject name.
    kafka_topic_subject = f"{kafka_topic}-value"
 
    # Instantiate the SchemaRegistryClient classs.
    sr_client = SchemaRegistryClient(config)

    _, error_message, response = sr_client.get_topic_subject_compatibility_level(kafka_topic_subject)
 
    logger.info("Error message (if any): %s.  Response for %s: %s", error_message, kafka_topic_subject, response)
 
    assert CompatibilityLevel.FULL.value == response.value