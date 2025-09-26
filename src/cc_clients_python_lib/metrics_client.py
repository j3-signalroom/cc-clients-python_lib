from datetime import datetime, timezone, timedelta
from enum import StrEnum
from typing import Dict, Tuple
import requests
from requests.auth import HTTPBasicAuth

from cc_clients_python_lib.http_status import HttpStatus
from cc_clients_python_lib.constants import DEFAULT_REQUEST_TIMEOUT_IN_SECONDS


__copyright__  = "Copyright (c) 2025 Jeffrey Jonathan Jennings"
__license__    = "MIT"
__credits__    = ["Jeffrey Jonathan Jennings (J3)"]
__maintainer__ = "Jeffrey Jonathan Jennings (J3)"
__email__      = "j3@thej3.com"
__status__     = "dev"


# Metrics Config Keys
METRICS_CONFIG = {
    "confluent_cloud_api_key": "confluent_cloud_api_key",
    "confluent_cloud_api_secret": "confluent_cloud_api_secret"
}

# Kafka Metric Types
class KafkaMetric(StrEnum):
    RECEIVED_BYTES = "io.confluent.kafka.server/received_bytes"
    RECEIVED_RECORDS = "io.confluent.kafka.server/received_records"
    SENT_BYTES = "io.confluent.kafka.server/sent_bytes"
    SENT_RECORDS = "io.confluent.kafka.server/sent_records"
    HOT_PARTITION_INGRESS = "io.confluent.kafka.server/hot_partition_ingress"
    HOT_PARTITION_EGRESS = "io.confluent.kafka.server/hot_partition_egress"

# Data Movement Types
class DataMovementType(StrEnum):
    INGRESS = "ingress"
    EGRESS = "egress"


