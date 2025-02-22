import src.common as common
import logging
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
 

@pytest.fixture(autouse=True)
def aws_sso_credentials(monkeypatch):
    """
    Don't forget to run from the command-line:
    aws sso login --profile CHS-EnterpriseApiAdmin-371823293044
 
    To populate the local AWS credential environment variables.
    """
    monkeypatch.setenv("AWS_PROFILE", "CHS-EnterpriseApiAdmin-371823293044")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
 

def test_get_subject_compatibility_level():
    sr_secrets_path = "confluent/api_key/non_production/schema_registry"
    sink_kafka_topic = "dev.mastery.load.raw.avro"
    sink_kafka_topic_subject = f"{sink_kafka_topic}-value"
 
    # Get Schema Registry Cluster configuration.
    config, error_message = common.get_secrets(os.environ['AWS_REGION'], sr_secrets_path)
    if config == {}:
        logger.error("Failed to get secrets from the AWS Secrets Manager because of %s", error_message)
        return
   
    # Instantiate the SchemaRegistryClient classs.
    sr_client = SchemaRegistryClient(config)
 
    _, _, response = sr_client.get_topic_subject_compatibility_level(sink_kafka_topic_subject)
 
    logger.info("Response: %s", response)
 
    assert CompatibilityLevel.BACKWARD.value == response.BACKWARD.value
 