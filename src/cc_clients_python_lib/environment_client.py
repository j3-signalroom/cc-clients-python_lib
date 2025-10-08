from typing import Dict, Tuple

from cc_clients_python_lib.common import get_resource_list
from cc_clients_python_lib.constants import DEFAULT_PAGE_SIZE


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

    def get_environments(self, page_size: int = DEFAULT_PAGE_SIZE) -> Tuple[int, str, Dict | None]:
        """This function submits a RESTful API call to get a list of environments.
        Reference: https://docs.confluent.io/cloud/current/api.html#tag/Environments-(orgv2)/operation/listOrgV2Environments

        Arg(s):
            page_size (int):  The page size.

        Return(s):
            Tuple[int, str, Dict | None]: A tuple of the HTTP status code, the response text, and the Environments dictionary.
        """
        http_status_code, error_message, raw_environments = get_resource_list(cloud_api_key=self.confluent_cloud_api_key,
                                                                              cloud_api_secret=self.confluent_cloud_api_secret,
                                                                              url=f"{self.base_url}/org/v2/environments",
                                                                              use_init_param=True,
                                                                              page_size=page_size)

        if http_status_code != 200:
            return http_status_code, error_message, None
        else:
            environments = {}
            for raw_environment in raw_environments:
                environment = {}
                environment["id"] = raw_environment.get("id")
                environment["display_name"] = raw_environment.get("display_name")

                # Handle optional fields.
                try:
                    environment["stream_governance_package_name"] = raw_environment.get("stream_governance_config").get("package")
                except AttributeError:
                    environment["stream_governance_package_name"] = ""
                environments[environment["id"]] = environment

            return http_status_code, error_message, environments


    def get_kafka_clusters(self, environment_id: str, page_size: int = DEFAULT_PAGE_SIZE) -> Tuple[int, str, Dict]:
        """This function submits a RESTful API call to get a list of Kafka clusters.
        Reference: https://docs.confluent.io/cloud/current/api.html#tag/Clusters-(cmkv2)/operation/listCmkV2Clusters

        Arg(s):
            environment_id (str):  The environment ID.
            page_size (int, Optional):  The page size. Defaults to DEFAULT_PAGE_SIZE.

        Return(s):
            Tuple[int, str, Dict]: A tuple of the HTTP status code, the response text, and the Kafka clusters dictionary.
        """
        http_status_code, error_message, raw_kafka_clusters = get_resource_list(cloud_api_key=self.confluent_cloud_api_key,
                                                                                cloud_api_secret=self.confluent_cloud_api_secret,
                                                                                url=f"{self.base_url}/cmk/v2/clusters?environment={environment_id}",
                                                                                use_init_param=False,
                                                                                page_size=page_size)
        if http_status_code != 200:
            return http_status_code, error_message, None
        else:
            kafka_clusters = {}
            for raw_kafka_cluster in raw_kafka_clusters:
                kafka_cluster = {}
                kafka_cluster["id"] = raw_kafka_cluster.get("id")
                kafka_cluster["display_name"] = raw_kafka_cluster.get("spec").get("display_name")
                kafka_cluster["cloud_provider"] = raw_kafka_cluster.get("spec").get("cloud")
                kafka_cluster["region_name"] = raw_kafka_cluster.get("spec").get("region")
                kafka_cluster["environment_id"] = raw_kafka_cluster.get("spec").get("environment").get("id")
                kafka_cluster["cluster_type_name"] = raw_kafka_cluster.get("spec").get("config").get("kind")
                kafka_cluster["http_endpoint"] = raw_kafka_cluster.get("spec").get("http_endpoint")
                kafka_cluster["kafka_bootstrap_endpoint"] = raw_kafka_cluster.get("spec").get("kafka_bootstrap_endpoint").lower().replace("sasl_ssl://", "")
                kafka_clusters[kafka_cluster["id"]] = kafka_cluster

            return http_status_code, error_message, kafka_clusters
