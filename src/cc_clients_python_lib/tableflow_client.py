from typing import Tuple
import requests
from requests.auth import HTTPBasicAuth


__copyright__  = "Copyright (c) 2025 Jeffrey Jonathan Jennings"
__license__    = "MIT"
__credits__    = ["Jeffrey Jonathan Jennings (J3)"]
__maintainer__ = "Jeffrey Jonathan Jennings (J3)"
__email__      = "j3@thej3.com"
__status__     = "dev"


# Tableflow Config Keys.
TABLEFLOW_CONFIG = {
    "tableflow_api_key": "tableflow_api_key",
    "tableflow_api_secret": "tableflow_api_secret"
}


class TableflowClient():
    def __init__(self, tableflow_config: dict):
        self.tableflow_api_key = str(tableflow_config[TABLEFLOW_CONFIG["tableflow_api_key"]])
        self.tableflow_api_secret = str(tableflow_config[TABLEFLOW_CONFIG["tableflow_api_secret"]])
        self.tableflow_base_url = "https://api.confluent.cloud/tableflow/v1"

    def get_tableflow_topic(self, topic_name: str, environment_id: str, kafka_cluster_id: str) -> Tuple[int, str, dict]:
        """Get the Tableflow enabled topic.

        Args:
            topic_name(str):       The name of the topic.
            environment_id(str):   The environment ID.
            kafka_cluster_id(str): The Kafka cluster ID.
            
        Returns:
            Tuple[int, str, dict]: A tuple containing the HTTP status code, error message, and response data.
        """
        # Validate the input parameters.
        if not topic_name or not environment_id or not kafka_cluster_id:
            return 400, "Invalid input parameters. Please provide a valid topic name, environment ID, and Kafka cluster ID.", {}
        
        # Submit the GET method to get the Tableflow enabled topic.
        response = requests.get(url=f"{self.tableflow_base_url}/tableflow-topics/{topic_name}?environment={environment_id}&spec.kafka_cluster={kafka_cluster_id}", auth=HTTPBasicAuth(self.tableflow_api_key, self.tableflow_api_secret))
 
        try:
            # Raise HTTPError, if occurred.
            response.raise_for_status()
 
            return response.status_code, response.text, response.json()
        except requests.exceptions.RequestException as e:
            return response.status_code, f"Error retrieving Tableflow enabled topic '{topic_name}': {e}",  response.json() if response.content else {}
        
    def get_tableflow_topic_table_path(self, topic_name: str, environment_id: str, kafka_cluster_id: str) -> Tuple[int, str, str]:
        http_status_code, error_message, response =  self.get_tableflow_topic(topic_name, environment_id, kafka_cluster_id)

        if http_status_code != 200:
            return http_status_code, error_message, response
        
        # Parse the response to get the table path.
        if response.get("spec") is None:
            return 400, "Invalid response. 'spec' key not found in the response.", ""
        if response.get("spec").get("storage") is None:
            return 400, "Invalid response. 'storage' key not found in the response.", ""
        if response.get("spec").get("storage").get("table_path") is None:
            return 400, "Invalid response. 'table_path' key not found in the response.", ""
        else:
            return http_status_code, error_message, response.get("spec").get("storage").get("table_path")
    