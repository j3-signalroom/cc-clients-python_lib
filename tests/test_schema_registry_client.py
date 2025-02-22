import logging
from dotenv import load_dotenv
import os
from src.cc_clients_lib.schema_registry_client import SchemaRegistryClient, CompatibilityLevel
 

__copyright__  = "Copyright (c) 2025 Jeffrey Jonathan Jennings"
__credits__    = ["Jeffrey Jonathan Jennings (J3)"]
__maintainer__ = "Jeffrey Jonathan Jennings (J3)"
__email__      = "j3@thej3.com"
__status__     = "dev"
 

# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
 

def test_get_subject_compatibility_level():
    # Set the Kafka topic and subject.
    kafka_topic = "dev.mastery.load.raw.avro"
    kafka_topic_subject = f"{kafka_topic}-value"
 
    # Instantiate the SchemaRegistryClient classs.
    sr_client = SchemaRegistryClient(schema_registry_credentials())
 
    _, _, response = sr_client.get_topic_subject_compatibility_level(kafka_topic_subject)
 
    logger.info("Response: %s", response)
 
    assert CompatibilityLevel.UNASSIGNED.value == response.value


def schema_registry_credentials() -> dict:
    """
    Load the Schema Registry Cluster configuration from the environment variables.

    Returns:
        dict:  The Schema Registry Cluster configuration.
    """
    load_dotenv()
 
    # Set the Schema Registry Cluster configuration.
    config = {}
    config['url'] = os.getenv("SCHEMA_REGISTRY_URL")
    config['api_key'] = os.getenv("SCHEMA_REGISTRY_API_KEY")
    config['api_secret'] = os.getenv("SCHEMA_REGISTRY_API_SECRET")
 
    return config
