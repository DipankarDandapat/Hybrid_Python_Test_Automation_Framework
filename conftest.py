"""
Conftest module for tests.

This module provides pytest fixtures and command line options for all test types.
"""
import os
import pathlib
from collections import defaultdict
import time
from datetime import datetime
from typing import Dict, Optional
import requests
import pytest
from py.xml import html
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from config.environment import Environment
from src.base.unified_driver import UnifiedDriverManager

from src.utils import logger
log = logger.customLogger()

def pytest_addoption(parser):
    """Add command line options for test configuration."""
    # Environment and test type options
    parser.addoption("--environment", action="store", default="staging",
                     help="Environment to run tests against (staging, prod, dev)")
    parser.addoption("--test-type", action="store", default="ui",
                     choices=["ui", "mobile", "api", "all"],
                     help="Type of test to run: ui, mobile, api, or all")

    # Execution mode options (applies to both UI and Mobile)
    parser.addoption("--execution-mode", action="store", default="local",
                     choices=["local", "cloud"],
                     help="Execution mode: local (default) or cloud")
    parser.addoption("--cloud-provider", action="store", default="browserstack",
                     choices=["browserstack", "saucelabs"],
                     help="Cloud provider for remote execution (required when execution-mode=cloud)")

    # UI testing specific options
    parser.addoption("--browser", action="store", default="chrome",
                     choices=["chrome", "firefox", "edge"],
                     help="Browser to use for UI tests")
    parser.addoption("--headless", action="store_true", default=False,
                     help="Run browser in headless mode")

    # Mobile testing specific options
    parser.addoption("--platform", action="store", default="android",
                     choices=["android", "ios"],
                     help="Mobile platform to use")
    parser.addoption("--app", action="store", default=None,
                     help="Path to mobile app or app ID for cloud execution")


