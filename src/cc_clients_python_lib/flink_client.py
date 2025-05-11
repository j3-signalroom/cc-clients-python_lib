from enum import StrEnum
import json
import time
from typing import Tuple, Dict
import requests
import uuid
import re
from requests.auth import HTTPBasicAuth

from cc_clients_python_lib.cc_openapi_v2_1 import JsonPatchRequestAddReplace, Op
from cc_clients_python_lib.http_status import HttpStatus
from cc_clients_python_lib.cc_openapi_v2_1.sql.v1 import Statement, StatementSpec
from cc_clients_python_lib.kafka_client import KafkaClient
from cc_clients_python_lib.schema_registry_client import SchemaRegistryClient


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

# Constants for the drop stages.
# These are used to track the progress of the drop table operation.
# The keys are the stage names and the values are the stage descriptions.
# The stage names are used in the drop_stages dictionary to track the progress of the operation.
# The stage descriptions are used in the log messages to provide more information about the operation.
DROP_STAGES = {
    "statement_drop": "statement_drop",
    "kafka_key_schema_subject_drop": "kafka_key_schema_subject_drop",
    "kafka_value_schema_subject_drop": "kafka_value_schema_subject_drop",
    "kafka_topic_drop": "kafka_topic_drop",
    "table_drop": "table_drop"
}

# Default values.
DEFAULT_PAGE_SIZE = 10

# Query Parameters.
QUERY_PARAMETER_PAGE_SIZE = "page_size"
QUERY_PARAMETER_PAGE_TOKEN = "page_token"


class StatementPhase(StrEnum):
    """This class defines the Flink SQL statement phases."""
    COMPLETED = "COMPLETED"
    DEGRADED = "DEGRADED"
    DELETED = "DELETED"
    FAILED = "FAILED"
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    STOPPING = "STOPPING"


class StatementType(StrEnum):
    """This class defines the Flink SQL statement types."""
    KAFKA_SINK = "INSERT_INTO"


