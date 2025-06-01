import os

from jsonpath_ng import parse
import curlify
from jsonschema import validate, ValidationError
from src.utils import logger
log = logger.customLogger()


def get_response_code(response):
    """
    Method to get response code
    :param response:
    :return:
    """
    try:
        status_code_value = response.status_code
        log.info(f'API executed successfully and the response code: {status_code_value}')
        return status_code_value
    except Exception as e:
        log.info('The error is ', e)

def get_response_data(response):
    """
    Method to get response testData
    :param response:
    :return:
    """
    try:
        response_data = response.json()

        return response_data
    except Exception as e:
        try:
            response_data = response.text
            log.info(f'API executed successfully and the response testData is {response_data}')
            return response_data
        except Exception as inner_exception:
            log.error(f'Error while getting response testData: {inner_exception}')
            return None

def get_value_from_response(response, jsonpath_expression):
    """
    Method to get the value from JSON response by passing valid JSON path expression.
    :param jsonpath_expression:
    :param response:
    :return:
    """
    try:
        api_response = get_response_data(response)
        if not api_response:
            raise ValueError("Response testData is empty or invalid")

        parsed_expression = parse(f'$.{jsonpath_expression}')
        match = parsed_expression.find(api_response)

        if not match:
            raise IndexError(f"No value found for the JSONPath expression: {jsonpath_expression}")

        value = match[0].value
        log.info(f'API executed successfully and the response value in {jsonpath_expression} is {value}')
        return value
    except IndexError as e:
        log.error(f"JSONPath expression did not return any results: {e}")
        return None
    except Exception as e:
        log.error(f'Error while getting value from response: {e}')
        return None

def validate_response_code(response, expected_response_code):
    """
    Method to validate the response code
    :param expected_response_code:
    :param response:
    :return:
    """
    # actual_status_code = get_response_code(response)
    # assert actual_status_code == expected_response_code
    # log.info(f'Expected response code: {expected_response_code} is matches the actual code: {actual_status_code}')
    actual_status_code = get_response_code(response)
    assert actual_status_code == expected_response_code, (
        f"Expected response code {expected_response_code} but got {actual_status_code}"
    )
    log.info(f'Expected response code {expected_response_code} matches the actual code {actual_status_code}')

def validate_entire_response_body_data(response, expected_response_data):
    """
    Method to validate response entire body
    :param expected_response_data:
    :param response:
    :return:
    """
    actual_response_data = get_response_data(response)
    assert actual_response_data == expected_response_data
    log.info(f'{expected_response_data} is same as  {response}')

def validate_in_response_body(response, jsonpath_expression, expected_value, message_on_failure):
    """
    Method to validate testData in the response body
    :param jsonpath_expression:
    :param message_on_failure:
    :param expected_value:
    :param response:
    :return:
    """

    data_value = get_value_from_response(response, jsonpath_expression)

    if isinstance(expected_value, (int, float)) or isinstance(data_value, (int, float)):
        data_verified = expected_value == data_value
    else:
        data_verified = expected_value in data_value

    log.info(f'{expected_value} is present in the response')
    assert data_verified, message_on_failure

def validate_schema(response, schema):
    """
    Validates the response against the provided schema.

    :param response: JSON response from the API
    :param schema: JSON schema to validate against
    :return: None
    """
    schema_validation_enabled = os.getenv("SCHEMA_VALIDATION", "true").lower() == "true"
    print(schema_validation_enabled)
    if not schema_validation_enabled:
        log.info("Skipping schema validation as per configuration.")
        return

    try:
        response1 = get_response_data(response)
        validate(instance=response1, schema=schema)
        log.info("Schema validation passed.")
    except ValidationError as e:
        log.warning(f"Schema validation failed: {e.message}")
        log.error("Test failed due to schema validation error.")
        raise  # Re-raise the exception to fail the test case

def validate_response_content_type(response, expected_content_type='application/json'):
    convert_response_to_curl(response)
    """
    Validates the Content-Type header of the API response using Python's built-in assertions.

    Args:
        response (requests.Response): The response object returned by an API call.
        expected_content_type (str): The expected Content-Type header value. Default is 'application/json'.
    """
    log.info("Starting validation for Content-Type header in the API response.")

    try:
        # Retrieve Content-Type from response headers
        content_type = response.headers.get('Content-Type', None)

        # Check if Content-Type is missing in the response headers
        assert content_type is not None, "Content-Type header is missing"
        log.info(f"Content-Type header is present: '{content_type}'")

        # Validate Content-Type starts with the expected value
        assert content_type.startswith(expected_content_type), (
            f"Expected Content-Type '{expected_content_type}', but got '{content_type}'"
        )
        log.info(f"Validation successful: Content-Type is '{content_type}' as expected.")

    except AssertionError as e:
        log.error(f"Validation failed: {str(e)}")
        raise
    except Exception as e:
        log.error(f"An unexpected error occurred during Content-Type validation: {str(e)}")
        raise

def convert_response_to_curl(response):
    """
    Converts a requests response object to a cURL command.

    :param response: requests response object
    """
    try:
        curl_command = curlify.to_curl(response.request)
        log.info("Generated cURL command:\n%s", curl_command)
    except Exception as e:
        log.error("Failed to generate cURL command: %s", str(e))