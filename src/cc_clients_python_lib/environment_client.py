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
    "environment_id": "environment_id",
    "confluent_cloud_api_key": "confluent_cloud_api_key",
    "confluent_cloud_api_secret": "confluent_cloud_api_secret"
}


class EnvironmentClient():
    def __init__(self, environment_config: dict):
        self.confluent_cloud_api_key = str(environment_config[ENVIRONMENT_CONFIG["confluent_cloud_api_key"]])
        self.confluent_cloud_api_secret = str(environment_config[ENVIRONMENT_CONFIG["confluent_cloud_api_secret"]])
        self.environment_id = environment_config[ENVIRONMENT_CONFIG["environment_id"]]
        self.base_url = "https://api.confluent.cloud"

    def get_environment_list(self, page_size: int = DEFAULT_PAGE_SIZE) -> Tuple[int, str, Dict]:
        """This function submits a RESTful API call to get a list of environments.
        Reference: https://docs.confluent.io/cloud/current/api.html#tag/Environments-(orgv2)/operation/listOrgV2Environments

        Arg(s):
            page_size (int):  The page size.

        Return(s):
            Tuple[int, str, Dict]: A tuple of the HTTP status code, the response text, and the Environments list.
        """
        return self.__get_resource_list(url=f"{self.base_url}/org/v2/environments",
                                        use_init_param=True,
                                        page_size=page_size)

    def get_kafka_cluster_list(self, page_size: int = DEFAULT_PAGE_SIZE) -> Tuple[int, str, Dict]:
        """This function submits a RESTful API call to get a list of Kafka clusters.
        Reference: https://docs.confluent.io/cloud/current/api.html#tag/Clusters-(cmkv2)/operation/listCmkV2Clusters

        Arg(s):
            page_size (int):  The page size.

        Return(s):
            Tuple[int, str, Dict]: A tuple of the HTTP status code, the response text, and the Kafka cluster list.
        """
        return self.__get_resource_list(url=f"{self.base_url}/cmk/v2/clusters?environment={self.environment_id}",
                                        use_init_param=False,
                                        page_size=page_size)

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
                resources.extend(response.json().get("data"))

                # Retrieve the page token from the next page URL.
                next_page_url = str(response.json().get("metadata").get("next"))
                page_token = next_page_url[next_page_url.find(f"&{QUERY_PARAMETER_PAGE_TOKEN}=") + page_token_parameter_length:]

            except requests.exceptions.RequestException as e:
                return response.status_code, f"Fail to retrieve the resource list because {e}", response.json() if response.content else {}

        return response.status_code, response.text, resources