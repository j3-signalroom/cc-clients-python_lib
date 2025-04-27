from enum import StrEnum
import time
from typing import Tuple, Dict
import requests
import uuid
from requests.auth import HTTPBasicAuth

from cc_clients_python_lib.http_status import HttpStatus
from cc_clients_python_lib.cc_openapi_v2_1.sql.v1 import Statement, StatementSpec


__copyright__  = "Copyright (c) 2025 Jeffrey Jonathan Jennings"
__license__    = "MIT"
__credits__    = ["Jeffrey Jonathan Jennings (J3)"]
__maintainer__ = "Jeffrey Jonathan Jennings (J3)"
__email__      = "j3@thej3.com"
__status__     = "dev"


# Flink Config Keys.
FLINK_CONFIG = {
    "flink_api_key": "flink_api_key",
    "flink_api_secret": "flink_api_secret",
    "organization_id": "organization_id",
    "environment_id": "environment_id",
    "cloud_provider": "cloud_provider",
    "cloud_region": "cloud_region",
    "compute_pool_id": "compute_pool_id",
    "principal_id": "principal_id",
    "confluent_cloud_api_key": "confluent_cloud_api_key",
    "confluent_cloud_api_secret": "confluent_cloud_api_secret"
}

# Default values.
DEFAULT_PAGE_SIZE = 10

# Query Parameters.
QUERY_PARAMETER_PAGE_SIZE = "page_size"
QUERY_PARAMETER_PAGE_TOKEN = "page_token"

# The Statement Phase List.
class StatementPhase(StrEnum):
    COMPLETED = "COMPLETED"
    DEGRADED = "DEGRADED"
    DELETED = "DELETED"
    FAILED = "FAILED"
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    STOPPING = "STOPPING"


