from typing import Dict, Tuple
import requests
from requests.auth import HTTPBasicAuth

from cc_clients_python_lib.common import get_resource_list
from cc_clients_python_lib.constants import DEFAULT_PAGE_SIZE


__copyright__  = "Copyright (c) 2025 Jeffrey Jonathan Jennings"
__license__    = "MIT"
__credits__    = ["Jeffrey Jonathan Jennings (J3)"]
__maintainer__ = "Jeffrey Jonathan Jennings (J3)"
__email__      = "j3@thej3.com"
__status__     = "dev"


# IAM Config Keys
IAM_CONFIG = {
    "confluent_cloud_api_key": "confluent_cloud_api_key",
    "confluent_cloud_api_secret": "confluent_cloud_api_secret"
}

class IamClient():
    def __init__(self, iam_config: dict):
        self.confluent_cloud_api_key = str(iam_config[IAM_CONFIG["confluent_cloud_api_key"]])
        self.confluent_cloud_api_secret = str(iam_config[IAM_CONFIG["confluent_cloud_api_secret"]])
        self.base_url = "https://api.confluent.cloud"

    def get_all_api_keys_by_principal_id(self, principal_id: str, page_size: int = DEFAULT_PAGE_SIZE) -> Tuple[int, str, Dict | None]:
        """This function submits a RESTful API call to get all API keys by the Principal ID.
        Reference: https://docs.confluent.io/cloud/current/api.html#tag/API-Keys-(iamv2)/operation/listIamV2ApiKeys
        Arg(s):
            page_size (int):  The page size.

        Return(s):
            Tuple[int, str, Dict | None]: A tuple of the HTTP status code, the response text, and the Environments list.
        """
        http_status_code, error_message, raw_api_keys = get_resource_list(cloud_api_key=self.confluent_cloud_api_key,
                                                                          cloud_api_secret=self.confluent_cloud_api_secret,
                                                                          url=f"{self.base_url}/iam/v2/api-keys?spec.owner={principal_id}",
                                                                          use_init_param=False,
                                                                          page_size=page_size)

        if http_status_code != 200:
            return http_status_code, error_message, None
        else:
            api_keys = {}
            for raw_api_key in raw_api_keys:
                api_key = {}
                api_key["api_key"] = raw_api_key.get("id")
                api_key["display_name"] = raw_api_key.get("spec").get("display_name")
                api_key["description"] = raw_api_key.get("spec").get("description")
                api_key["resource_id"] = raw_api_key.get("spec").get("resource").get("id")
                api_key["resource_kind"] = raw_api_key.get("spec").get("resource").get("kind")
                api_key["environment_id"] = raw_api_key.get("spec").get("resource")["environment"]
                api_keys[raw_api_key.get("id")] = api_key

            return http_status_code, error_message, api_keys
        
    def create_api_key(self, resource_id: str, principal_id: str, display_name: str, description: str) -> Tuple[int, str, Dict]:
        """This function submits a RESTful API call to create an API key pair.
        Reference: https://docs.confluent.io/cloud/current/api.html#tag/API-Keys-(iamv2)/operation/createIamV2ApiKey

        Arg(s):
            resource_id (str):  The Resource ID.
            principal_id (str): The Principal ID for the API key.
            display_name (str): The display name for the API key.
            description (str):  The description for the API key.

        Return(s):
            Tuple[int, str, Dict]: A tuple of the HTTP status code, the error message (if any), and the API key pair.
        """
        payload = {
            "spec": {
                "display_name": display_name,
                "description": description,
                "owner": {
                    "id": principal_id
                },
                "resource": {
                    "id": resource_id
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
            api_key_pair["key"] = response.json().get("id").strip()
            api_key_pair["secret"] = response.json().get("spec").get("secret").strip()

            return response.status_code, "", api_key_pair
        except requests.exceptions.RequestException as e:
            return response.status_code, f"Fail to create the API key pair because {e}.  The error details are: {response.json() if response.content else {}}", response.json() if response.content else {}

    def delete_api_key(self, api_key: str) -> Tuple[int, str]:
        """This function submits a RESTful API call to delete an API key pair.
        Reference: https://docs.confluent.io/cloud/current/api.html#tag/API-Keys-(iamv2)/operation/deleteIamV2ApiKey

        Arg(s):
            api_key (str):  The API key.

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
            return response.status_code, f"Fail to delete the API key pair because {e}.  The error details are: {response.json() if response.content else {}}"
