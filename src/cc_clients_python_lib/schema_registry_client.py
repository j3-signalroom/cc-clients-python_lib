import time
from typing import Tuple
import requests
from requests.auth import HTTPBasicAuth
import fastavro
from enum import StrEnum
import json

from cc_clients_python_lib.http_status import HttpStatus
 

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
        # Send a GET request to get the subject's latest schema.
        response = requests.get(url=f"{self.schema_registry_url}/subjects/{subject_name}/versions/latest", auth=HTTPBasicAuth(self.api_key, self.api_secret))
 
        try:
            # Raise HTTPError, if occurred.
            response.raise_for_status()
 
            # Return the latest schema for the subject.
            return response.status_code, response.text, response.json().get("schema")
        except requests.exceptions.RequestException as e:
            return response.status_code, f"Error retrieving subject '{subject_name}': {e}",  response.json() if response.content else {}
       
    def register_topic_subject_schema(self, subject_name: str, subject_schema, force: bool = False) -> Tuple[int, str, int]:
        """This function submits a RESTful API call to register the subject's schema.
 
        Arg(s):
            schema_registry_confg (dict):  The Schema Registry Cluster configuration.
            subject_name (str):            The Kafka topic subject name.
            subject_schema (any):          The subject's new schema to be registered.
            force (bool):                  (Optional)  A flag to force the registration of the schema, by setting the Compatibility
                                           to NONE, register schema, and then set back to orginal setting.
 
        Returns:
            int:  HTTP Status Code.
            str:  HTTP Error, if applicable.
            int:  The schema ID of the newly created schema.
        """
        if force:
            # Get the current Kafka topic subject compatibility level.
            http_status_code, http_error_message, current_compatibility_level = self.get_topic_subject_compatibility_level(subject_name)
            match http_status_code:
                case HttpStatus.OK:
                    pass
                case HttpStatus.NOT_FOUND:
                    http_status_code, http_error_message, current_compatibility_level = self.get_global_topic_subject_compatibility_level()
                    if current_compatibility_level == CompatibilityLevel.UNASSIGNED:
                        return http_status_code, f"Error retrieving the global compatibility level because {http_error_message}.", -1
                case _:
                    return http_status_code, f"Error retrieving the current compatibility level because {http_error_message}.", -1
        
            # Set the topic subject compatibility setting to "NONE", so the existing subject's latest schema
            # can be overwritten.
            http_status_code, http_error_message = self.set_topic_subject_compatibility_level(subject_name, CompatibilityLevel.NONE)
            if http_status_code != HttpStatus.OK:
                return http_status_code, f"Error setting the current compatibility level because {http_error_message}.", -1
    
        # Convert the Avro schema to a string.
        if isinstance(subject_schema, dict):
            schema_str, error_message = self.convert_avro_schema_into_string(subject_name, subject_schema)
            if error_message != "":
                return HttpStatus.INTERNAL_SERVER_ERROR, error_message, -1
        else:
            schema_str = subject_schema        
   
        # Send a POST request to register the schema.
        response = requests.post(url=f"{self.schema_registry_url}/subjects/{subject_name}/versions",
                                 json={"schema": schema_str},
                                 auth=HTTPBasicAuth(self.api_key, self.api_secret))
 
        try:    
            # Raise HTTPError, if occurred.
            response.raise_for_status()

            schema_id = response.json().get("id")
            schema_registration_result = response.text

            if force:
                # Restore the topic subject compatibility level.
                http_status_code, http_error_message = self.set_topic_subject_compatibility_level(subject_name, current_compatibility_level)
                if http_status_code == HttpStatus.OK:
                    return response.status_code, schema_registration_result, schema_id
                else:
                    return http_status_code, http_error_message, -1
            else:
                return response.status_code, schema_registration_result, schema_id
        except requests.exceptions.RequestException as e:
            return response.status_code, f"Error registering subject '{subject_name}': {e}", -1
   
    def set_topic_subject_compatibility_level(self, subject_name: str, compatibility_level: CompatibilityLevel) -> Tuple[int, str]:
        """This function submits a RESTful API call to set the topic subject compatibility level.
 
        Arg(s):
            schema_registry_confg (dict):               The Schema Registry Cluster configuration.
            subject_name (str):                         The Kafka topic subject name.
            compatibility_level (CompatibilityLevel):   The compatibility setting.
 
        Returns:
            int:  HTTP Status Code.
            str:  HTTP Error, if applicable.
        """
        # Send a PUT request to update the compatibility setting of the subject.
        response = requests.put(url=f"{self.schema_registry_url}/config/{subject_name}",
                                json={"compatibility": compatibility_level.value},
                                auth=HTTPBasicAuth(self.api_key, self.api_secret))

        try:
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
            response = requests.get(endpoint, auth=HTTPBasicAuth(self.api_key, self.api_secret))
 
            # Raise HTTPError, if occurred.
            response.raise_for_status()
 
            # Return the success code and message.
            return response.status_code, response.text, CompatibilityLevel(response.json()['compatibilityLevel'])
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
        # Send a GET the Topic Subject compatibility setting level.
        response = requests.get(url=f"{self.schema_registry_url}/config", auth=HTTPBasicAuth(self.api_key, self.api_secret))

        try:
            # Raise HTTPError, if occurred.
            response.raise_for_status()
 
            # Return the success code and message.
            return response.status_code, response.text, CompatibilityLevel(response.json()['compatibilityLevel'])
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
        
    def delete_kafka_topic_key_schema_subject(self, kafka_topic_name) -> Tuple[int, str]:
        """This function submits a RESTful API call to delete the topic schema subject.
 
        Arg(s):
            kafka_topic_name (str):  The Kafka topic name of the key schema subject.
 
        Returns:
            int: HTTP Status Code.
            str: HTTP Error, if applicable.
        """
        # Send a DELETE to perform a soft-delete of all version of the schema.
        delete_response = requests.delete(url=f"{self.schema_registry_url}/subjects/{kafka_topic_name}-key", auth=HTTPBasicAuth(self.api_key, self.api_secret))
 
        try:
            # Raise HTTPError, if occurred.
            delete_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return delete_response.status_code, f"Delete topic schema subject soft-delete failed because {e} and the response returned was {delete_response.text}"
 
        try:
            # Send a DELETE to perform a hard-delete of all version of the schema.
            delete_response = requests.delete(f"{self.schema_registry_url}/subjects/{kafka_topic_name}-key?permanent=true", auth=HTTPBasicAuth(self.api_key, self.api_secret))
 
            # Raise HTTPError, if occurred.
            delete_response.raise_for_status()

            retry = 0
            max_retries = 3
            retry_delay_in_seconds = 5

            while retry < max_retries:
                # Send a GET request to get the subject's latest schema.
                get_response = requests.get(url=f"{self.schema_registry_url}/subjects/{kafka_topic_name}-key/versions/latest", auth=HTTPBasicAuth(self.api_key, self.api_secret))
        
                try:
                    # Raise HTTPError, if occurred.
                    get_response.raise_for_status()

                    retry += 1
                    if retry == max_retries:
                        return get_response.status_code, f"Max retries exceeded.  Fail to check if the subject '{kafka_topic_name}-key' exist because the response is {get_response.text}.  But not sure if the Subject Schema Key is deleted or not."
                    else:
                        time.sleep(retry_delay_in_seconds)
                except requests.exceptions.RequestException as e:
                    retry += 1
                    if retry == max_retries:
                        return get_response.status_code, f"Max retries exceeded.  Fail to check if the subject '{kafka_topic_name}-key' exist because {e}, and the response is {get_response.text}.  But not sure if the Subject Schema Key is deleted or not."
                    elif get_response.status_code == HttpStatus.NOT_FOUND:
                        return HttpStatus.OK, delete_response.text
                    else:
                        time.sleep(retry_delay_in_seconds)
        except requests.exceptions.RequestException as e:
            return delete_response.status_code, f"Delete topic key schema subject hard-delete failed because {e} and the response returned was {delete_response.text}"
        
    def delete_kafka_topic_value_schema_subject(self, kafka_topic_name) -> Tuple[int, str]:
        """This function submits a RESTful API call to delete the topic value schema subject.
 
        Arg(s):
            kafka_topic_name (str):  The Kafka topic name of the value schema subject.
 
        Returns:
            int: HTTP Status Code.
            str: HTTP Error, if applicable.
        """
        # Send a DELETE to perform a soft-delete of all version of the schema.
        delete_response = requests.delete(url=f"{self.schema_registry_url}/subjects/{kafka_topic_name}-value", auth=HTTPBasicAuth(self.api_key, self.api_secret))
 
        try:
            # Raise HTTPError, if occurred.
            delete_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return delete_response.status_code, f"Delete topic schema subject soft-delete failed because {e} and the response returned was {delete_response.text}"
        
        # The Confluent Schema Registry endpoint to delete the topic schema subject hard-delete of all versions registered.
        # Send a DELETE to perform a hard-delete of all version of the schema.
        delete_response = requests.delete(url=f"{self.schema_registry_url}/subjects/{kafka_topic_name}-value?permanent=true", auth=HTTPBasicAuth(self.api_key, self.api_secret))
 
        try:
            # Raise HTTPError, if occurred.
            delete_response.raise_for_status()

            retry = 0
            max_retries = 3
            retry_delay_in_seconds = 5

            while retry < max_retries:
                # Send a GET request to get the subject's latest schema.
                get_response = requests.get(url=f"{self.schema_registry_url}/subjects/{kafka_topic_name}-value/versions/latest", auth=HTTPBasicAuth(self.api_key, self.api_secret))
        
                try:
                    # Raise HTTPError, if occurred.
                    get_response.raise_for_status()

                    retry += 1
                    if retry == max_retries:
                        return get_response.status_code, f"Max retries exceeded.  Fail to check if the subject '{kafka_topic_name}-value' exist because the response is {get_response.text}.  But not sure if the Subject Schema Value is deleted or not."
                    else:
                        time.sleep(retry_delay_in_seconds)
                except requests.exceptions.RequestException as e:
                    retry += 1
                    if retry == max_retries:
                        return get_response.status_code, f"Max retries exceeded.  Fail to check if the subject '{kafka_topic_name}-value' exist because {e}, and the response is {get_response.text}.  But not sure if the Subject Schema Value is deleted or not."
                    elif get_response.status_code == HttpStatus.NOT_FOUND:
                        return HttpStatus.OK, delete_response.text
                    else:
                        time.sleep(retry_delay_in_seconds)
        except requests.exceptions.RequestException as e:
            return delete_response.status_code, f"Delete topic value schema subject hard-delete failed because {e} and the response returned was {delete_response.text}"

 