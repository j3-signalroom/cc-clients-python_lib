# How to programmatically pause and resume a Flink statement REDUX
Hi Everyone! I wanted to update my previous blog post, "[How to programmatically pause and resume a Flink statement](https://thej3.com/how-to-programmatically-pause-and-resume-a-flink-statement-9577fb171972)," to let you know that Confluent on [May 6th, 2025](https://docs.confluent.io/cloud/current/release-notes/index.html#may-6th-2025), released an update to its CCAF (Confluent Cloud for Apache Flink) RESTful API. It now supports the [`PATCH` method](https://docs.confluent.io/cloud/current/api.html#tag/Statements-(sqlv1)/operation/patchSqlv1Statement)!  Yay!!!  😀  The `PATCH` method is much simpler to use and does not require implementing a retry mechanism with optimistic locking. This is a great improvement for developers who want to programmatically pause and resume a Flink SQL statement. The `PATCH method` is now the preferred way to update the mutable attributes of a Flink SQL statement.  The [`PUT` method](https://docs.confluent.io/cloud/current/api.html#tag/Statements-(sqlv1)/operation/updateSqlv1Statement) is still available, but it is no longer necessary to use it in conjunction with the [`GET` method](https://docs.confluent.io/cloud/current/api.html#tag/Statements-(sqlv1)/operation/getSqlv1Statement).

## The Reimplementation
The code is now significantly simpler. Rather than implementing the pausing and resuming of a Flink statement in my [`cc-clients-python_lib` library](https://github.com/j3-signalroom/cc-clients-python_lib) like this:

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

Now, with the new `PATCH` method, I can easily implement the `stop_statement()` method like this:

```python
    def stop_statement(self, statement_name: str, stop: bool = True) -> Tuple[int, str]:
        """This function submits a RESTful API call to stop or start the Flink SQL statement.

        Note: "Confluent Cloud for Apache Flink enforces a 30-day retention for statements in
        terminal states." 

        Arg(s):
            statement_name (str):  The Flink SQL statement name.
            stop (bool):           (Optional) The stop flag. Default is True.

        Returns:
            int:    HTTP Status Code.
            str:    HTTP Error, if applicable.
        """
        patch_request = []
        patch_request.append(json.loads(
            JsonPatchRequestAddReplace(
                path="/spec/stopped", 
                value=stop, 
                op=Op.replace).model_dump_json()))

        # Send a PATCH request to update the status of the statement.
        response = requests.patch(url=f"{self.flink_sql_base_url}statements/{statement_name}",
                                  data=json.dumps(patch_request),
                                  auth=HTTPBasicAuth(self.flink_api_key, self.flink_api_secret))
        
        try:
            # Raise HTTPError, if occurred.
            response.raise_for_status()
            return response.status_code, response.text
        except Exception as e:
            return response.status_code, f"Failed to {"stop" if stop else "resume"} the statement because {e}, and the response is {response.text}"
```
> **Note:** The `JsonPatchRequestAddReplace` model is a Pydantic model I generated from the [Confluent OpenAPI specification](https://docs.confluent.io/cloud/current/api.html#:~:text=OpenAPI%20specification%3A-,Download,-Introduction) to represent the Flink SQL statement.  The code for the model is in the [`src/cc_clients_python_lib/cc_openapi_v2_1/__init__.py`](https://github.com/j3-signalroom/cc-clients-python_lib/blob/main/src/cc_clients_python_lib/cc_openapi_v2_1/__init__.py).


## The Retest
To test the `stop_statement()` method, I created a test case in the [`tests/test_flink_client.py` module](https://github.com/j3-signalroom/cc-clients-python_lib/blob/main/tests/test_flink_client.py) using the `pytest` framework.  Here is the code for the test case:

To test the `stop_statement()` method, I used the same unit test that I created in the [`tests/test_flink_client.py` module](https://github.com/j3-signalroom/cc-clients-python_lib/blob/main/tests/test_flink_client.py) with the [`pytest` framework](https://docs.pytest.org/en/stable/). Here is the code:

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

> **Note:**  The `config` variable is a dictionary containing the `FlinkClient` class’s configuration. The `statement_name` variable represents the name of the Flink SQL statement that you wish to stop or start. All these variables are defined in the `.env` file. (Refer to the [tests/test_flink_client.py/load_configurations](https://github.com/j3-signalroom/cc-clients-python_lib/blob/main/tests/test_flink_client.py) function for the environment variables required to run the test.)


## Conclusion
Thanks to the new `PATCH` method, I simplified the code for pausing and resuming a Flink SQL statement. The new method is much easier to use and does not require implementing a retry mechanism with optimistic locking. This is a great improvement for developers who want to programmatically pause and resume a Flink SQL statement. Thank you, Confluent!

I hope you found this blog post helpful and that it will assist you in your projects.