class FlinkClient():
    def __init__(self, flink_config: dict, private_network: bool = False):
        """This class initializes the Flink Client.

        Arg(s):            
            flink_config (dict):        The Flink configuration.
            private_network (bool):     (Optional) The private network flag.
        """
        self.organization_id = flink_config[FLINK_CONFIG["organization_id"]]
        self.environment_id = flink_config[FLINK_CONFIG["environment_id"]]
        self.flink_api_key = str(flink_config[FLINK_CONFIG["flink_api_key"]])
        self.flink_api_secret = str(flink_config[FLINK_CONFIG["flink_api_secret"]])
        self.cloud_provider = flink_config[FLINK_CONFIG["cloud_provider"]]
        self.cloud_region = flink_config[FLINK_CONFIG["cloud_region"]]
        self.compute_pool_id = flink_config[FLINK_CONFIG["compute_pool_id"]]
        self.principal_id = flink_config[FLINK_CONFIG["principal_id"]]
        self.confluent_cloud_api_key = str(flink_config[FLINK_CONFIG["confluent_cloud_api_key"]])
        self.confluent_cloud_api_secret = str(flink_config[FLINK_CONFIG["confluent_cloud_api_secret"]])
        self.flink_sql_base_url = f"https://flink.{self.cloud_region}.{self.cloud_provider}.{'private.' if private_network else ''}confluent.cloud/sql/v1/organizations/{self.organization_id}/environments/{self.environment_id}/"
        self.flink_compute_pool_base_url = "https://api.confluent.cloud/fcpm/v2/compute-pools"

    def statement_list(self, page_size: int = DEFAULT_PAGE_SIZE) -> Tuple[int, str, Dict]:
        """This function submits a RESTful API call to get the Flink SQL statement list.

        Arg(s):
            page_size (int):    (Optional) The page size.

        Returns:
            int:    HTTP Status Code.
            str:    HTTP Error, if applicable.
            dict:   The enitre list of available statements.
        """
        # Initialize the page token, statement list, and query parameters.
        page_token = "ITERATE_AT_LEAST_ONCE"
        statements = []
        query_parameters = f"?{QUERY_PARAMETER_PAGE_SIZE}={page_size}"
        page_token_parameter_length = len(f"&{QUERY_PARAMETER_PAGE_TOKEN}=")

        while page_token != "":
            # Set the query parameters.
            if page_token != "ITERATE_AT_LEAST_ONCE":
                query_parameters = f"?{QUERY_PARAMETER_PAGE_SIZE}={page_size}&{QUERY_PARAMETER_PAGE_TOKEN}={page_token}"
                
            # Send a GET request to get the next collection of statements.
            response = requests.get(url=f"{self.flink_sql_base_url}statements{query_parameters}", 
                                    auth=HTTPBasicAuth(self.flink_api_key, self.flink_api_secret))
            
            try:
                # Raise HTTPError, if occurred.
                response.raise_for_status()

                # Append the next collection of statements to the current statement list.
                statements.extend(response.json().get("data"))

                # Retrieve the page token from the next page URL.
                next_page_url = str(response.json().get("metadata").get("next"))
                page_token = next_page_url[next_page_url.find(f"&{QUERY_PARAMETER_PAGE_TOKEN}=") + page_token_parameter_length:]

            except requests.exceptions.RequestException as e:
                return response.status_code, f"Fail to retrieve the statement list because {e}", response.json() if response.content else {}
            
        return response.status_code, response.text, statements
        
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
    
    def delete_statements_by_phase(self, statement_phase: StatementPhase) -> Tuple[int, str]:
        """This function deletes all Flink SQL statements by phase.

        Arg(s):
            statement_phase (StatementPhase): The Flink SQL statement phase.

        Returns:
            int:    HTTP Status Code.
            str:    HTTP Error, if applicable.
        """
        # Get the statement list.
        http_status_code, error_message, response = self.statement_list()

        if http_status_code != HttpStatus.OK:
            return http_status_code, error_message

        # Delete the statements by phase.
        for statement in response:
            if StatementPhase(statement.get("status").get("phase")) == statement_phase:
                http_status_code, error_message = self.delete_statement(statement.get("name"))

                if http_status_code != HttpStatus.ACCEPTED:
                    return http_status_code, error_message

        return HttpStatus.ACCEPTED, ""
    
    def stop_statement(self, statement_name: str, stop: bool = True) -> Tuple[int, str]:
        """This function submits a RESTful API call to pause a Flink SQL statement.

        Arg(s):
            statement_name (str):  The Flink SQL statement name.
            stop (bool):           (Optional) The stop flag. Default is True.

        Returns:
            int:    HTTP Status Code.
            str:    HTTP Error, if applicable.
        """
        retry = 0
        max_retries = 9
        retry_delay_in_seconds = 5

        while retry < max_retries:
            # Send a GET request to get the statement.
            response = requests.get(url=f"{self.flink_sql_base_url}statements/{statement_name}",
                                    auth=HTTPBasicAuth(self.flink_api_key, self.flink_api_secret))

            try:
                # Raise HTTPError, if occurred.
                response.raise_for_status()

                # Turn the JSON response into a Statement model.
                statement = Statement(**response.json())

                # Get the statement resource version.
                resource_version = statement.metadata.resource_version

                # Set the stop flag.
                statement.spec.stopped = stop

                # Send a PUT request to update the status of the statement.
                response = requests.put(url=f"{self.flink_sql_base_url}statements/{statement_name}",
                                        data=statement.model_dump_json(),
                                        auth=HTTPBasicAuth(self.flink_api_key, self.flink_api_secret))
                
                try:
                    # Raise HTTPError, if occurred.
                    response.raise_for_status()

                    # Turn the JSON response into a Statement model.
                    statement = Statement(**response.json())

                    # Check if the resource version is the same.
                    if statement.metadata.resource_version == resource_version:
                        return response.status_code, response.text
                    else:
                        retry += 1
                        if retry == max_retries:
                            return response.status_code, f"Max retries exceeded.  Fail to update the statement because of a resource version mismatch.  Expected resource version #{resource_version}, but got resource version #{statement.metadata.resource_version}."
                        else:
                            time.sleep(retry_delay_in_seconds)
                except requests.exceptions.RequestException as e:
                    retry += 1
                    if retry == max_retries:
                        return response.status_code, f"Max retries exceeded.  Fail to update the statement because {e}, and the response is {response.text}"
                    else:
                        time.sleep(retry_delay_in_seconds)
            except requests.exceptions.RequestException as e:
                retry += 1
                if retry == max_retries:
                    return response.status_code, f"Max retries exceeded.  Fail to retrieve the statement because {e}, and the response is {response.text}"
                else:
                    time.sleep(retry_delay_in_seconds)

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
        # Create an instance of the Statement model.
        statement = Statement(name=(f"{statement_name}-{str(uuid.uuid4())}").replace("_", "-"),
                              organization_id=self.organization_id,
                              environment_id=self.environment_id,
                              spec=StatementSpec(statement=sql_query, 
                                                 properties=sql_query_properties, 
                                                 compute_pool_id=self.compute_pool_id,
                                                 principal=self.principal_id,
                                                 stopped=False))

        # Send a POST request to submit a statement.
        response = requests.post(url=f"{self.flink_sql_base_url}statements",
                                 data=statement.model_dump_json(),
                                 auth=HTTPBasicAuth(self.flink_api_key, self.flink_api_secret))

        try:
            # Raise HTTPError, if occurred.
            response.raise_for_status()

            return response.status_code, response.text, response.json()
        except requests.exceptions.RequestException as e:
            return response.status_code, f"Fail to submit a statement because {e}", response.json() if response.content else {}
        
    def compute_pool_list(self, page_size: int = DEFAULT_PAGE_SIZE) -> Tuple[int, str, Dict]:
        """This function submits a RESTful API call to get the Flink Compute Pool List.

        Arg(s):
            page_size (int):    (Optional) The page size.

        Returns:
            int:    HTTP Status Code.
            str:    HTTP Error, if applicable.
            dict:   The entire list of available compute pools.
        """
         # Initialize the page token, statement list, and query parameters.
        page_token = "ITERATE_AT_LEAST_ONCE"
        compute_pools = []
        query_parameters = f"?spec.region={self.cloud_region}&environment={self.environment_id}&{QUERY_PARAMETER_PAGE_SIZE}={page_size}"
        page_token_parameter_length = len(f"&{QUERY_PARAMETER_PAGE_TOKEN}=")

        while page_token != "":
            # Set the query parameters.
            if page_token != "ITERATE_AT_LEAST_ONCE":
                query_parameters = f"?spec.region={self.cloud_region}&environment={self.environment_id}&{QUERY_PARAMETER_PAGE_SIZE}={page_size}&{QUERY_PARAMETER_PAGE_TOKEN}={page_token}"


            # Send a GET request to get compute list.
            response = requests.get(url=f"{self.flink_compute_pool_base_url}{query_parameters}", 
                                    auth=HTTPBasicAuth(self.confluent_cloud_api_key, self.confluent_cloud_api_secret))

            try:
                # Raise HTTPError, if occurred.
                response.raise_for_status()

                # Append the next collection of statements to the current statement list.
                compute_pools.extend(response.json().get("data"))

                # Retrieve the page token from the next page URL.
                next_page_url = str(response.json().get("metadata").get("next"))
                page_token = next_page_url[next_page_url.find(f"&{QUERY_PARAMETER_PAGE_TOKEN}=") + page_token_parameter_length:]
            except requests.exceptions.RequestException as e:
                return response.status_code, f"Fail to retrieve the computer pool because {e}", response.json() if response.content else {}
            
        return response.status_code, response.text, compute_pools
        

    def compute_pool(self) -> Tuple[int, str, Dict]:
        """This function submits a RESTful API call to get the Flink Compute Pool.

        Returns:
            int:    HTTP Status Code.
            str:    HTTP Error, if applicable.
        """
        http_status_code, error_message, response = self.compute_pool_list()

        if http_status_code != HttpStatus.OK:
            return http_status_code, error_message, response
        else:
            for compute_pool in response:
                if compute_pool["id"] == self.compute_pool_id:
                    return HttpStatus.OK, "", compute_pool

            return HttpStatus.NOT_FOUND, f"Fail to find the compute pool with ID {self.compute_pool_id}", response
