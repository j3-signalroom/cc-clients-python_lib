from typing import Tuple, Dict
import requests
import uuid
import json
from requests.auth import HTTPBasicAuth


__copyright__  = "Copyright (c) 2025 Jeffrey Jonathan Jennings"
__license__    = "MIT"
__credits__    = ["Jeffrey Jonathan Jennings (J3)"]
__maintainer__ = "Jeffrey Jonathan Jennings (J3)"
__email__      = "j3@thej3.com"
__status__     = "dev"


# Flink SQL Config Keys.
FLINK_CONFIG = {
    "flink_api_key": "flink_api_key",
    "flink_api_secret": "flink_api_secret",
    "organization_id": "organization_id",
    "environment_id": "environment_id",
    "cloud_provider": "cloud_provider",
    "cloud_region": "cloud_region",
    "compute_pool_id": "compute_pool_id",
    "principal_id": "principal_id"
}


class FlinkSqlClient():
    def __init__(self, flink_sql_config: dict):
        self.organization_id = flink_sql_config[FLINK_CONFIG["organization_id"]]
        self.environment_id = flink_sql_config[FLINK_CONFIG["environment_id"]]
        self.flink_api_key = str(flink_sql_config[FLINK_CONFIG["flink_api_key"]])
        self.flink_api_secret = str(flink_sql_config[FLINK_CONFIG["flink_api_secret"]])
        self.cloud_provider = flink_sql_config[FLINK_CONFIG["cloud_provider"]]
        self.cloud_region = flink_sql_config[FLINK_CONFIG["cloud_region"]]
        self.compute_pool_id = flink_sql_config[FLINK_CONFIG["compute_pool_id"]]
        self.principal_id = flink_sql_config[FLINK_CONFIG["principal_id"]]
        self.flink_sql_base_url = f"https://flink.{self.cloud_region}.{self.cloud_provider}.confluent.cloud/sql/v1/organizations/{self.organization_id}/environments/{self.environment_id}/"
        self.flink_compute_pool_base_url = f"https://api.confluent.cloud/fcpm/v2/compute-pools/"

    def get_statement_list(self, page_size: int = None) -> Tuple[int, str, Dict]:
        """This function submits a RESTful API call to get the Flink SQL statement list.

        Returns:
            int:    HTTP Status Code.
            str:    HTTP Error, if applicable.
        """
        if page_size is None:
            query_parameters = ""
        else:
            query_parameters = f"?page_size={page_size}"

        # Send a GET request to get statement list.
        response = requests.get(url=f"{self.flink_sql_base_url}statements{query_parameters}", 
                                auth=HTTPBasicAuth(self.flink_api_key, self.flink_api_secret))

        try:
            # Raise HTTPError, if occurred.
            response.raise_for_status()

            return response.status_code, "", response.json()
        except requests.exceptions.RequestException as e:
            return response.status_code, f"Fail to retrieve the statement list because {e}", {}
        
    def delete_statement(self, statement_name: str) -> Tuple[int, str]:
        """This function submits a RESTful API call to delete a Flink SQL statement.

        Arg(s):
            statement_name (str):  The Flink SQL statement name.

        Returns:
            int:    HTTP Status Code.
            str:    HTTP Error, if applicable.
        """
        # Send a DELETE request to delete the statement.
        response = requests.delete(url=f"{self.flink_sql_base_url}statements/{statement_name}", 
                                   auth=HTTPBasicAuth(self.flink_api_key, self.flink_api_secret))

        try:
            # Raise HTTPError, if occurred.
            response.raise_for_status()

            return response.status_code, response.text
        except requests.exceptions.RequestException as e:
            return response.status_code, f"Fail to delete the statement because {e}"
        
    def submit_statement(self, statement_name: str, sql_query: str, sql_query_properties: Dict) -> Tuple[int, str, Dict]:
        """This function submits a RESTful API call to submit a Flink SQL statement.

        Arg(s):
            statement_name (str):        The Flink SQL statement name.
            sql_query (str):             The Flink SQL statement.
            sql_query_properties (dict): The Flink SQL statement properties.

        Returns:
            int:    HTTP Status Code.
            str:    HTTP Error, if applicable.
            dict:   The response JSON.
        """
        # Create a JSON payload to submit a statement.
        statement_name += (f"-{str(uuid.uuid4())}").replace("_", "-")
        payload = {
            "name": statement_name,
            "organization_id": self.organization_id,
            "environment_id": self.environment_id,
            "spec": {
                "statement": sql_query,
                "properties": sql_query_properties,
                "compute_pool_id": self.compute_pool_id,
                "principal": self.principal_id,
                "stopped": False
            }
        }

        # Send a POST request to submit a statement.
        response = requests.post(url=f"{self.flink_sql_base_url}statements",
                                    data=json.dumps(payload),
                                    auth=HTTPBasicAuth(self.flink_api_key, self.flink_api_secret))

        try:
            # Raise HTTPError, if occurred.
            response.raise_for_status()

            return response.status_code, response.text, response.json()
        except requests.exceptions.RequestException as e:
            return response.status_code, f"Fail to submit astatement because {e}", response.json()
        
    def get_compute_pool(self) -> Tuple[int, str, Dict]:
        """This function submits a RESTful API call to get the Flink Compute Pool.

        Returns:
            int:    HTTP Status Code.
            str:    HTTP Error, if applicable.
        """
        # Send a GET request to get compute list.
        response = requests.get(url=f"{self.flink_compute_pool_base_url}?spec.region={self.cloud_region}&environment={self.environment_id}&spec.network={self.compute_pool_id}", 
                                auth=HTTPBasicAuth(self.flink_api_key, self.flink_api_secret))

        try:
            # Raise HTTPError, if occurred.
            response.raise_for_status()

            return response.status_code, "", response.json()
        except requests.exceptions.RequestException as e:
            return response.status_code, f"Fail to retrieve the computer pool because {e}", {}