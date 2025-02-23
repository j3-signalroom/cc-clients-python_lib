from typing import Tuple
import requests
from requests.auth import HTTPBasicAuth
import fastavro
from enum import StrEnum
import json
from src.cc_clients_lib.common import HttpStatus
 

__copyright__  = "Copyright (c) 2025 Jeffrey Jonathan Jennings"
__license__    = "MIT"
__credits__    = ["Jeffrey Jonathan Jennings (J3)"]
__maintainer__ = "Jeffrey Jonathan Jennings (J3)"
__email__      = "j3@thej3.com"
__status__     = "dev"
 

# Schema Registry Config Keys.
SCHEMA_REGISTRY_CONFIG = {
    "url": "url",
    "api_key": "api_key",
    "api_secret": "api_secret"
}

# The Kafka Topic Subject Compatibility Level List.
class CompatibilityLevel(StrEnum):
    UNASSIGNED = "UNASSIGNED"
    NONE = "NONE"
    BACKWARD = "BACKWARD"
    BACKWARD_TRANSITIVE = "BACKWARD_TRANSITIVE"
    FORWARD = "FORWARD"
    FORWARD_TRANSITIVE = "FORWARD_TRANSITIVE"
    FULL = "FULL"
    FULL_TRANSITIVE = "FULL_TRANSITIVE"


