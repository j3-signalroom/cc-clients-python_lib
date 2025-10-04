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


def get_resource_list(cloud_api_key: str, cloud_api_secret: str, url: str, use_init_param: bool, page_size: int = DEFAULT_PAGE_SIZE) -> Tuple[int, str, Dict]:
    """This function submits a RESTful API call to get a list of Resources.

    Arg(s):
        cloud_api_key (str):    The Confluent Cloud API key.
        cloud_api_secret (str): The Confluent Cloud API secret.
        url (str):              The URL for the RESTful API call.
        use_init_param (bool):  Whether to use the init parameter.
        page_size (int, optional):        The page size.  Defaults to DEFAULT_PAGE_SIZE.

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
                                auth=HTTPBasicAuth(cloud_api_key, cloud_api_secret))
        
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