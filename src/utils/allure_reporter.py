"""
Allure Reporter Module.

This module provides utility functions for Allure reporting.
"""
import allure
import os
import json
from datetime import datetime
from src.utils import logger

log = logger.customLogger()


def allure_step(step_name):
    """
    Decorator for Allure step.

    Args:
        step_name (str): Step name

    Returns:
        function: Decorated function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with allure.step(step_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def add_allure_step(step_name, status="passed"):
    """
    Add step to Allure report.

    Args:
        step_name (str): Step name
        status (str, optional): Step status. Defaults to "passed".
    """
    with allure.step(step_name):
        if status.lower() == "failed":
            allure.attach(
                body=f"Step failed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                name="Failure Details",
                attachment_type=allure.attachment_type.TEXT
            )


def attach_screenshot(screenshot_path, name="Screenshot"):
    """
    Attach screenshot to Allure report.

    Args:
        screenshot_path (str): Screenshot file path
        name (str, optional): Attachment name. Defaults to "Screenshot".
    """
    try:
        if os.path.exists(screenshot_path):
            with open(screenshot_path, "rb") as file:
                allure.attach(
                    file.read(),
                    name=name,
                    attachment_type=allure.attachment_type.PNG
                )
            log.info(f"Attached screenshot to Allure report: {screenshot_path}")
        else:
            log.error(f"Screenshot not found: {screenshot_path}")
    except Exception as e:
        log.error(f"Failed to attach screenshot to Allure report: {str(e)}")


def attach_request_data(method, url, headers=None, params=None, payload=None):
    """
    Attach API request data to Allure report.

    Args:
        method (str): HTTP method
        url (str): Request URL
        headers (dict, optional): Request headers. Defaults to None.
        params (dict, optional): Request parameters. Defaults to None.
        payload (dict, optional): Request payload. Defaults to None.
    """
    request_data = {
        "method": method,
        "url": url,
        "headers": headers,
        "params": params,
        "payload": payload
    }

    allure.attach(
        json.dumps(request_data, indent=4, default=str),
        name="Request Data",
        attachment_type=allure.attachment_type.JSON
    )
    log.info("Attached request data to Allure report")


def attach_response_data(response):
    """
    Attach API response data to Allure report.

    Args:
        response: Response object
    """
    try:
        response_data = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.json() if response.headers.get('Content-Type', '').startswith('application/json') else response.text
        }

        allure.attach(
            json.dumps(response_data, indent=4, default=str),
            name="Response Data",
            attachment_type=allure.attachment_type.JSON
        )
        log.info("Attached response data to Allure report")
    except Exception as e:
        log.error(f"Failed to attach response data to Allure report: {str(e)}")
        allure.attach(
            response.text,
            name="Response Text",
            attachment_type=allure.attachment_type.TEXT
        )


def attach_test_data(test_data):
    """
    Attach test data to Allure report.

    Args:
        test_data (dict): Test data
    """
    allure.attach(
        json.dumps(test_data, indent=4, default=str),
        name="Test Data",
        attachment_type=allure.attachment_type.JSON
    )
    log.info("Attached test data to Allure report")