# The Schema Registry Client Class.
class SchemaRegistryClient():
    def __init__(self, schema_registry_config: dict):
        self.schema_registry_url = schema_registry_config[SCHEMA_REGISTRY_CONFIG["url"]]
        self.api_key = str(schema_registry_config[SCHEMA_REGISTRY_CONFIG["api_key"]])
        self.api_secret = str(schema_registry_config[SCHEMA_REGISTRY_CONFIG["api_secret"]])
       
 
    def get_topic_subject_latest_schema(self, subject_name: str) -> Tuple[int, str, dict]:
        """This function submits a RESTful API call to get a subject's latest schema.
 
        Arg(s):
            schema_registry_confg (dict):  The Schema Registry Cluster configuration.
            subject_name (str):            The Kafka topic subject name.
 
        Returns:
            int:    HTTP Status Code.
            str:    HTTP Error, if applicable.
            dict:   The subject's latest schema.  Otherwise, an empty dict is returned.
        """
        # The Confluent Schema Registry endpoint to get the subject's latest schema.
        endpoint = f"{self.schema_registry_url}/subjects/{subject_name}/versions/latest"
 
        try:
            # Send a GET request to get the subject's latest schema.
            response = requests.get(endpoint, auth=HTTPBasicAuth(self.api_key, self.api_secret))
 
            # Raise HTTPError, if occurred.
            response.raise_for_status()
 
            # Return the latest schema for the subject.
            return HttpStatus.OK, "", response.json().get("schema")
        except requests.exceptions.RequestException as e:
            return response.status_code, f"Error retrieving subject '{subject_name}': {e}", {}
       
    def register_topic_subject_schema(self, subject_name: str, schema_str: str) -> Tuple[int, str, int]:
        """This function submits a RESTful API call to register the subject's schema.
 
        Arg(s):
            schema_registry_confg (dict):  The Schema Registry Cluster configuration.
            subject_name (str):            The Kafka topic subject name.
            schema_str (str):              The subject's new schema to be registered.
 
        Returns:
            int:  HTTP Status Code.
            str:  HTTP Error, if applicable.
            int:  The schema ID of the newly created schema.
        """
        # The Confluent Schema Registry endpoint to register the subject's schema.
        endpoint = f"{self.schema_registry_url}/subjects/{subject_name}/versions"
 
        try:    
            # Construct payload.
            payload = {
                "schema": schema_str
            }
 
            # Send a POST request to register the schema.
            response = requests.post(
                endpoint,
                json=payload,
                auth=HTTPBasicAuth(self.api_key, self.api_secret)
            )
 
            # Raise HTTPError, if occurred.
            response.raise_for_status()
 
            # Return the new schema ID of the newly registered schema.
            return HttpStatus.OK, "", response.json().get("id")
        except requests.exceptions.RequestException as e:
            return response.status_code, f"Error registering subject '{subject_name}': {e}", -1
   
    def set_topic_subject_compatibility_level(self, subject_name: str, compatibility_level: CompatibilityLevel) -> Tuple[int, str]:
        """This function submits a RESTful API call to set the topic subject compatibility level.
 
        Arg(s):
            schema_registry_confg (dict):                   The Schema Registry Cluster configuration.
            subject_name (str):                             The Kafka topic subject name.
            compatibility_level (CompatibilityLevel):   The compatibility setting.
 
        Returns:
            int:  HTTP Status Code.
            str:  HTTP Error, if applicable.
        """
        # The Confluent Schema Registry endpoint to set the subject compatibility settting.
        endpoint = f"{self.schema_registry_url}/config/{subject_name}"
 
        # The payload for updating the compatibility setting.
        payload = {"compatibility": compatibility_level.value}
 
        try:
            # Send a PUT request to update the compatibility setting of the subject.
            response = requests.put(
                endpoint,
                json=payload,
                auth=HTTPBasicAuth(self.api_key, self.api_secret)
            )
 
            # Raise HTTPError, if occurred.
            response.raise_for_status()
 
            # Return the success code and message.
            return response.status_code, f"Compatibility level changed successfully: {response.json()}"
        except requests.exceptions.RequestException as e:
            return response.status_code, f"Compatibility level changed failed because {e}"
       
    def get_topic_subject_compatibility_level(self, subject_name: str) -> Tuple[int, str, CompatibilityLevel]:
        """This function submits a RESTful API call to get the topic subject compatibility levels.
 
        Arg(s):
            schema_registry_confg (dict):                   The Schema Registry Cluster configuration.
            subject_name (str):                             The Kafka topic subject name.
 
        Returns:
            int:                  HTTP Status Code.
            str:                  HTTP Error, if applicable.
            compatibility_level:  The Topic Subject compatibility level.
        """
        # The Confluent Schema Registry endpoint to get the subject compatibility level.
        endpoint = f"{self.schema_registry_url}/config/{subject_name}"
 
        try:
            # Send a GET the Topic Subject compatibility setting level.
            response = requests.get(
                endpoint,
                auth=HTTPBasicAuth(self.api_key, self.api_secret)
            )
 
            # Raise HTTPError, if occurred.
            response.raise_for_status()
 
            # Return the success code and message.
            return response.status_code, "", CompatibilityLevel(response.json()['compatibilityLevel'])
        except requests.exceptions.RequestException as e:
            return response.status_code, f"Compatibility level changed failed because {e}", CompatibilityLevel.UNASSIGNED
 
    def get_global_topic_subject_compatibility_level(self) -> Tuple[int, str, CompatibilityLevel]:
        """This function submits a RESTful API call to get the topic subject compatibility levels.
 
        Arg(s):
            schema_registry_confg (dict):                   The Schema Registry Cluster configuration.
 
        Returns:
            int:                  HTTP Status Code.
            str:                  HTTP Error, if applicable.
            compatibility_level:  The Topic Subject compatibility level.
        """
        # The Confluent Schema Registry endpoint to get the global subject compatibility level.
        endpoint = f"{self.schema_registry_url}/config"
 
        try:
            # Send a GET the Topic Subject compatibility setting level.
            response = requests.get(
                endpoint,
                auth=HTTPBasicAuth(self.api_key, self.api_secret)
            )
 
            # Raise HTTPError, if occurred.
            response.raise_for_status()
 
            # Return the success code and message.
            return response.status_code, "", CompatibilityLevel(response.json()['compatibilityLevel'])
        except requests.exceptions.RequestException as e:
            return response.status_code, f"Compatibility level changed failed because {e}", CompatibilityLevel.UNASSIGNED
           
    def convert_avro_schema_into_string(self, subject_name: str, avro_schema: dict) -> Tuple[str, str]:
        """This function converts the Avro schema into a string.
 
        Arg(s):
            subject_name (str):  The Kafka topic subject name.
            avro_schema (dict):  The subject's Avro schema.
        """
        # Replace 's with "s to make it a proper JSON, and replace any None with null to
        # adhere to the Avro schema specification.
        schema_str = str(avro_schema).replace("'", '"')
        schema_str = schema_str.replace("None", "null")
 
        try:
            # Confirm the schema conforms to the Avro specification, and if not an exception is raised.
            schema = json.loads(schema_str)
            fastavro.parse_schema(schema)
 
            return schema_str, ""
        except Exception as e:
            return "", f"Converted Subject '{subject_name}' is invalid because {e}"
 