"""
Sample API Test Module.

This module contains tests for the User API endpoints.
Tests are parameterized using test testData from JSON files.
"""
import pytest
import os

from src.utils.shared_API_Data import shared_data
from src.utils.api_utilities import validate_response_code, validate_schema, validate_response_content_type, \
    validate_in_response_body, get_value_from_response
from src.utils.file_reader import read_file

from src.utils import logger
log = logger.customLogger()

testcasedata = read_file("TodoListData", 'Delete_todo.json')


@pytest.mark.Positive
@pytest.mark.parametrize("case", testcasedata["Positive"])
def test_Delete_todo_Positive(api_request_context, case):

    log.info(f"Running test case: {case['description']}")

    baseURL = os.getenv('TO_DOS')
    todos=shared_data.get_data("todos_id")
    case["path_params"]["id"] = todos

    # Make API request
    response = api_request_context.make_request(
        base_url=baseURL,
        method=case["method"],
        api_endpoint=case["endpoint"],
        path_params=case["path_params"],
        header=case["headers"]
    )


    # Validate response
    validate_response_code(response, case["expected_status"])
    # Validate content type
    validate_response_content_type(response)

    # Validate schema if provided
    if "expected_schema" in case and case["expected_schema"]:
        validate_schema(response=response, schema=case["expected_schema"])





@pytest.mark.Negative
@pytest.mark.parametrize("case", testcasedata["Negative"])
def test_Delete_todo_Negative(api_request_context, case):
    log.info(f"Running test case: {case['description']}")

    baseURL = os.getenv('TO_DOS')


    # Make API request
    response = api_request_context.make_request(
        base_url=baseURL,
        method=case["method"],
        api_endpoint=case["endpoint"],
        header=case["headers"]
    )

    # Validate response
    validate_response_code(response, case["expected_status"])

    # Validate content type
    validate_response_content_type(response)