@pytest.fixture(scope="function")
def api_session():
    """Create and configure API session with retry mechanism per test function."""
    log.info("🌐 Creating API session")
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=5,
        status_forcelist=[502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE", "PATCH"],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    yield session
    session.close()
    log.info("🌐 API session closed")


@pytest.fixture(scope="session", autouse=True)
def setup_environment(request):
    """Setup environment configuration from command line options and env files."""
    env_name = request.config.getoption("--environment")
    test_type = request.config.getoption("--test-type")
    execution_mode = request.config.getoption("--execution-mode")
    cloud_provider = request.config.getoption("--cloud-provider")

    log.info(f"Setting up environment: {env_name}, test_type: {test_type}, execution_mode: {execution_mode}")

    # Load environment using Environment class (if it exists)
    try:
        Environment(env_name)
    except Exception as e:
        log.warning(f"Could not load Environment class: {e}")

    # Set core environment variables
    os.environ["ENVIRONMENT"] = env_name
    os.environ["TEST_TYPE"] = test_type
    os.environ["EXECUTION_MODE"] = execution_mode

    # Validate cloud provider is specified when using cloud execution
    if execution_mode == "cloud":
        if not cloud_provider:
            raise ValueError("--cloud-provider must be specified when using --execution-mode=cloud")
        os.environ["CLOUD_PROVIDER"] = cloud_provider
        # Set remote flag for backward compatibility
        os.environ["REMOTE"] = "True"
        log.info(f"Cloud execution enabled with provider: {cloud_provider}")
    else:
        os.environ["REMOTE"] = "False"
        log.info("Local execution mode enabled")

    # Set test-specific environment variables
    if test_type in ["ui", "all"]:
        browser = request.config.getoption("--browser")
        headless = request.config.getoption("--headless")
        os.environ["BROWSER"] = browser
        os.environ["HEADLESS"] = str(headless).lower()
        log.info(f"UI test configuration - Browser: {browser}, Headless: {headless}")

    if test_type in ["mobile", "all"]:
        platform = request.config.getoption("--platform")
        app = request.config.getoption("--app")
        os.environ["PLATFORM"] = platform
        if app:
            os.environ["APP"] = app
        log.info(f"Mobile test configuration - Platform: {platform}, App: {app}")


@pytest.fixture(scope="session")
def test_config(request):
    """Get test configuration from command line options."""
    return {
        'environment': request.config.getoption("--environment"),
        'test_type': request.config.getoption("--test-type"),
        'execution_mode': request.config.getoption("--execution-mode"),
        'cloud_provider': request.config.getoption("--cloud-provider"),
        'browser': request.config.getoption("--browser"),
        'headless': request.config.getoption("--headless"),
        'platform': request.config.getoption("--platform"),
        'app': request.config.getoption("--app")
    }


@pytest.fixture(scope="function")
def unified_driver_manager(request, test_config):
    """
    Create UnifiedDriverManager instance with all configuration parameters.
    This fixture handles all test types: UI, Mobile, and API.

    Args:
        request: Pytest request object
        test_config: Test configuration dictionary

    Returns:
        UnifiedDriverManager: Driver manager instance
    """
    test_type = test_config['test_type']

    # Determine the actual test type for driver creation when "all" is selected
    actual_test_type = _get_actual_test_type_from_node(request.node)

    log.info(f"Creating UnifiedDriverManager for {actual_test_type} tests (original test_type: {test_type})")

    # Only get API session if this is an API test
    api_session = None
    if actual_test_type == 'api':
        api_session = request.getfixturevalue('api_session')

    # Create driver manager with all configuration parameters
    driver_manager = UnifiedDriverManager(
        test_type=actual_test_type,
        platform=test_config['platform'],
        execution_mode=test_config['execution_mode'],
        cloud_provider=test_config['cloud_provider'],
        browser=test_config['browser'],
        headless=test_config['headless'],
        app_path=test_config['app'],
        implicit_wait=int(os.getenv('IMPLICIT_WAIT', '10')),
        session=api_session
    )

    # Add driver manager to request for access in tests (only if class-based)
    if hasattr(request, 'cls') and request.cls is not None:
        request.cls.driver_manager = driver_manager

    # Yield driver manager to test
    yield driver_manager

    # Clean up based on test type
    actual_test_type = _get_actual_test_type_from_node(request.node)
    if actual_test_type == 'ui':
        log.info("🖥️ UI test completed - cleaning up UI session")
    elif actual_test_type == 'mobile':
        log.info("📱 Mobile test completed - cleaning up mobile session")
    elif actual_test_type == 'api':
        log.info("🌐 API test completed - API session will be closed")


@pytest.fixture(scope="function")
def driver(request, unified_driver_manager, test_config):
    """
    Create driver instance for UI and Mobile tests.
    For API tests, this returns None as API tests use the session directly.

    This fixture initializes a driver instance for tests
    and handles cleanup after test completion.

    Args:
        request: Pytest request object
        unified_driver_manager: UnifiedDriverManager instance
        test_config: Test configuration dictionary

    Returns:
        webdriver or None: Driver instance for UI/Mobile, None for API
    """
    execution_mode = test_config['execution_mode']

    # Determine the actual test type for driver creation when "all" is selected
    actual_test_type = _get_actual_test_type_from_node(request.node)

    log.info(f"Initializing driver for {actual_test_type} test in {execution_mode} mode")

    # Initialize driver
    driver = unified_driver_manager.initialize_driver()

    # Add driver to request for access in tests (only if class-based)
    if hasattr(request, 'cls') and request.cls is not None:
        request.cls.driver = driver

    # Yield driver to test
    yield driver

    # Quit driver after test with specific cleanup messages
    if driver is not None:
        try:
            actual_test_type = _get_actual_test_type_from_node(request.node)
            if actual_test_type == 'ui':
                log.info("🖥️ Closing UI driver session")
            elif actual_test_type == 'mobile':
                log.info("📱 Closing mobile driver session")

            unified_driver_manager.quit_driver()

            if actual_test_type == 'ui':
                log.info("🖥️ UI driver session closed")
            elif actual_test_type == 'mobile':
                log.info("📱 Mobile driver session closed")

        except Exception as e:
            log.warning(f"Error during driver cleanup: {e}")


@pytest.fixture(scope="function")
def api_client(request, unified_driver_manager):
    """
    Provide API client functionality through UnifiedDriverManager.
    This fixture is specifically for API tests and provides access to all HTTP methods.

    Args:
        request: Pytest request object
        unified_driver_manager: UnifiedDriverManager instance

    Returns:
        UnifiedDriverManager: Driver manager instance configured for API testing
    """
    # Determine the actual test type for this specific test
    actual_test_type = _get_actual_test_type_from_node(request.node)

    if actual_test_type != 'api':
        pytest.skip("API client fixture is only available for API tests")

    return unified_driver_manager


# Legacy fixture for backward compatibility
@pytest.fixture(scope="function")
def driver_manager(unified_driver_manager):
    """Legacy fixture name for backward compatibility."""
    return unified_driver_manager


# Legacy fixture for backward compatibility
@pytest.fixture(scope="function")
def api_request_context(api_client):
    """Legacy fixture name for backward compatibility."""
    return api_client


def _get_actual_test_type_from_node(node):
    """
    Determine the actual test type based on the test node path.

    Args:
        node: Pytest node object

    Returns:
        str: The actual test type (ui, mobile, or api)
    """
    if hasattr(node, 'nodeid'):
        node_path = node.nodeid
    elif hasattr(node, 'fspath'):
        node_path = str(node.fspath)
    else:
        node_path = str(node)

    # Normalize path separators for cross-platform compatibility
    node_path = node_path.replace('\\', '/')

    if "/tests/mobile/" in node_path or "tests/mobile/" in node_path:
        return "mobile"
    elif "/tests/ui/" in node_path or "tests/ui/" in node_path:
        return "ui"
    elif "/tests/api/" in node_path or "tests/api/" in node_path:
        return "api"
    else:
        # Default fallback - check environment variable if available
        return os.getenv('TEST_TYPE', 'ui').lower()


@pytest.fixture(scope="function", autouse=True)
def set_current_test_type(request):
    """
    Automatically set the current test type based on the test location.
    This runs for every test and ensures the correct test type is available.
    """
    actual_test_type = _get_actual_test_type_from_node(request.node)
    os.environ["CURRENT_TEST_TYPE"] = actual_test_type
    log.debug(f"Set CURRENT_TEST_TYPE to: {actual_test_type} for test: {request.node.nodeid}")


def pytest_collection_modifyitems(config, items):
    """Add markers to test items based on their location."""
    for item in items:
        if "tests/mobile/" in item.nodeid:
            item.add_marker(pytest.mark.mobile)
        elif "tests/ui/" in item.nodeid:
            item.add_marker(pytest.mark.ui)
        elif "tests/api/" in item.nodeid:
            item.add_marker(pytest.mark.api)


def pytest_ignore_collect(collection_path: pathlib.Path, config):
    """
    Prevent collecting test files from undesired directories based on --test-type.
    Uses pathlib.Path as required by Pytest 8+.
    """
    test_type = config.getoption("--test-type")
    path_norm = collection_path.as_posix()  # Normalize path for cross-platform

    # If test_type is "all", don't ignore any test directories
    if test_type == "all":
        return False

    # Only collect tests that match the specified test type
    if test_type == "mobile" and ("/tests/ui/" in path_norm or "/tests/api/" in path_norm):
        return True
    elif test_type == "ui" and ("/tests/mobile/" in path_norm or "/tests/api/" in path_norm):
        return True
    elif test_type == "api" and ("/tests/ui/" in path_norm or "/tests/mobile/" in path_norm):
        return True

    return False


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "ui: mark test as UI test")
    config.addinivalue_line("markers", "mobile: mark test as mobile test")
    config.addinivalue_line("markers", "api: mark test as API test")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    pytest_html = item.config.pluginmanager.getplugin('html')
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, 'extra', [])

    # Set a simple description
    if "case" in item.fixturenames and hasattr(item, "callspec"):
        case = item.callspec.params.get("case", {})
        setattr(report, "description", case.get("description", ""))
    else:
        setattr(report, "description", item.nodeid.split("::")[-1])

    # Handle screenshots and logs only for failures
    if report.when in ('call', 'setup') and report.failed:
        driver = item.funcargs.get("driver", None)
        if driver:
            try:
                # Take screenshot
                screenshot = driver.get_screenshot_as_base64()
                extra.append(pytest_html.extras.image(screenshot, 'Screenshot'))
            except Exception as e:
                print(f"Failed to take screenshot: {e}")

        # Add only the log messages without tracebacks
        if hasattr(item, "capturelog"):
            logs = []
            for record in item.capturelog.get_records("call"):
                logs.append(f"{record.levelname}: {record.message}")

            if logs:
                extra.append(pytest_html.extras.text("\n".join(logs), "Logs"))


    report.extra = extra

