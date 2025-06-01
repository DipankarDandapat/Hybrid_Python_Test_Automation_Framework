"""
Sample API Test Module.

This module contains tests for the User API endpoints.
Tests are parameterized using test testData from JSON files.
"""
import allure
import pytest
import os

from src.utils.shared_API_Data import shared_data
from src.utils.api_utilities import validate_response_code, validate_schema, validate_response_content_type, \
    validate_in_response_body, get_value_from_response
from src.utils.file_reader import read_file

from src.utils.allure_reporter import (
    allure_step,
    add_allure_step,
    attach_request_data,
    attach_response_data,
    attach_test_data
)


from src.utils import logger
log = logger.customLogger()

testcasedata = read_file("TodoListData", 'Create_todos.json')

@allure.epic("API Testing")
@allure.feature("Todo_List")
@pytest.mark.Positive
@pytest.mark.parametrize("case", testcasedata["Positive"])
def test_Create_Todo_Positive(api_request_context, case):
    # Allure test metadata
    allure.dynamic.story("Positive User API Tests")
    allure.dynamic.title(f"Test User API: {case['endpoint']} - {case['method']}")
    allure.dynamic.description(f"Testing {case['method']} request to {case['endpoint']} with expected status {case.get('expected_status', 200)}")
    allure.dynamic.severity(allure.severity_level.NORMAL)
    # Attach test data to report
    attach_test_data(case)
    # Setup test
    add_allure_step("Setting up test environment")

    log.info(f"Running test case: {case['description']}")

    baseURL = os.getenv('TO_DOS')

    with allure.step(f"Making {case['method']} request to {baseURL}{case['endpoint']}"):
        # Attach request data
        attach_request_data(
            method=case["method"],
            url=f"{baseURL}{case['endpoint']}",
            headers=case["headers"],
            payload=case["payload"]
        )

        # Make API request
        response = api_request_context.make_request(
            base_url=baseURL,
            method=case["method"],
            api_endpoint=case["endpoint"],
            header=case["headers"],
            payload=case["payload"]
        )

        # Attach response data
        attach_response_data(response)

     # Validate response
    with allure.step("Validating response status code"):
        status_valid=validate_response_code(response, case["expected_status"])
    # Validate content type
    with allure.step("Validating response content type"):

        validate_response_content_type(response)

    with allure.step("Validating response body content "):
        validate_in_response_body(response, 'data.title', case["payload"]["title"], 'title not matches')
        validate_in_response_body(response, 'data.description', case["payload"]["description"], 'description not matches')


    shared_data.set_data("todos_id", get_value_from_response(response, 'data._id'))


    # Validate schema if provided
    with allure.step("Validating response schema"):
        if "expected_schema" in case and case["expected_schema"]:
            validate_schema(response=response, schema=case["expected_schema"])




@pytest.mark.Semantic
@pytest.mark.parametrize("case", testcasedata["Semantic"])
def test_Create_Todo_Semantic(api_request_context, case):
    log.info(f"Running test case: {case['description']}")

    baseURL = os.getenv('TO_DOS')

    # Make API request
    response = api_request_context.make_request(
        base_url=baseURL,
        method=case["method"],
        api_endpoint=case["endpoint"],
        header=case["headers"],
        payload=case["payload"]
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
def test_Create_Todo_Negative(api_request_context, case):
    log.info(f"Running test case: {case['description']}")

    baseURL = os.getenv('TO_DOS')


    # Make API request
    response = api_request_context.make_request(
        base_url=baseURL,
        method=case["method"],
        api_endpoint=case["endpoint"],
        header=case["headers"],
        payload=case["payload"]
    )

    # Validate response
    validate_response_code(response, case["expected_status"])

    # Validate content type
    validate_response_content_type(response)