class FlinkClient():
    def __init__(self, flink_config: dict, private_network_base_url :str = None, kafka_config: dict = None, sr_config: dict = None):
        """This class initializes the Flink Client.

        Arg(s):            
            flink_config (dict):               The Flink configuration.
            private_network_base_url (str):    (Optional) The private network base URL.
            kafka_config (dict):               (Optional) The Kafka configuration.
            sr_config (dict):                  (Optional) The Schema Registry configuration.
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

        # Set the base URL for the Flink SQL API.
        # If the private network base URL is provided, use it. Otherwise, use the default base URL.
        if private_network_base_url is not None:
            self.flink_sql_base_url = f"https://{private_network_base_url}/sql/v1/organizations/{self.organization_id}/environments/{self.environment_id}/"
        else:
            self.flink_sql_base_url = f"https://flink.{self.cloud_region}.{self.cloud_provider}.confluent.cloud/sql/v1/organizations/{self.organization_id}/environments/{self.environment_id}/"
        self.flink_compute_pool_base_url = "https://api.confluent.cloud/fcpm/v2/compute-pools"

        # If the kafka_config is supplied, instantiate the Kafka Client.
        if kafka_config is not None:
            self.kafka_client = KafkaClient(kafka_config)

        # If the sr_config is supplied, instantiate the Schema Registry Client.
        if sr_config is not None:
            self.sr_client = SchemaRegistryClient(sr_config)

    def get_statement_list(self, page_size: int = DEFAULT_PAGE_SIZE) -> Tuple[int, str, Dict]:
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
        """This function submits a RESTful API call to delete a Flink SQL statement, and blocks until
        the statement moves to a COMPLETED phase.

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

            retry = 0
            max_retries = 3
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

                    if StatementPhase(statement.status.phase) == StatementPhase.COMPLETED:
                        return HttpStatus.OK, response.text
                    else:
                        retry += 1
                        if retry == max_retries:
                            return HttpStatus.ACCEPTED, f"Max retries exceeded.  Deleting the statement is stil in the {statement.status.phase} phase."
                        else:
                            time.sleep(retry_delay_in_seconds) 
                except requests.exceptions.RequestException as e:
                    retry += 1
                    if retry == max_retries:
                        return response.status_code, f"Max retries exceeded.  Fail to retrieve the statement because {e}, and the response is {response.text}.  But not sure if the statement is deleted or not."
                    elif response.status_code == HttpStatus.NOT_FOUND:
                        return HttpStatus.OK, response.text
                    else:
                        time.sleep(retry_delay_in_seconds)
        except requests.exceptions.RequestException as e:
            if response.status_code == HttpStatus.NOT_FOUND:
                return HttpStatus.OK, f"Statement {statement_name} is already deleted."
            else:
                return response.status_code, f"Fail to delete the statement because {e} and the response returned was {response.text}"
    
    def delete_statements_by_phase(self, statement_phase: StatementPhase) -> Tuple[int, str]:
        """This function deletes all Flink SQL statements by phase.

        Arg(s):
            statement_phase (StatementPhase): The Flink SQL statement phase.

        Returns:
            int:    HTTP Status Code.
            str:    HTTP Error, if applicable.
        """
        # Get the statement list.
        http_status_code, error_message, response = self.get_statement_list()

        if http_status_code != HttpStatus.OK:
            return http_status_code, error_message

        # Delete the statements by phase.
        for item in response:
            # Turn the JSON response into a Statement model.
            statement = Statement(**item)

            if StatementPhase(statement.status.phase) == statement_phase:
                http_status_code, error_message = self.delete_statement(statement.name)

                if http_status_code != HttpStatus.OK:
                    return http_status_code, error_message

        return HttpStatus.OK, ""
    
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

    def update_all_sink_statements(self, stop: bool = True, new_compute_pool_id: str = None, new_security_principal_id: str = None) -> Tuple[int, str]:
        """This function submits a RESTful API call to update all Sink Flink SQL statements.
        
        Arg(s):
            page_size (int):                 (Optional) The page size.
            stop (bool):                     (Optional) The stop flag. Default is True.
            new_compute_pool_id (str):       (Optional) The new compute pool ID.
            new_security_principal_id (str): (Optional) The new security principal ID.
            
        Returns:
            int:    HTTP Status Code.
            str:    HTTP Error, if applicable.
        """
        # Get the statement list.
        http_status_code, error_message, response = self.get_statement_list()

        if http_status_code != HttpStatus.OK:
            return http_status_code, error_message

        # Update all background statements.
        for item in response:
            # Turn the JSON response into a Statement model.
            statement = Statement(**item)

            if statement.status.traits.sql_kind == StatementType.KAFKA_SINK:
                http_status_code, error_message = self.update_statement(statement.name, stop=stop, new_compute_pool_id=new_compute_pool_id, new_security_principal_id=new_security_principal_id)

                if http_status_code != HttpStatus.ACCEPTED:
                    return http_status_code, error_message

        return HttpStatus.ACCEPTED, ""

    def update_statement(self, statement_name: str, stop: bool, new_compute_pool_id: str = None, new_security_principal_id: str = None) -> Tuple[int, str]:
        """This function submits a RESTful API call to first stop the statement, and
        then update the mutable attributes of a Flink SQL statement.

        Arg(s):
            statement_name (str):           The current Flink SQL statement name.
            stop (bool):                    The stop flag.
            new_compute_pool_id (str):      (Optional) The new compute pool ID.
            new_security_principal_id (str):(Optional) The new security principal ID.

        Returns:
            int:    HTTP Status Code.
            str:    HTTP Error, if applicable.
        """
        http_status_code, error_message = self.stop_statement(statement_name=statement_name)
        if http_status_code != HttpStatus.OK:
            return http_status_code, error_message
        else:
            http_status_code, error_message = self.__update_statement(statement_name=statement_name, new_compute_pool_id=new_compute_pool_id, new_security_principal_id=new_security_principal_id)

            if http_status_code == HttpStatus.OK and not stop:
                http_status_code, error_message = self.stop_statement(statement_name=statement_name, stop=False)

            return http_status_code, error_message

    def stop_statement(self, statement_name: str, stop: bool = True) -> Tuple[int, str]:
        """This function submits a RESTful API call to stop or start the Flink SQL statement.

        Note: "Confluent Cloud for Apache Flink enforces a 30-day retention for statements in
        terminal states." 

        Arg(s):
            statement_name (str):  The Flink SQL statement name.
            stop (bool):           (Optional) The stop flag. Default is True.

        Returns:
            int:    HTTP Status Code.
            str:    HTTP Error, if applicable.
        """
        patch_request = []
        patch_request.append(json.loads(
            JsonPatchRequestAddReplace(
                path="/spec/stopped", 
                value=stop, 
                op=Op.replace).model_dump_json()))

        # Send a PATCH request to update the status of the statement.
        response = requests.patch(url=f"{self.flink_sql_base_url}statements/{statement_name}",
                                  data=json.dumps(patch_request),
                                  auth=HTTPBasicAuth(self.flink_api_key, self.flink_api_secret))
        
        try:
            # Raise HTTPError, if occurred.
            response.raise_for_status()
            return response.status_code, response.text
        except Exception as e:
            return response.status_code, f"Failed to {"stop" if stop else "resume"} the statement because {e}, and the response is {response.text}"
    
    def drop_table(self, catalog_name: str, database_name: str, table_name: str) -> Tuple[bool, str, Dict]:
        """Drop a table and its dependencies (i.e., all associated Flink statements, Kafka Topic, and Schemas).
        This method will drop the table and its dependencies, including the Kafka topic and any statements that
        reference the table.  It will also delete any statements that are in a failed state associated with the
        table.
        
        Args:
            catalog_name (str): The catalog name.
            database_name (str): The database name.
            table_name (str): The table name.
            
        Returns:
            bool:   The success status.
            str:    The error message.
            dict:   The response.
        """
        # Regular expression search pattern to find the table name within a DROP, INSERT or SELECT statement.
        search_pattern = r'(?:drop|from|insert)\s+([-.`\w+\s]+?)\s*(?=\;|\)|\(|values)'

        # Initialize the variables.
        drop_stages = {}
        
        # Retrieve a list of all the statements in a Flink region.
        http_status_code, error_message, response = self.get_statement_list()
        if http_status_code != HttpStatus.OK:
            return False, error_message, {}
        
        # Iterate through the list of statements.
        number_of_deleted_statements = 0
        for item in response:
            # Turn the JSON response into a Statement model.
            statement = Statement(**item)

            query = statement.spec.statement.lower()

            # Find the table name in the query.
            candidate_find = re.search(search_pattern, query)

            # If the table name is found in the statement query, then statement is deleted.
            if candidate_find:
                if StatementPhase(statement.status.phase) == StatementPhase.FAILED:
                    # If the statement is in a FAILED phase, then statement is deleted.
                    if statement.spec.properties["sql.current-catalog"] == catalog_name and table_name in candidate_find.group(1):
                        http_status_code, error_message = self.delete_statement(statement.name)
                        if http_status_code != HttpStatus.OK:
                            return False, error_message, {}
                        else:
                            number_of_deleted_statements += 1
                else:
                    # If the statement is not in a FAILED phase, then statement is deleted.
                    if statement.spec.properties["sql.current-catalog"] == catalog_name and statement.spec.properties["sql.current-database"] == database_name and table_name in candidate_find.group(1):
                        http_status_code, error_message = self.delete_statement(statement.name)
                        if http_status_code != HttpStatus.OK:
                            return False, error_message, {}
                        else:
                            number_of_deleted_statements += 1

        # Log the drop action taken on the statement.
        drop_stages[DROP_STAGES["statement_drop"]] = f"{number_of_deleted_statements} statement{'s' if number_of_deleted_statements > 0 else ''} deleted."

        # Drop the table.
        http_status_code, error_message, exist = self.kafka_client.kafka_topic_exist(table_name.replace("`", ""))
        if http_status_code != HttpStatus.OK and http_status_code != HttpStatus.NOT_FOUND:
            drop_stages[DROP_STAGES["kafka_topic_drop"]] = f"Unable to confirm if the Kafka topic exist.  Got {http_status_code} with {error_message}."
            return False, error_message, drop_stages
        
        if exist:
            # Initialize the retry mechanism variables.
            retry = 0
            max_retries = 3
            retry_delay_in_seconds = 15

            while retry <= max_retries:
                # Submits a DROP TABLE statement, which removes a table definition from Apache Flink® and, depending
                # on the table type, will also delete associated resources like the Kafka topic and schemas in Schema 
                # Registry.
                http_status_code, error_message, response = self.submit_statement(f"drop-{table_name}-{str(uuid.uuid4())}",
                                                                                  f"DROP TABLE {table_name};",
                                                                                  {"sql.current-catalog": catalog_name, "sql.current-database": database_name})

                if http_status_code >= HttpStatus.OK and http_status_code <= HttpStatus.NO_CONTENT:
                    #
                    time.sleep(1)
                    topic_check_retry = 0
                    topic_name = table_name.replace("`", "")

                    while topic_check_retry <= max_retries:
                        http_status_code, error_message, exist = self.kafka_client.kafka_topic_exist(topic_name)
                        if http_status_code != HttpStatus.OK and http_status_code != HttpStatus.NOT_FOUND:
                            return False, error_message, drop_stages
                        
                        if not exist:
                            drop_stages[DROP_STAGES["kafka_topic_drop"]] = "Kafka topic dropped."
                            drop_stages[DROP_STAGES["table_drop"]] = "Table dropped."
                            
                            succeed, stage = self.__delete_subject_schema(f"{topic_name}-key")
                            drop_stages[DROP_STAGES["kafka_key_schema_subject_drop"]] = stage

                            succeed, stage = self.__delete_subject_schema(f"{topic_name}-value")
                            drop_stages[DROP_STAGES["kafka_value_schema_subject_drop"]] = stage

                            return succeed, error_message, drop_stages
                        else:
                            # If the topic still exists, then wait for a retry delay and check again.
                            if topic_check_retry == max_retries:
                                # If the maximum number of retries is reached, then delete the Kafka topic.
                                # This is a last resort to ensure that the topic is deleted.
                                http_status_code, error_message = self.kafka_client.delete_kafka_topic(topic_name)

                                if http_status_code != HttpStatus.OK and http_status_code != HttpStatus.NOT_FOUND:
                                    drop_stages[DROP_STAGES["kafka_topic_drop"]] = "Kafka topic dropped."
                                    drop_stages[DROP_STAGES["table_drop"]] = "Table dropped."

                                    succeed, stage = self.__delete_subject_schema(f"{topic_name}-key")
                                    drop_stages[DROP_STAGES["kafka_key_schema_subject_drop"]] = stage

                                    succeed, stage = self.__delete_subject_schema(f"{topic_name}-value")
                                    drop_stages[DROP_STAGES["kafka_value_schema_subject_drop"]] = stage

                                    return succeed, error_message, drop_stages
                                else:
                                    drop_stages[DROP_STAGES["kafka_topic_drop"]] = "Kafka topic drop failed."
                                    drop_stages[DROP_STAGES["table_drop"]] = "Table drop failed."
                                    return False, "Fail to Drop the Kafka Topic.", drop_stages
                            else:
                                time.sleep(retry_delay_in_seconds)
                                topic_check_retry += 1
                else: 
                    time.sleep(retry_delay_in_seconds)
                    retry += 1

            # If the maximum number of retries is reached, then return an error.
            drop_stages[DROP_STAGES["kafka_topic_drop"]] = "Kafka topic drop failed."
            drop_stages[DROP_STAGES["table_drop"]] = "Table drop failed."
            return False, "Maximum number of retries reached.", drop_stages
        else:
            drop_stages[DROP_STAGES["kafka_topic_drop"]] = "Kafka topic does not exist."
            drop_stages[DROP_STAGES["table_drop"]] = "No action was taken since backing Kafka topic does not exist."
            return True, "", drop_stages
    
    def __update_statement(self, statement_name: str, new_compute_pool_id: str = None, new_security_principal_id: str = None) -> Tuple[int, str]:
        """This private function submits a RESTful API call to update the mutable attributes of a 
        Flink SQL statement.

        Arg(s):
            statement_name (str):             The current Flink SQL statement name.
            new_compute_pool_id (str):        (Optional) The new compute pool ID.
            new_security_principal_id (str):  (Optional) The new security principal ID.

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

                # Set the stop flag, compute pool ID, and security principal ID.
                if statement.spec.stopped:
                    if new_compute_pool_id is not None:
                        statement.spec.compute_pool_id = new_compute_pool_id
                    if new_security_principal_id is not None:
                        statement.spec.principal = new_security_principal_id

                    # Send a PUT request to update the status of the statement.
                    response = requests.put(url=f"{self.flink_sql_base_url}statements/{statement_name}",
                                            data=statement.model_dump_json(),
                                            auth=HTTPBasicAuth(self.flink_api_key, self.flink_api_secret))
                    
                    try:
                        # Raise HTTPError, if occurred.
                        response.raise_for_status()

                        # Turn the JSON response into a Statement model.
                        statement = Statement(**response.json())

                        # Check if the resource version is the same.  If it is the same, the statement has successfully
                        # been updated.  If it is not the same, this indicates that the statement has been updated since
                        # the last GET request.  In this case, we need to retry the request.
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
                else:
                    # If the statement is not stopped, then we need to stop it first.
                    http_status_code, error_message = self.stop_statement(statement_name=statement_name)
                    if http_status_code != HttpStatus.OK:
                        return http_status_code, error_message
                    else:
                        retry += 1
                        if retry == max_retries:
                            return response.status_code, "Max retries exceeded.  Fail to update the statement because the statement is not stopped."
                        else:
                            time.sleep(retry_delay_in_seconds)
            except requests.exceptions.RequestException as e:
                retry += 1
                if retry == max_retries:
                    return response.status_code, f"Max retries exceeded.  Fail to retrieve the statement because {e}, and the response is {response.text}"
                else:
                    time.sleep(retry_delay_in_seconds)
    
    def __delete_subject_schema(self, subject_name: str) -> Tuple[bool, str]:
        """This private function deletes the subject schema.
        
        Arg(s):
            subject_name (str): The subject name.
            
        Returns:
            bool:   The success status.
            str:    The message.
        """
        # Initialize the retry mechanism variables.
        schema_check_retry = 0
        max_retries = 3
        retry_delay_in_seconds = 15
        while schema_check_retry <= max_retries:
            # Check if the value schema subject exists.
            http_status_code, _, _ = self.sr_client.get_topic_subject_latest_schema(subject_name)
            if http_status_code == HttpStatus.OK:
                http_status_code, _ = self.sr_client.delete_kafka_topic_value_schema_subject(subject_name)
                if http_status_code != HttpStatus.OK and http_status_code != HttpStatus.NOT_FOUND:
                    return True, f"Kafka {subject_name} was dropped."
                else:
                    return False, "Fail to drop {subject_name}.", f"Kafka {subject_name} drop failed."
            elif http_status_code == HttpStatus.NOT_FOUND:
                return True, f"Kafka {subject_name} does not exist."
            else:
                #
                if schema_check_retry == max_retries:
                    # If the value schema subject exists, then delete it.
                    http_status_code, _ = self.sr_client.delete_kafka_topic_value_schema_subject(subject_name)
                    if http_status_code != HttpStatus.OK and http_status_code != HttpStatus.NOT_FOUND:
                        return True, f"Kafka {subject_name} was dropped."
                    else:
                        return False, f"Kafka {subject_name} drop failed."
                else:
                    time.sleep(retry_delay_in_seconds)
                    schema_check_retry += 1