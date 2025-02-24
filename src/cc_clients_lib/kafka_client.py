from typing import Tuple
import requests
from requests.auth import HTTPBasicAuth


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
    "cluster_id": "cluster_id",
    "environment_id": "environment_id",
    "cloud_provider": "cloud_provider",
    "cloud_region": "cloud_region"
}

class KafkaClient():
    def __init__(self, kafka_config: dict):
        self.cluster_id = kafka_config[KAFKA_CONFIG["cluster_id"]]
        self.environment_id = kafka_config[KAFKA_CONFIG["environment_id"]]
        self.kafka_api_key = str(kafka_config[KAFKA_CONFIG["kafka_api_key"]])
        self.kafka_api_secret = str(kafka_config[KAFKA_CONFIG["kafka_api_secret"]])
        self.cloud_provider = kafka_config[KAFKA_CONFIG["cloud_provider"]]
        self.cloud_region = kafka_config[KAFKA_CONFIG["cloud_region"]]
        self.kafka_base_url = f"https://confluent.cloud/environments/{self.environment_id}/clusters/{self.cluster_id}"

    def delete_kafka_topic(self, kafka_topic_name: str) -> Tuple[int, str]:
        """This function submits a RESTful API call to delete a Kafka topic name.

        Arg(s):
            kafka_topic_name (str):  The Kafka topic name.

        Returns:
            int:    HTTP Status Code.
            str:    HTTP Error, if applicable.
        """
        # The Kafka cluster endpoint to delete a Kafka topic.
        endpoint = f"{self.kafka_base_url}topics/{kafka_topic_name}"

        try:
            # Send a DELETE request to delete the Kafka topic.
            response = requests.delete(endpoint, auth=HTTPBasicAuth(self.kafka_api_key, self.kafka_api_secret))

            # Raise HTTPError, if occurred.
            response.raise_for_status()

            return response.status_code, response.json()
        except requests.exceptions.RequestException as e:
            return response.status_code, f"Fail to delete the Kafka topic because {e}"