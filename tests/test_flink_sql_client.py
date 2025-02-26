import logging
from dotenv import load_dotenv
import os
import pytest
from src.cc_clients_lib.flink_sql_client import FlinkSqlClient, FLINK_CONFIG
from src.cc_clients_lib.common import HttpStatus


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
statement_name = ""


@pytest.fixture(autouse=True)
def load_configurations():
    """Load the Schema Registry Cluster configuration and Kafka test topic from the environment variables."""
    load_dotenv()
 
    global config
    global statement_name

    # Set the Flink configuration.
    config[FLINK_CONFIG["flink_api_key"]] = os.getenv("FLINK_API_KEY")
    config[FLINK_CONFIG["flink_api_secret"]] = os.getenv("FLINK_API_SECRET")
    config[FLINK_CONFIG["organization_id"]] = os.getenv("ORGANIZATION_ID")
    config[FLINK_CONFIG["environment_id"]] = os.getenv("ENVIRONMENT_ID")
    config[FLINK_CONFIG["cloud_provider"]] = os.getenv("CLOUD_PROVIDER")
    config[FLINK_CONFIG["cloud_region"]] = os.getenv("CLOUD_REGION")
    config[FLINK_CONFIG["compute_pool_id"]] = os.getenv("COMPUTE_POOL_ID")
    config[FLINK_CONFIG["principal_id"]] = os.getenv("PRINCIPAL_ID")
    
    # Set the Flink SQL statement name.
    statement_name = os.getenv("FLINK_STATEMENT_NAME")


def test_delete_statement():
    """Test the delete_statement() function."""

    # Instantiate the FlinkSqlClient classs.
    flink_client = FlinkSqlClient(config)

    http_status_code, response = flink_client.delete_statement(statement_name)
 
    try:
        assert http_status_code == HttpStatus.ACCEPTED, f"HTTP Status Code: {http_status_code}"
    except AssertionError as e:
        logger.error(e)
        logger.error("Response: %s", response)

def test_get_statement_list():
    """Test the get_statement_list() function."""

    # Instantiate the FlinkSqlClient classs.
    flink_client = FlinkSqlClient(config)

    http_status_code, _, response = flink_client.get_statement_list()
 
    try:
        assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"

        logger.info("Response: %s", response)
    except AssertionError as e:
        logger.error(e)
        logger.error("Response: %s", response)