def pytest_html_results_table_header(cells):
    """Add 'Description' column to report header."""
    cells.insert(2, html.th("Description"))
    cells.pop()  # Remove "Links" column if not needed

def pytest_html_results_table_row(report, cells):
    """Add 'Description' value to report row."""
    cells.insert(2, html.td(getattr(report, "description", "")))
    cells.pop()  # Remove "Links" column if not needed

@pytest.hookimpl(optionalhook=True)
def pytest_metadata(metadata):
    metadata.pop("Platform", None)
    metadata.pop("Packages", None)
    metadata.pop("Plugins", None)
    metadata.pop("JAVA_HOME", None)

def pytest_sessionstart(session):
    """Print test session information."""
    test_data["start_time"] = time.time()
    config = session.config
    test_type = config.getoption("--test-type")
    environment = config.getoption("--environment")
    execution_mode = config.getoption("--execution-mode")

    log.info("="*80)
    log.info(f"STARTING TEST SESSION")
    log.info(f"Environment: {environment}")
    log.info(f"Test Type: {test_type}")
    log.info(f"Execution Mode: {execution_mode}")

    if execution_mode == "cloud":
        cloud_provider = config.getoption("--cloud-provider")
        log.info(f"Cloud Provider: {cloud_provider}")

    if test_type in ["ui", "all"]:
        browser = config.getoption("--browser")
        headless = config.getoption("--headless")
        log.info(f"Browser: {browser}, Headless: {headless}")
    if test_type in ["mobile", "all"]:
        platform = config.getoption("--platform")
        log.info(f"Platform: {platform}")

    log.info("="*80)

