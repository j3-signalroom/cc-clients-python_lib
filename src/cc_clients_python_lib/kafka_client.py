from typing import Tuple
import requests
import time
from requests.auth import HTTPBasicAuth

from cc_clients_python_lib.http_status import HttpStatus

__copyright__  = "Copyright (c) 2025 Jeffrey Jonathan Jennings"
__license__    = "MIT"
__credits__    = ["Jeffrey Jonathan Jennings (J3)"]
__maintainer__ = "Jeffrey Jonathan Jennings (J3)"
__email__      = "j3@thej3.com"
__status__     = "dev"


# Kafka Config Keys.
KAFKA_CONFIG = {
    "kafka_api_key": "kafka_api_key",
    "kafka_api_secret": "kafka_api_secret",
    "bootstrap_server_id": "bootstrap_server_id",
    "bootstrap_server_cloud_region": "bootstrap_server_cloud_region",
    "bootstrap_server_cloud_provider": "bootstrap_server_cloud_provider",
    "kafka_cluster_id": "kafka_cluster_id"
}

class KafkaClient():
    def __init__(self, kafka_config: dict):
        self.bootstrap_server_id = kafka_config[KAFKA_CONFIG["bootstrap_server_id"]]
        self.bootstrap_server_cloud_region = kafka_config[KAFKA_CONFIG["bootstrap_server_cloud_region"]]
        self.bootstrap_server_cloud_provider = kafka_config[KAFKA_CONFIG["bootstrap_server_cloud_provider"]]
        self.kafka_cluster_id = kafka_config[KAFKA_CONFIG["kafka_cluster_id"]]
        self.kafka_api_key = str(kafka_config[KAFKA_CONFIG["kafka_api_key"]])
        self.kafka_api_secret = str(kafka_config[KAFKA_CONFIG["kafka_api_secret"]])
        self.kafka_base_url = f"https://{self.bootstrap_server_id}.{self.bootstrap_server_cloud_region}.{self.bootstrap_server_cloud_provider}.confluent.cloud/kafka/v3/clusters/{self.kafka_cluster_id}/"

    def delete_kafka_topic(self, kafka_topic_name: str) -> Tuple[int, str]:
        """This function submits a RESTful API call to delete a Kafka topic, and then blocks until the
        Kafka topic is deleted.

        Arg(s):
            kafka_topic_name (str):  The Kafka topic name.

        Returns:
            int:    HTTP Status Code.
            str:    HTTP Error, if applicable.
        """
        # Send a GET request to delete the Kafka topic.
        endpoint = f"{self.kafka_base_url}topics/{kafka_topic_name}"
        delete_response = requests.delete(endpoint, auth=HTTPBasicAuth(self.kafka_api_key, self.kafka_api_secret))

        try:
            # Raise HTTPError, if occurred.
            delete_response.raise_for_status()
                  
            retry = 0
            max_retries = 3
            retry_delay_in_seconds = 5

            while retry < max_retries:
                # Send a GET request to get the Kafka topic.
                get_response = requests.get(endpoint, auth=HTTPBasicAuth(self.kafka_api_key, self.kafka_api_secret))

                try:
                    # Raise HTTPError, if occurred.
                    get_response.raise_for_status()

                    retry += 1
                    if retry == max_retries:
                        return get_response.status_code, f"Max retries exceeded.  Fail to check if the Kafka Topic exist because the response is {get_response.text}.  But not sure if the Kafka Topic is deleted or not."
                    else:
                        time.sleep(retry_delay_in_seconds)
                except requests.exceptions.RequestException as e:
                    retry += 1
                    if retry == max_retries:
                        return get_response.status_code, f"Max retries exceeded.  Fail to check if the Kafka Topic exist because {e}, and the response is {get_response.text}.  But not sure if the Kafka Topic is deleted or not."
                    elif get_response.status_code == HttpStatus.NOT_FOUND:
                        return HttpStatus.OK, delete_response.json()
                    else:
                        time.sleep(retry_delay_in_seconds)
        except requests.exceptions.RequestException as e:
            return delete_response.status_code, f"Fail to delete the Kafka topic because {e} and the response returned was {delete_response.text}"
        
    def kafka_topic_exist(self, kafka_topic_name: str) -> Tuple[int, str, bool]:
        """This function submits a RESTful API call to get a Kafka topic to see if it exist or not.

        Arg(s):
            kafka_topic_name (str):  The Kafka topic name.

        Returns:
            int:    HTTP Status Code.
            str:    HTTP Error, if applicable.
            bool:   True if the Kafka topic exist, False otherwise.
        """
        # Send a GET request to get the Kafka topic.
        response = requests.get(f"{self.kafka_base_url}topics/{kafka_topic_name}", auth=HTTPBasicAuth(self.kafka_api_key, self.kafka_api_secret))

        try:
            # Raise HTTPError, if occurred.
            response.raise_for_status()

            return response.status_code, response.json(), True
        except requests.exceptions.RequestException as e:
            return response.status_code, f"Fail to determine if the Kafka topic exist because {e} and the response returned was {response.text}", False
    