from datetime import datetime
from typing import Dict, Tuple
import requests
from requests.auth import HTTPBasicAuth

from cc_clients_python_lib.http_status import HttpStatus


__copyright__  = "Copyright (c) 2025 Jeffrey Jonathan Jennings"
__license__    = "MIT"
__credits__    = ["Jeffrey Jonathan Jennings (J3)"]
__maintainer__ = "Jeffrey Jonathan Jennings (J3)"
__email__      = "j3@thej3.com"
__status__     = "dev"

# Metrics Config Keys.
METRICS_CONFIG = {
    "cloud_api_key": "cloud_api_key",
    "cloud_api_secret": "cloud_api_secret"
}

class MetricsClient():
    def __init__(self, metrics_config: Dict):
        self.cloud_api_key = metrics_config[METRICS_CONFIG["cloud_api_key"]]
        self.cloud_api_secret = metrics_config[METRICS_CONFIG["cloud_api_secret"]]
        self.metrics_base_url = "https://api.telemetry.confluent.cloud/v2/metrics/cloud"

    def get_topic_bytes(self, kafka_cluster_id: str, topic_name: str, start_time: datetime, end_time: datetime) -> Tuple[int, str, Dict | None]:
        """Get actual bytes from Confluent Cloud Metrics API.
        
        Args:
            kafka_cluster_id (str): The Kafka cluster ID.
            topic_name (str): The Kafka topic name.
            start_time (datetime): The start time for the query.
            end_time (datetime): The end time for the query.
            
        Returns:
            Tuple[int, str, Dict | None]: A tuple containing the HTTP status code, error
            message (if any), and a dictionary with total bytes, total records, average bytes per record,
            period start and end times, and source if successful; otherwise, None.
        """
        try:
            # Convert datetime to ISO format with milliseconds
            start_iso = start_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            end_iso = end_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            
            # Query for received bytes
            query_data = {
                "aggregations": [
                    {
                        "agg": "SUM"
                    }
                ],
                "filter": {
                    "op": "AND",
                    "filters": [
                        {
                            "field": "metric.label.topic",
                            "op": "EQ", 
                            "value": topic_name
                        },
                        {
                            "field": "resource.kafka.id",
                            "op": "EQ",
                            "value": kafka_cluster_id
                        }
                    ]
                },
                "granularity": "PT1H",  # 1 hour granularity
                "group_by": [
                    "metric.label.topic"
                ],
                "intervals": [f"{start_iso}/{end_iso}"],
                "limit": 1000,
                "metric": "io.confluent.kafka.server/received_bytes"
            }
            
            response = requests.post(url=f"{self.metrics_base_url}/query",
                                     auth=HTTPBasicAuth(self.cloud_api_key, self.cloud_api_secret),
                                     json=query_data,
                                     timeout=30)
            
            try:
                # Raise HTTPError, if occurred.
                response.raise_for_status()

                data = response.json()
                total_bytes = 0
                record_count = 0
                
                for result in data.get('data', []):
                    total_bytes += result.get('value', 0)
                    record_count += 1
                
                # Also get record count for the period
                record_query = {**query_data, "metric": "io.confluent.kafka.server/received_records"}
                record_response = requests.post(url=f"{self.metrics_base_url}/query",
                                                auth=HTTPBasicAuth(self.cloud_api_key, self.cloud_api_secret),
                                                json=record_query,
                                                timeout=30)
                
                total_records = 0
                try:
                    # Raise HTTPError, if occurred.
                    record_response.raise_for_status()

                    record_data = record_response.json()
                    for result in record_data.get('data', []):
                        total_records += result.get('value', 0)
                except:  # noqa: E722
                    pass
                
                return HttpStatus.OK, "", {
                    'total_bytes': total_bytes,
                    'total_records': total_records,
                    'avg_bytes_per_record': total_bytes / total_records if total_records > 0 else 0,
                    'period_start': start_time,
                    'period_end': end_time,
                    'source': 'metrics_api'
                }
            except requests.exceptions.RequestException as e:
                return response.status_code, f"Metrics API Request failed for topic {topic_name} because {e}", None
        except Exception as e:
            return HttpStatus.BAD_REQUEST, f"Fail to query the Metrics API for topic {topic_name} because {e}", None