test_data: Dict[str, Optional[float] | dict] = {
    "start_time": None,
    "end_time": None,
    "duration": None,
    "project_wise_results": defaultdict(
        lambda: defaultdict(
            lambda: {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "PassedTest": [],
                "FailedTest": [],
                "SkippedTest": [],
                "positive": 0,
                "negative": 0,
                "semantic": 0
            }
        )
    )
}


def get_test_group_and_project(nodeid):
    parts = nodeid.split("::")[0].split("/")
    if "tests" in parts:
        index = parts.index("tests")
        if index + 2 < len(parts):
            test_type = parts[index + 1]  # api or ui
            project = parts[index + 2]    # AiTutor or TestPlatform
            group = f"{test_type.upper()} Tests"
            return group, project
    return "Other Tests", "UnknownProject"

@pytest.hookimpl
def pytest_runtest_logreport(report):
    if report.when != "call":
        return

    test_name = report.nodeid
    duration = report.duration

    group, project = get_test_group_and_project(test_name)
    project_result = test_data["project_wise_results"][group][project]
    project_result["total"] += 1

    # Initialize test type tracking if not exists
    if "test_types" not in project_result:
        project_result["test_types"] = {
            "Positive": {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "tests": []},
            "Negative": {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "tests": []},
            "Semantic": {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "tests": []}
        }

    # Get the test item to check markers
    test_type = None
    # Try to get the item from the report
    if hasattr(report, 'node'):
        item = report.node
    else:
        # Fallback for older pytest versions
        item = report

    # Check for markers
    if hasattr(item, 'own_markers'):
        # Newer pytest versions
        for mark in item.own_markers:
            if mark.name in ['Positive', 'Negative', 'Semantic']:
                test_type = mark.name
                break
    elif hasattr(item, 'keywords'):
        # Older pytest versions
        for mark in item.keywords.keys():
            if mark in ['Positive', 'Negative', 'Semantic']:
                test_type = mark
                break

    test_info = {
        "name": test_name,
        "duration": f"{duration:.2f}s",
        "status": "passed" if report.passed else "failed" if report.failed else "skipped",
        "reason": report.longrepr.reprcrash.message.splitlines()[0] if report.failed else str(
            report.longrepr) if report.skipped else None
    }

    if test_type:
        project_result["test_types"][test_type]["total"] += 1
        project_result["test_types"][test_type]["tests"].append(test_info)

        if report.passed:
            project_result["test_types"][test_type]["passed"] += 1
            project_result["passed"] += 1
            project_result["PassedTest"].append(test_info)
        elif report.failed:
            project_result["test_types"][test_type]["failed"] += 1
            project_result["failed"] += 1
            project_result["FailedTest"].append(test_info)
        elif report.skipped:
            project_result["test_types"][test_type]["skipped"] += 1
            project_result["skipped"] += 1
            project_result["SkippedTest"].append(test_info)
    else:
        if report.passed:
            project_result["passed"] += 1
            project_result["PassedTest"].append(test_info)
        elif report.failed:
            project_result["failed"] += 1
            project_result["FailedTest"].append(test_info)
        elif report.skipped:
            project_result["skipped"] += 1
            project_result["SkippedTest"].append(test_info)

    # Also update the simple counters for backward compatibility
    if test_type == 'Positive':
        project_result["positive"] += 1
    elif test_type == 'Negative':
        project_result["negative"] += 1
    elif test_type == 'Semantic':
        project_result["semantic"] += 1

