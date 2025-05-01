# How to programmatically pause and resume a Flink statement
Welcome, streaming enthusiasts! Today, I’m excited to show you how to harness the [Flink RESTful API](https://docs.confluent.io/cloud/current/flink/operate-and-deploy/flink-rest-api.html) to programmatically pause and resume your Confluent Cloud for Apache Flink (CCAF) statements — giving you unprecedented control over your real-time data streaming pipelines. But before we dive into the step-by-step guide, I’ll walk you through the production challenge that inspired this solution and explain why fine-grained operational control like this can be a game-changer for reliability, performance, and cost management. Buckle up — it’s time to transform how you manage your Flink jobs!

## The Background
I was working on a customer and internal company projects that required me to pause and resume a Flink statement. Both projects shared a similar requirement: to pause the Flink statement when the input topic(s) had no new records for an extended period (say 30 minutes) and to resume the statement when new records arrived. This approach would help reduce costs when continuously running Flink statements sit idle. Before tackling this problem, I needed to understand how to programmatically pause and resume a Flink statement. So, I started looking into the [Flink RESTful API](https://docs.confluent.io/cloud/current/flink/operate-and-deploy/flink-rest-api.html) and found it relatively easy, with a gotcha or two. As I implement the initial solution to pause and resume a Flink statement, I will explain the gotchas.

> **Note:** I also plan to use this "pause and resume" functionality to conduct bulk updates to Flink statements: compute pool, and security principal.

## The Implementation
For some of you, you are familiar with my [`cc-clients-python_lib` library](https://github.com/j3-signalroom/cc-clients-python_lib), a collection of Python functions I use to interact with Confluent Cloud using their [RESTful APIs](https://docs.confluent.io/cloud/current/api.html). I began building the `stop-statement` method in the `FlinkClient()` class in the [`flink_client.py` module](https://github.com/j3-signalroom/cc-clients-python_lib/blob/main/src/cc_clients_python_lib/flink_client.py). My first thought was to submit a PATCH with a payload that would update some stop flag, and I would be done. So, this is what I found in the document as of this writing:

![flink-restful-api-patch-statement](images/flink-restful-api-patch-statement.png)

The link to the page is [here](https://docs.confluent.io/cloud/current/api.html#tag/Statements-(sqlv1)/operation/updateSqlv1Statement).

Alrighty then, I thought I was almost done.  I took the sample `curl` below, adjusted it to my needs, and ran it:

```bash
curl --request PATCH \
     --url 'https://flink.region.provider.confluent.cloud/sql/v1/organizations/{organization_id}/environments/{environment_id}/statements/{statement_name}' \
     --header 'Authorization: Basic REPLACE_BASIC_AUTH' \
     --header 'content-type: application/json-patch+json' \
     --data '{  "api_version": "sql/v1",
                "kind": "Statement",
                "metadata": {
                    "self": "https://flink.us-west1.aws.confluent.cloud/sql/v1/environments/env-123/statements/my-statement",
                    "created_at": "1996-03-19T01:02:03-04:05",
                    "updated_at": "2023-03-31T00:00:00-00:00",
                    "uid": "12345678-1234-1234-1234-123456789012",
                    "resource_version": "a23av",
                    "labels": {
                    "user.confluent.io/hidden": "true",
                    "property1": "string",
                    "property2": "string"
                    },
                    "resource_name": ""
                },
                "name": "sql123",
                "organization_id": "7c60d51f-b44e-4682-87d6-449835ea4de6",
                "environment_id": "string",
                "spec": {
                    "statement": "SELECT * FROM TABLE WHERE VALUE1 = VALUE2;",
                    "properties": {
                    "sql.current-catalog": "my_environment",
                    "sql.current-database": "my_kafka_cluster"
                    },
                    "compute_pool_id": "fcp-00000",
                    "principal": "sa-abc123",
                    "stopped": false
                },
                "status": {
                    "phase": "RUNNING",
                    "scaling_status": {
                    "scaling_state": "OK",
                    "last_updated": "1996-03-19T01:02:03-04:05"
                    },
                    "detail": "Statement is running successfully",
                    "traits": {
                    "sql_kind": "SELECT",
                    "is_bounded": true,
                    "is_append_only": true,
                    "upsert_columns": [
                        0
                    ],
                    "schema": {
                        "columns": [
                        {
                            "name": "Column_Name",
                            "type": {
                            "type": "CHAR",
                            "nullable": true,
                            "length": 8
                            }
                        }
                        ]
                    }
                    },
                    "network_kind": "PUBLIC",
                    "latest_offsets": {
                    "topic-1": "partition:0,offset:100;partition:1,offset:200",
                    "topic-2": "partition:0,offset:50"
                    },
                    "latest_offsets_timestamp": "2023-03-31T00:00:00-00:00"
                },
                "result": {
                    "api_version": "sql/v1",
                    "kind": "StatementResult",
                    "metadata": {
                    "self": "https://flink.us-west1.aws.confluent.cloud/sql/v1/environments/env-123/statements",
                    "next": "https://flink.us-west1.aws.confluent.cloud/sql/v1/environments/env-abc123/statements?page_token=UvmDWOB1iwfAIBPj6EYb",
                    "created_at": "2006-01-02T15:04:05-07:00"
                    },
                    "results": {
                    "data": [
                        {
                        "op": 0,
                        "row": [
                            "101",
                            "Jay",
                            [
                            null,
                            "abc"
                            ],
                            [
                            null,
                            "456"
                            ],
                            "1990-01-12 12:00.12",
                            [
                            [
                                null,
                                "Alice"
                            ],
                            [
                                "42",
                                "Bob"
                            ]
                            ]
                        ]
                        }
                    ]
                    }
                }
            }'
```

But I ran into my first gotcha, this was the error response I got:
```bash
{ 
  "errors": [
     { 
        "id": "<JWT token redacted>", 
        "status": "403", 
        "detail": "Patch feature is currently disabled", 
        "source": {} 
      } 
  ]
}
```

![that70s-show-kitty](images/that70s-show-kitty.gif)


So, it must be me; I must have done something wrong, right? Because the document clearly states that the `PATCH` method is supported, I wasted about an hour trying everything to no avail! I finally gave up and submitted a support ticket to Confluent. Then, of course, as luck would have it, Confluent automatically replied with an article that solved their known issue.

![facepalm-really](images/facepalm-really.gif)

Here is the article:

**What can cause "Patch feature is currently disabled" Error when updating Flink Statement Sets via API**

**_(last updated December 16, 2024)_**

**Description**

Users attempting to update a Flink statement set using the `PATCH` method via the FlinkAPI will encounter an error indicating that the method is unsupported.

```json
{ 
  "errors": [
     { 
        "id": "<JWT token redacted>", 
        "status": "403", 
        "detail": "Patch feature is currently disabled", 
        "source": {} 
      } 
  ]
}
```

**Cause**

The FlinkAPI does not support the `PATCH` method for updating Flink statement sets.

**Resolution**

To update a Flink statement set, use a `PUT` request instead of `PATCH`. The `PUT` request body must include the `resource_version`. This value changes each time the statement is updated. Therefore, you must first retrieve the current statement set using a `GET` request to obtain the latest `resource_version`. Include this value in your `PUT` request body. Be prepared to retry the `PUT` request if a `409` conflict error is returned, which indicates that the `resource_version` has changed since you last retrieved it. You may need to implement a _retry mechanism with optimistic locking_ to handle concurrent updates.

## The Solution

![denzel-washington-my-heart](images/denzel-washington-my-heart.gif)

So, I took the advice from the article and implemented a _retry mechanism with optimistic locking_. (By the way, the need to implement a _retry mechanism with optimistic_ locking was the second gotcha.) Here is the code for the `stop_statement()` method in the `FlinkClient` class:

```python
    def stop_statement(self, statement_name: str, stop: bool = True) -> Tuple[int, str]:
        """This function submits a RESTful API call to stop or start the Flink SQL statement.

        For more information, why this function is a bit complex, please refer to the
        Issue [#166](https://github.com/j3-signalroom/cc-clients-python_lib/issues/166).

        Note: "Confluent Cloud for Apache Flink enforces a 30-day retention for statements in
        terminal states." 
        
        Arg(s):
            statement_name (str):  The Flink SQL statement name.
            stop (bool):           (Optional) The stop flag. Default is True.

        Returns:
            int:    HTTP Status Code.
            str:    HTTP Error, if applicable.
        """
        return self.__update_statement(statement_name=statement_name, stop=stop)
    
    def __update_statement(self, statement_name: str, stop: bool, new_compute_pool_id: str = None, new_security_principal_id: str = None) -> Tuple[int, str]:
        """This private function submits a RESTful API call to update the mutable attributes of a 
        Flink SQL statement.

        Arg(s):
            statement_name (str):             The current Flink SQL statement name.
            stop (bool):                      The stop flag.
            new_compute_pool_id (str):        (Optional) The new compute pool ID.
            new_security_principal_id (str):  (Optional) The new security principal ID.

        Returns:
            int:    HTTP Status Code.
            str:    HTTP Error, if applicable.
        """
        retry = 0
        max_retries = 9
        retry_delay_in_seconds = 5

        while retry < max_retries:
            # Send a GET request to get the statement.
            response = requests.get(url=f"{self.flink_sql_base_url}statements/{statement_name}",
                                    auth=HTTPBasicAuth(self.flink_api_key, self.flink_api_secret))

            try:
                # Raise HTTPError, if occurred.
                response.raise_for_status()

                # Turn the JSON response into a Statement model.
                statement = Statement(**response.json())

                # Get the statement resource version.
                resource_version = statement.metadata.resource_version

                # Set the stop flag, compute pool ID, and security principal ID.
                statement.spec.stopped = stop
                if new_compute_pool_id is not None:
                    statement.spec.compute_pool_id = new_compute_pool_id
                if new_security_principal_id is not None:
                    statement.spec.principal = new_security_principal_id

                # Send a PUT request to update the status of the statement.
                response = requests.put(url=f"{self.flink_sql_base_url}statements/{statement_name}",
                                        data=statement.model_dump_json(),
                                        auth=HTTPBasicAuth(self.flink_api_key, self.flink_api_secret))
                
                try:
                    # Raise HTTPError, if occurred.
                    response.raise_for_status()

                    # Turn the JSON response into a Statement model.
                    statement = Statement(**response.json())

                    # Check if the resource version is the same.  If it is the same, the statement has successfully
                    # been updated.  If it is not the same, this indicates that the statement has been updated since
                    # the last GET request.  In this case, we need to retry the request.
                    if statement.metadata.resource_version == resource_version:
                        return response.status_code, response.text
                    else:
                        retry += 1
                        if retry == max_retries:
                            return response.status_code, f"Max retries exceeded.  Fail to update the statement because of a resource version mismatch.  Expected resource version #{resource_version}, but got resource version #{statement.metadata.resource_version}."
                        else:
                            time.sleep(retry_delay_in_seconds)
                except requests.exceptions.RequestException as e:
                    retry += 1
                    if retry == max_retries:
                        return response.status_code, f"Max retries exceeded.  Fail to update the statement because {e}, and the response is {response.text}"
                    else:
                        time.sleep(retry_delay_in_seconds)
            except requests.exceptions.RequestException as e:
                retry += 1
                if retry == max_retries:
                    return response.status_code, f"Max retries exceeded.  Fail to retrieve the statement because {e}, and the response is {response.text}"
                else:
                    time.sleep(retry_delay_in_seconds)
```

> **Note:** The `Statement` model is a Pydantic model I generated from the [Confluent OpenAPI specification](https://docs.confluent.io/cloud/current/api.html#:~:text=OpenAPI%20specification%3A-,Download,-Introduction) to represent the Flink SQL statement.  The code for the model is in the [`src/cc_clients_python_lib/cc_openapi_v2_1/__init__.py`](https://github.com/j3-signalroom/cc-clients-python_lib/blob/main/src/cc_clients_python_lib/cc_openapi_v2_1/__init__.py).


## The Test
To test the `stop_statement()` method, I created a test case in the [`tests/test_flink_client.py` module](https://github.com/j3-signalroom/cc-clients-python_lib/blob/main/tests/test_flink_client.py) using the `pytest` framework.  Here is the code for the test case:

```python
def test_stop_statement():
    """Test the stop_statement() function."""

    # Instantiate the FlinkClient class.
    flink_client = FlinkClient(config)

    http_status_code, response = flink_client.stop_statement(statement_name, True)
 
    try:
        assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"
    except AssertionError as e:
        logger.error(e)
        logger.error("Response: %s", response)
```

> **Note:**  The `config` variable is a dictionary containing the `FlinkClient` class's configuration. The `statement_name` variable is the name of the Flink SQL statement that you want to stop or start. All these variables are defined in the `.env` file. (Refer to the [tests/test_flink_client.py/load_configurations](https://github.com/j3-signalroom/cc-clients-python_lib/blob/main/tests/test_flink_client.py) function for the environment variables required to run the test.)

## In Action

### Testing the stopping of a Flink SQL Statement
To test the stopping of a currently running Flink SQL statement, which you can see in the picture below, taken from the CCAF Flink statements tab UI:

![flink-statement-started](images/flink-statement-started.png)

Execute the following command in the terminal:

```bash
pytest -s tests/test_flink_client.py::test_stop_statement
```

From the UI, the Flink SQL statement will go into a `Pending` state, as shown below:

![flink-statement-started](images/flink-statement-pending.png)

Then, after a few seconds, the Flink SQL statement will go into a `Stopped` state, as shown below:

![flink-statement-stopped](images/flink-statement-stopped.png)

### Testing the starting of a Flink SQL Statement
To test starting a currently stopped Flink SQL statement, first modify the unit test by passing `False` instead of `True` as an argument in the `stop_statement` method:
```python
def test_stop_statement():
    """Test the stop_statement() function."""

    # Instantiate the FlinkClient class.
    flink_client = FlinkClient(config)

    http_status_code, response = flink_client.stop_statement(statement_name, False)
 
    try:
        assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"
    except AssertionError as e:
        logger.error(e)
        logger.error("Response: %s", response)
```

> **Note:**  The `config` variable is a dictionary containing the `FlinkClient` class's configuration. The `statement_name` variable is the name of the Flink SQL statement that you want to stop or start. All these variables are defined in the `.env` file. (Refer to the [tests/test_flink_client.py/load_configurations](https://github.com/j3-signalroom/cc-clients-python_lib/blob/main/tests/test_flink_client.py) function for the environment variables required to run the test.)

To test starting a currently stopped Flink SQL statement, which you can see in the picture below, taken from the CCAF Flink statements tab UI:

![flink-statement-stopped](images/flink-statement-stopped.png)

Execute the following command in the terminal:
```bash
pytest -s tests/test_flink_client.py::test_stop_statement
```
From the UI, the Flink SQL statement will go into a `Pending` state, as shown below:
![flink-statement-pending](images/flink-statement-pending.png)

Then, after a few seconds, the Flink SQL statement will go into a `Running` state, as shown below:
![flink-statement-started](images/flink-statement-started.png)

## Conclusion
In this blog post, I demonstrated how to programmatically pause and resume a Flink SQL statement using the Flink RESTful API. I also discussed the challenges I faced along the way and how I overcame them.

> _**Note:** Confluent Cloud for Apache Flink enforces a 30-day retention for statements in terminal states._

I hope you found this blog post helpful and that it will help you in your projects.
