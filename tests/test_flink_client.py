import logging
from dotenv import load_dotenv
import os
import pytest
from cc_clients_python_lib.flink_client import FlinkClient, FLINK_CONFIG, StatementPhase
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
    config[FLINK_CONFIG["confluent_cloud_api_key"]] = os.getenv("CONFLUENT_CLOUD_API_KEY")
    config[FLINK_CONFIG["confluent_cloud_api_secret"]] = os.getenv("CONFLUENT_CLOUD_API_SECRET")
    
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

    # Instantiate the FlinkClient classs.
    flink_client = FlinkClient(config)

    http_status_code, response = flink_client.delete_statement(statement_name)
 
    try:
        assert http_status_code == HttpStatus.ACCEPTED, f"HTTP Status Code: {http_status_code}"
    except AssertionError as e:
        logger.error(e)
        logger.error("Response: %s", response)


def test_delete_statements_by_phase():
    """Test the delete_statements_by_phase() function."""

    # Instantiate the FlinkClient classs.
    flink_client = FlinkClient(config)

    http_status_code, error_message = flink_client.delete_statements_by_phase(StatementPhase.COMPLETED)

    try:
        assert http_status_code == HttpStatus.ACCEPTED, f"HTTP Status Code: {http_status_code}"
    except AssertionError as e:
        logger.error(e)
        logger.error("Error Message: %s", error_message)


def test_get_statement_list():
    """Test the get_statement_list() function."""

    # Instantiate the FlinkClient classs.
    flink_client = FlinkClient(config)

    http_status_code, _, response = flink_client.get_statement_list()
 
    try:
        assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"

        for item in response:
            logger.info("%s, %s, %s, %s, %s", item.get("spec").get("properties").get("sql.current-catalog"), item.get("spec").get("properties").get("sql.current-database"), item.get("spec").get("statement"), item.get("status").get("phase"), item.get("name"))
    except AssertionError as e:
        logger.error(e)
        logger.error("Response: %s", response)


def test_submit_statement():
    """Test the submit_statement() function."""

    # Instantiate the FlinkClient classs.
    flink_client = FlinkClient(config)

    http_status_code, error_message, response = flink_client.submit_statement("drop-statement",
                                                                              "DROP TABLE IF EXISTS hello;", 
                                                                              {"sql.current-catalog": catalog_name, "sql.current-database": database_name})
 
    try:
        logger.info("HTTP Status Code: %d, Error Message: %s, Response: %s", http_status_code, error_message, response)
        assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"        
    except AssertionError as e:
        logger.error(e)
        logger.error("HTTP Status Code: %d, Error Message: %s, Response: %s", http_status_code, error_message, response)


def test_get_compute_pool_list():
    """Test the get_compute_pool() function."""

    # Instantiate the FlinkClient classs.
    flink_client = FlinkClient(config)

    http_status_code, error_message, response = flink_client.get_compute_pool_list()
        
    try:
        assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"

        for item in response:
            logger.info("%s, %d, %d, %s", item.get("id"), item.get("status").get("current_cfu"), item.get("spec").get("max_cfu"), item.get("status").get("phase"))
    except AssertionError as e:
        logger.error(e)
        logger.error("Error Message: %s, Response: %s", error_message, response)


def test_get_compute_pool():
    """Test the get_compute_pool() function."""

    # Instantiate the FlinkClient classs.
    flink_client = FlinkClient(config)

    http_status_code, error_message, response = flink_client.get_compute_pool()

    try:        
        assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"
        logger.info("%s, %d, %d, %s", response.get("id"), response.get("status").get("current_cfu"), response.get("spec").get("max_cfu"), response.get("status").get("phase"))    
    except AssertionError as e:
        logger.error(e)
        logger.error("Error Message: %s, Response: %s", error_message, response)


def test_stop_statement():
    """Test the pause_statement() function."""

    # Instantiate the FlinkClient classs.
    flink_client = FlinkClient(config)

    http_status_code, response = flink_client.stop_statement(statement_name, True)
 
    try:
        assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"
    except AssertionError as e:
        logger.error(e)
        logger.error("Response: %s", response)