@pytest.hookimpl
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    test_data["end_time"] = time.time()
    if test_data["start_time"] is not None:
        test_data["duration"] = test_data["end_time"] - test_data["start_time"]
    else:
        test_data["duration"] = 0

    all_projects = test_data["project_wise_results"]

    terminalreporter.write_sep("-", f"Total duration: {test_data['duration']:.2f} seconds")

    env = config.getoption("--environment") or "unknown"
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    duration = f"{test_data['duration']:.2f} seconds"

    # Generate the detailed report
    report = (
        f"\nAPI/UI/Mobile TESTING REPORT\n"
        f"=========================\n"
        f"Environment : {env}\n"
        f"Date        : {current_time}\n"
        f"Duration    : {duration}\n\n"
    )

    # Track failed tests for the FAILED TESTS section
    failed_tests_by_project = defaultdict(list)

    # Process each test group (API/UI)
    for group, projects in sorted(all_projects.items()):
        # Add group header
        report += f"{group.upper()} SUMMARY\n"
        report += f"-------------------------\n"

        # Process each project in the group
        for project, data in sorted(projects.items()):
            # Project summary line
            report += (
                f"{project.ljust(12)} > "
                f"Total: {data['total']} | "
                f"Passed: {data['passed']} | "
                f"Failed: {data['failed']} | "
                f"Skipped: {data['skipped']}\n"
            )

            # Test type breakdown
            if "test_types" in data:
                for test_type, type_data in sorted(data["test_types"].items()):
                    if type_data["total"] > 0:
                        report += (
                            f"  - {test_type.ljust(8)} > "
                            f"Total: {type_data['total']} | "
                            f"Passed: {type_data['passed']} | "
                            f"Failed: {type_data['failed']} | "
                            f"Skipped: {type_data['skipped']}\n"
                        )

            # Collect failed tests for the FAILED TESTS section
            if data["failed"] > 0:
                failed_tests_by_project[f"{group}::{project}"].extend(data["FailedTest"])

        report += "\n"

    # Add FAILED TESTS section if there are any failures
    if failed_tests_by_project:
        report += (
            f"FAILED TESTS\n"
            f"-------------------------\n"
        )

        for project_path, tests in sorted(failed_tests_by_project.items()):
            group, project = project_path.split("::")
            report += f"{group.upper()}::{project}:\n"
            for test in tests:
                report += f"  - {test['name']} ({test['duration']})\n"
                if test.get('reason'):
                    report += f"    Reason: {test['reason']}\n"
            report += "\n"

    print(report)
