import logging
from dotenv import load_dotenv
import os
import pytest
from src.cc_clients_python_lib.flink_sql_client import FlinkSqlClient, FLINK_CONFIG
from src.cc_clients_python_lib.common import HttpStatus


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
catalog_name = ""
database_name = ""


@pytest.fixture(autouse=True)
def load_configurations():
    """Load the Schema Registry Cluster configuration and Kafka test topic from the environment variables."""
    load_dotenv()
 
    # Set the Flink configuration.
    global config
    config[FLINK_CONFIG["flink_api_key"]] = os.getenv("FLINK_API_KEY")
    config[FLINK_CONFIG["flink_api_secret"]] = os.getenv("FLINK_API_SECRET")
    config[FLINK_CONFIG["organization_id"]] = os.getenv("ORGANIZATION_ID")
    config[FLINK_CONFIG["environment_id"]] = os.getenv("ENVIRONMENT_ID")
    config[FLINK_CONFIG["cloud_provider"]] = os.getenv("CLOUD_PROVIDER")
    config[FLINK_CONFIG["cloud_region"]] = os.getenv("CLOUD_REGION")
    config[FLINK_CONFIG["compute_pool_id"]] = os.getenv("COMPUTE_POOL_ID")
    config[FLINK_CONFIG["principal_id"]] = os.getenv("PRINCIPAL_ID")
    
    # Set the Flink SQL statement name.
    global statement_name
    statement_name = os.getenv("FLINK_STATEMENT_NAME")

    # Set the Flink SQL catalog and database names.
    global catalog_name
    global database_name
    catalog_name = os.getenv("FLINK_CATALOG_NAME")
    database_name = os.getenv("FLINK_DATABASE_NAME")


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

    logger.info("total_size: %s", response.get("metadata").get("total_size"))


    for item in response.get("data"):
        logger.info("%s, %s, %s, %s, %s", item.get("spec").get("properties").get("sql.current-catalog"), item.get("spec").get("properties").get("sql.current-database"), item.get("spec").get("statement"), item.get("status").get("phase"), item.get("name"))
 
    try:
        assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"
    except AssertionError as e:
        logger.error(e)
        logger.error("Response: %s", response)


def test_submit_statement():
    """Test the submit_statement() function."""

    # Instantiate the FlinkSqlClient classs.
    flink_client = FlinkSqlClient(config)

    http_status_code, error_message, response = flink_client.submit_statement("drop-statement",
                                                                              "DROP TABLE IF EXISTS hello;", 
                                                                              {"sql.current-catalog": catalog_name, "sql.current-database": database_name})
 
    try:
        logger.info("HTTP Status Code: %d, Error Message: %s, Response: %s", http_status_code, error_message, response)
        assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"        
    except AssertionError as e:
        logger.error(e)
        logger.error("HTTP Status Code: %d, Error Message: %s, Response: %s", http_status_code, error_message, response)
