from typing import Dict, Tuple
import requests
from requests.auth import HTTPBasicAuth

from cc_clients_python_lib.constants import (DEFAULT_PAGE_SIZE,
                                             QUERY_PARAMETER_PAGE_SIZE,
                                             QUERY_PARAMETER_PAGE_TOKEN)


__copyright__  = "Copyright (c) 2025 Jeffrey Jonathan Jennings"
__license__    = "MIT"
__credits__    = ["Jeffrey Jonathan Jennings (J3)"]
__maintainer__ = "Jeffrey Jonathan Jennings (J3)"
__email__      = "j3@thej3.com"
__status__     = "dev"


# Environment Config Keys
ENVIRONMENT_CONFIG = {
    "confluent_cloud_api_key": "confluent_cloud_api_key",
    "confluent_cloud_api_secret": "confluent_cloud_api_secret"
}


class EnvironmentClient():
    def __init__(self, environment_config: dict):
        self.confluent_cloud_api_key = str(environment_config[ENVIRONMENT_CONFIG["confluent_cloud_api_key"]])
        self.confluent_cloud_api_secret = str(environment_config[ENVIRONMENT_CONFIG["confluent_cloud_api_secret"]])
        self.base_url = "https://api.confluent.cloud"

    def create_kafka_api_key(self, kafka_cluster_id: str, principal_id: str) -> Tuple[int, str, Dict]:
        """This function submits a RESTful API call to create a Kafka API key pair.
        Reference: https://docs.confluent.io/cloud/current/api.html#tag/API-Keys-(iamv2)/operation/createIamV2ApiKey

        Arg(s):
            kafka_cluster_id (str):  The Kafka cluster ID.
            principal_id (str): The principal ID for the Kafka API key.

        Return(s):
            Tuple[int, str, Dict]: A tuple of the HTTP status code, the error message (if any), and the Kafka API key pair.
        """
        payload = {
            "spec": {
                "display_name": "Kafka Cluster API Key",
                "description": "API key for Kafka cluster operations",
                "owner": {
                    "id": principal_id
                },
                "resource": {
                    "id": kafka_cluster_id
                }
            }
        }

        response = requests.post(url=f"{self.base_url}/iam/v2/api-keys",
                                 auth=HTTPBasicAuth(self.confluent_cloud_api_key, self.confluent_cloud_api_secret),
                                 json=payload)
        
        try:
            # Raise HTTPError, if occurred.
            response.raise_for_status()

            api_key_pair = {}
            api_key_pair["key"] = response.json().get("id")
            api_key_pair["secret"] = response.json().get("spec").get("secret")

            return response.status_code, "", api_key_pair
        except requests.exceptions.RequestException as e:
            return response.status_code, f"Fail to create the Kafka API key pair because {e}.  The error details are: {response.json() if response.content else {}}", response.json() if response.content else {}

    def delete_kafka_api_key(self, api_key: str) -> Tuple[int, str]:
        """This function submits a RESTful API call to delete a Kafka API key pair.
        Reference: https://docs.confluent.io/cloud/current/api.html#tag/API-Keys-(iamv2)/operation/deleteIamV2ApiKey

        Arg(s):
            api_key (str):  The Kafka API key.

        Return(s):
            Tuple[int, str]: A tuple of the HTTP status code, and error message (if any).
        """
        response = requests.delete(url=f"{self.base_url}/iam/v2/api-keys/{api_key}",
                                   auth=HTTPBasicAuth(self.confluent_cloud_api_key, self.confluent_cloud_api_secret))
        
        try:
            # Raise HTTPError, if occurred.
            response.raise_for_status()

            return response.status_code, ""
        except requests.exceptions.RequestException as e:
            return response.status_code, f"Fail to delete the Kafka API key pair because {e}.  The error details are: {response.json() if response.content else {}}"

    def get_environment_list(self, page_size: int = DEFAULT_PAGE_SIZE) -> Tuple[int, str, Dict | None]:
        """This function submits a RESTful API call to get a list of environments.
        Reference: https://docs.confluent.io/cloud/current/api.html#tag/Environments-(orgv2)/operation/listOrgV2Environments

        Arg(s):
            page_size (int):  The page size.

        Return(s):
            Tuple[int, str, Dict | None]: A tuple of the HTTP status code, the response text, and the Environments list.
        """
        http_status_code, error_message, raw_environments = self.__get_resource_list(url=f"{self.base_url}/org/v2/environments",
                                                                                 use_init_param=True,
                                                                                 page_size=page_size)

        if http_status_code != 200:
            return http_status_code, error_message, None
        else:
            environments = []
            for raw_environment in raw_environments:
                environment = {}
                environment["id"] = raw_environment.get("id")
                environment["display_name"] = raw_environment.get("display_name")

                # Handle optional fields.
                try:
                    environment["stream_governance_package_name"] = raw_environment.get("stream_governance_config").get("package")
                except AttributeError:
                    environment["stream_governance_package_name"] = ""
                environments.append(environment)

            return http_status_code, error_message, environments


    def get_kafka_cluster_list(self, environment_id: str, page_size: int = DEFAULT_PAGE_SIZE) -> Tuple[int, str, Dict]:
        """This function submits a RESTful API call to get a list of Kafka clusters.
        Reference: https://docs.confluent.io/cloud/current/api.html#tag/Clusters-(cmkv2)/operation/listCmkV2Clusters

        Arg(s):
            environment_id (str):  The environment ID.
            page_size (int, Optional):  The page size. Defaults to DEFAULT_PAGE_SIZE.

        Return(s):
            Tuple[int, str, Dict]: A tuple of the HTTP status code, the response text, and the Kafka cluster list.
        """
        http_status_code, error_message, raw_kafka_clusters = self.__get_resource_list(url=f"{self.base_url}/cmk/v2/clusters?environment={environment_id}",
                                                                                       use_init_param=False,
                                                                                       page_size=page_size)
        if http_status_code != 200:
            return http_status_code, error_message, None
        else:
            kafka_clusters = []
            for raw_kafka_cluster in raw_kafka_clusters:
                kafka_cluster = {}
                kafka_cluster["id"] = raw_kafka_cluster.get("id")
                kafka_cluster["display_name"] = raw_kafka_cluster.get("spec").get("display_name")
                kafka_cluster["cloud_provider"] = raw_kafka_cluster.get("spec").get("cloud")
                kafka_cluster["region_name"] = raw_kafka_cluster.get("spec").get("region")
                kafka_cluster["environment_id"] = raw_kafka_cluster.get("spec").get("environment").get("id")
                kafka_cluster["cluster_type_name"] = raw_kafka_cluster.get("spec").get("config").get("kind")
                kafka_cluster["http_endpoint"] = raw_kafka_cluster.get("spec").get("http_endpoint")
                kafka_cluster["kafka_bootstrap_endpoint"] = raw_kafka_cluster.get("spec").get("kafka_bootstrap_endpoint").replace("SASL_SSL://", "")
                kafka_clusters.append(kafka_cluster)

            return http_status_code, error_message, kafka_clusters

    def __get_resource_list(self, url: str, use_init_param: bool, page_size: int = DEFAULT_PAGE_SIZE) -> Tuple[int, str, Dict]:
        """This function submits a RESTful API call to get a list of Resources.

        Arg(s):
            page_size (int):  The page size.
            url (str):       The URL for the RESTful API call.
            use_init_param (bool):  Whether to use the init parameter.

        Return(s):
            Tuple[int, str, Dict]: A tuple of the HTTP status code, the response text, and the Resource list.
        """
        # Initialize the page token, Resource list, and query parameters.
        page_token = "ITERATE_AT_LEAST_ONCE"
        resources = []
        query_parameters = f"{'?' if use_init_param else '&'}{QUERY_PARAMETER_PAGE_SIZE}={page_size}"
        page_token_parameter_length = len(f"{'?' if use_init_param else '&'}{QUERY_PARAMETER_PAGE_TOKEN}=")

        # Iterate to get all the Resources.
        while page_token != "":
            # Set the query parameters.
            if page_token != "ITERATE_AT_LEAST_ONCE":
                query_parameters = f"{'?' if use_init_param else '&'}{QUERY_PARAMETER_PAGE_SIZE}={page_size}&{QUERY_PARAMETER_PAGE_TOKEN}={page_token}"

            # Send a GET request to get the next collection of resources.
            response = requests.get(url=f"{url}{query_parameters}",
                                    auth=HTTPBasicAuth(self.confluent_cloud_api_key, self.confluent_cloud_api_secret))
            
            try:
                # Raise HTTPError, if occurred.
                response.raise_for_status()

                # Append the next collection of Resources to the current Resource list.
                if response.json().get("data") is not None:
                    resources.extend(response.json().get("data"))

                # Retrieve the page token from the next page URL.
                next_page_url = str(response.json().get("metadata").get("next"))
                page_token = next_page_url[next_page_url.find(f"?{QUERY_PARAMETER_PAGE_TOKEN}=") + page_token_parameter_length:]

            except requests.exceptions.RequestException as e:
                return response.status_code, f"Fail to retrieve the resource list because {e}", response.json() if response.content else {}

        return response.status_code, response.text, resources