import logging
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
 
    # Set Schema Registry Cluster configuration.
    config = {}
    config['url'] = "https://schema-registry-external-371823293044.us-east-1.elb.amazonaws.com"
    config['api_key'] = ""
    config['api_secret'] = ""
   
    # Instantiate the SchemaRegistryClient classs.
    sr_client = SchemaRegistryClient(config)
 
    _, _, response = sr_client.get_topic_subject_compatibility_level(kafka_topic_subject)
 
    logger.info("Response: %s", response)
 
    assert CompatibilityLevel.BACKWARD.value == response.BACKWARD.value
 