class MetricsClient():
    def __init__(self, metrics_config: Dict):
        self.confluent_cloud_api_key = metrics_config[METRICS_CONFIG["confluent_cloud_api_key"]]
        self.confluent_cloud_api_secret = metrics_config[METRICS_CONFIG["confluent_cloud_api_secret"]]
        self.metrics_base_url = "https://api.telemetry.confluent.cloud/v2/metrics/cloud"

    def get_topic_total(self, 
                        kafka_metric: KafkaMetric, 
                        kafka_cluster_id: str, 
                        topic_name: str, 
                        query_start_time: datetime, 
                        query_end_time: datetime, 
                        timeout: int = DEFAULT_REQUEST_TIMEOUT_IN_SECONDS) -> Tuple[int, str, Dict | None, Dict | None]:
        """This function retrieves the Kafka Metric Total for a given Kafka topic within a specified time range.

        Args:
            kafka_metric (KafkaMetric): The Kafka metric to query (e.g., RECEIVED_BYTES, RECEIVED_RECORDS).
            kafka_cluster_id (str): The Kafka cluster ID.
            topic_name (str): The Kafka topic name.
            query_start_time (datetime): The start time for the query.
            query_end_time (datetime): The end time for the query.
            timeout (int, optional): The request timeout in seconds. Defaults to DEFAULT_REQUEST_TIMEOUT_IN_SECONDS.
            
        Returns:
            Tuple[int, str, Dict | None, Dict | None]: A tuple containing the HTTP status code, error
            message (if any), a dictionary with rate limit information, and a dictionary with the specified total,
            and period start and end times if successful; otherwise, None.
        """
        try:
            # Convert datetime to ISO format with milliseconds
            query_start_iso = query_start_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            query_end_iso = query_end_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

            # Query for Kafka Metric Total
            query_data = {
                "aggregations": [
                    {
                        "agg": "SUM",
                        "metric": kafka_metric.value
                    }
                ],
                "filter": {
                    "op": "AND",
                    "filters": [
                        {
                            "field": "metric.topic", 
                            "op": "EQ", 
                            "value": topic_name
                        },
                        {
                            "field": "resource.kafka.id", 
                            "op": "EQ", 
                            "value": kafka_cluster_id
                        },
                    ],
                },
                "granularity": "PT1H",
                "group_by": [
                    "metric.topic"
                ],
                "intervals": [
                    f"{query_start_iso}/{query_end_iso}"
                ]
            }
            
            response = requests.post(url=f"{self.metrics_base_url}/query",
                                     auth=HTTPBasicAuth(self.confluent_cloud_api_key, self.confluent_cloud_api_secret),
                                     json=query_data,
                                     timeout=timeout)
            
            # Extract rate limit information from response headers
            headers = dict(response.headers) if response.headers else None
            rate_limits = {}
            if headers and "ratelimit-remaining" in headers:
                rate_limits["remaining_count"] = int(headers["ratelimit-remaining"])
            if headers and "ratelimit-limit" in headers:
                rate_limits["limit_count"] = int(headers["ratelimit-limit"])
            if headers and "ratelimit-reset" in headers:
                rate_limits["reset_in_seconds"] = int(headers["ratelimit-reset"])

            try:
                # Raise HTTPError, if occurred.
                response.raise_for_status()

                data = response.json()

                # Aggregate results by metric
                total = 0
                for result in data.get("data", []):
                    total += result.get("value", 0)

                return HttpStatus.OK, "", rate_limits, {
                    'metric': kafka_metric.value,
                    'total': total,
                    'period_start': query_start_time.isoformat(),
                    'period_end': query_end_time.isoformat()
                }
            except requests.exceptions.RequestException as e:
                return response.status_code, f"Metrics API Request failed for topic {topic_name} because {e}.  The error details are: {response.json() if response.content else {}}", rate_limits, None
        except Exception as e:
            return HttpStatus.BAD_REQUEST, f"Fail to query the Metrics API for topic {topic_name} because {e}.  The error details are: {response.json() if response.content else {}}", None, None

    def get_topic_daily_aggregated_totals(self, 
                                          kafka_metric: KafkaMetric, 
                                          kafka_cluster_id: str, 
                                          topic_name: str,
                                          timeout: int = DEFAULT_REQUEST_TIMEOUT_IN_SECONDS) -> Tuple[int, str, Dict | None, Dict | None]:
        """This function retrieves the Kafka Metric Daily Aggregated Totals for a given Kafka topic within a rolling window of the last 7 days.

        Args:
            kafka_metric (KafkaMetric): The Kafka metric to query (e.g., RECEIVED_BYTES, RECEIVED_RECORDS).
            kafka_cluster_id (str): The Kafka cluster ID.
            topic_name (str): The Kafka topic name.
            timeout (int, optional): The request timeout in seconds. Defaults to DEFAULT_REQUEST_TIMEOUT_IN_SECONDS.

        Returns:
            Tuple[int, str, Dict | None, Dict | None]: A tuple containing the HTTP status code, error
            message (if any), a dictionary with rate limit information, and a dictionary with aggregate
            the specified max daily total if successful; otherwise, None.
        """
        try:
            # Calculate the ISO 8601 formatted start and end times within a rolling window for the last 7 days
            utc_now = datetime.now(timezone.utc)
            seven_days_ago = utc_now - timedelta(days=7)
            iso_start_time = seven_days_ago.strftime('%Y-%m-%dT%H:%M:%SZ')
            iso_end_time = utc_now.strftime('%Y-%m-%dT%H:%M:%SZ')

            # Query for the daily Kafka Metric Total within a rolling window of the last 7 days
            query_data = {
                "aggregations": [
                    {
                        "metric": kafka_metric.value
                    }
                ],
                "filter": {
                    "op": "AND",
                    "filters": [
                        {
                            "field": "metric.topic", 
                            "op": "EQ", 
                            "value": topic_name
                        },
                        {
                            "field": "resource.kafka.id", 
                            "op": "EQ", 
                            "value": kafka_cluster_id
                        },
                    ],
                },
                "granularity": "P1D",
                "group_by": [
                    "metric.topic"
                ],
                "intervals": [
                    f"{iso_start_time}/{iso_end_time}"
                ]
            }

            response = requests.post(url=f"{self.metrics_base_url}/query",
                                     auth=HTTPBasicAuth(self.confluent_cloud_api_key, self.confluent_cloud_api_secret),
                                     json=query_data,
                                     timeout=timeout)
            
            # Extract rate limit information from response headers
            headers = dict(response.headers) if response.headers else None
            rate_limits = {}
            if headers and "ratelimit-remaining" in headers:
                rate_limits["remaining_count"] = int(headers["ratelimit-remaining"])
            if headers and "ratelimit-limit" in headers:
                rate_limits["limit_count"] = int(headers["ratelimit-limit"])
            if headers and "ratelimit-reset" in headers:
                rate_limits["reset_in_seconds"] = int(headers["ratelimit-reset"])

            try:
                # Raise HTTPError, if occurred.
                response.raise_for_status()

                data = response.json()

                # Collect the daily totals
                daily_totals = []
                for result in data.get("data", []):
                    daily_totals.append(result.get("value", 0))
                
                return HttpStatus.OK, "", rate_limits, {
                    'metric': kafka_metric.value,
                    'period_start': iso_start_time,
                    'period_end': iso_end_time,
                    'number_of_totals': len(daily_totals),
                    'daily_total': daily_totals,                    
                    'min_total': min(daily_totals) if daily_totals else 0,
                    'avg_total': sum(daily_totals) / len(daily_totals) if daily_totals else 0,
                    'max_total': max(daily_totals) if daily_totals else 0,
                    'sum_total': sum(daily_totals) if daily_totals else 0
                }
            except requests.exceptions.RequestException as e:
                return response.status_code, f"Metrics API Request failed for topic {topic_name} because {e}.  The error details are: {response.json() if response.content else {}}", rate_limits, None
        except Exception as e:
            return HttpStatus.BAD_REQUEST, f"Fail to query the Metrics API for topic {topic_name} because {e}.  The error details are: {response.json() if response.content else {}}", None, None

    def is_topic_partition_hot(self, 
                               kafka_cluster_id: str, 
                               topic_name: str, 
                               data_movement_type: DataMovementType, 
                               query_start_time: datetime, 
                               query_end_time: datetime, 
                               timeout: int = DEFAULT_REQUEST_TIMEOUT_IN_SECONDS) -> Tuple[int, str, bool | None, Dict | None]:
        """This function checks if a Kafka topic partition is considered "hot" based on the specified
        data movement type (INGRESS or EGRESS) within a given time range.

        Args:
            kafka_cluster_id (str): The Kafka cluster ID.
            topic_name (str): The Kafka topic name.
            data_movement_type (DataMovementType): The data movement type (INGRESS or EGRESS).
            query_start_time (datetime): The start time for the query.
            query_end_time (datetime): The end time for the query.
            timeout (int, optional): The request timeout in seconds. Defaults to DEFAULT_REQUEST_TIMEOUT_IN_SECONDS.
            
        Returns:
            Tuple[int, str, bool | None, Dict | None]: A tuple containing the HTTP status code, error
            message (if any), a dictionary with rate limit information, and a boolean indicating whether
            the partition is hot if successful; otherwise, None.
        """
        try:
            # Convert datetime to ISO format with milliseconds
            query_start_iso = query_start_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            query_end_iso = query_end_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

            # Query for Kafka Metric Total
            query_data = {
                "aggregations": [
                    {
                        "metric": KafkaMetric.HOT_PARTITION_INGRESS.value if data_movement_type == DataMovementType.INGRESS else KafkaMetric.HOT_PARTITION_EGRESS.value
                    }
                ],
                "filter": {
                    "op": "AND",
                    "filters": [
                        {
                            "field": "metric.topic", 
                            "op": "EQ", 
                            "value": topic_name
                        },
                        {
                            "field": "resource.kafka.id", 
                            "op": "EQ", 
                            "value": kafka_cluster_id
                        }
                    ],
                },
                "granularity": "PT1H",
                "group_by": [
                    "metric.topic"
                ],
                "intervals": [
                    f"{query_start_iso}/{query_end_iso}"
                ]
            }
            
            response = requests.post(url=f"{self.metrics_base_url}/query",
                                     auth=HTTPBasicAuth(self.confluent_cloud_api_key, self.confluent_cloud_api_secret),
                                     json=query_data,
                                     timeout=timeout)
            
            # Extract rate limit information from response headers
            headers = dict(response.headers) if response.headers else None
            rate_limits = {}
            if headers and "ratelimit-remaining" in headers:
                rate_limits["remaining_count"] = int(headers["ratelimit-remaining"])
            if headers and "ratelimit-limit" in headers:
                rate_limits["limit_count"] = int(headers["ratelimit-limit"])
            if headers and "ratelimit-reset" in headers:
                rate_limits["reset_in_seconds"] = int(headers["ratelimit-reset"])

            try:
                # Raise HTTPError, if occurred.
                response.raise_for_status()

                data = response.json()

                is_partition_hot = True if data.get("data") else False

                return HttpStatus.OK, "", rate_limits, {
                    'metric': KafkaMetric.HOT_PARTITION_INGRESS.value if data_movement_type == DataMovementType.INGRESS else KafkaMetric.HOT_PARTITION_EGRESS.value,
                    'is_partition_hot': is_partition_hot,
                    'period_start': query_start_time.isoformat(),
                    'period_end': query_end_time.isoformat()
                }
            except requests.exceptions.RequestException as e:
                return response.status_code, f"Metrics API Request failed for topic {topic_name} because {e}.  The error details are: {response.json() if response.content else {}}", rate_limits, None
        except Exception as e:
            return HttpStatus.BAD_REQUEST, f"Fail to query the Metrics API for topic {topic_name} because {e}.  The error details are: {response.json() if response.content else {}}", None, None
