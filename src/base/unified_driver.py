"""
Unified Driver Module.

This module provides a unified driver manager for web, mobile, and API testing.
It supports local and remote WebDriver initialization for different platforms,
as well as API request handling with various HTTP methods.
"""
import os
import json
from typing import Optional, Dict, Any, Union
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from appium import webdriver as appium_webdriver
from appium.webdriver.client_config import AppiumClientConfig
from selenium.common.exceptions import WebDriverException
from string import Template
from appium.options.android import UiAutomator2Options

from src.utils import logger
log = logger.customLogger()

class UnifiedDriverManager:
    """Unified Driver Manager for handling web, mobile, and API testing."""

    def __init__(self, test_type='ui', platform='android', execution_mode='local',
                 cloud_provider='browserstack', browser='chrome', headless=False,
                 app_path=None, implicit_wait=10, session=None):
        """
        Initialize Unified Driver Manager with provided configuration.

        Args:
            test_type (str): Type of test - 'ui', 'mobile', or 'api'
            platform (str): Mobile platform - 'android' or 'ios'
            execution_mode (str): Execution mode - 'local' or 'cloud'
            cloud_provider (str): Cloud provider - 'browserstack', 'saucelabs'
            browser (str): Browser for UI tests - 'chrome', 'firefox', 'edge'
            headless (bool): Run browser in headless mode
            app_path (str): Path to mobile app or app ID for cloud execution
            implicit_wait (int): Implicit wait timeout in seconds
            session: Request session object for API testing
        """
        # Core configuration
        self.test_type = test_type.lower()
        self.platform = platform.lower()
        self.execution_mode = execution_mode.lower()
        self.cloud_provider = cloud_provider.lower()
        self.implicit_wait = implicit_wait
        self.driver = None

        # Web-specific configuration
        self.browser = browser.lower()
        self.headless = headless

        # Mobile-specific configuration
        self.app_path = app_path
        self.server_url = os.getenv('APPIUM_SERVER_URL', 'http://127.0.0.1:4723')

        # API-specific configuration
        self.session = session
        if self.test_type == 'api' and self.session:
            self._setup_api_methods()

        # Load mobile capabilities if needed
        if self.test_type == 'mobile':
            self.android_caps = self._load_capabilities('android_caps.json')
            self.ios_caps = self._load_capabilities('ios_caps.json')

        log.info(f"Initialized UnifiedDriverManager - Type: {self.test_type}, "
                   f"Platform: {self.platform}, Mode: {self.execution_mode}, "
                   f"Provider: {self.cloud_provider}")

    def _setup_api_methods(self):
        """Setup API method mapping for requests."""
        self.method_map = {
            'GET': self.get_request,
            'POST': self.post_request,
            'PUT': self.put_request,
            'PATCH': self.patch_request,
            'DELETE': self.delete_request
        }
        log.info("API methods initialized")

    def _load_capabilities(self, filename):
        """
        Load capabilities from JSON configuration file.

        Args:
            filename (str): Name of the JSON file containing capabilities

        Returns:
            dict: Capabilities dictionary
        """
        try:
            # Get the project root directory
            current_file_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_file_dir))
            config_path = os.path.join(project_root, 'config', filename)

            # Try alternative paths if main path doesn't exist
            if not os.path.exists(config_path):
                possible_paths = [
                    os.path.join(project_root, 'config', filename),
                    os.path.join(current_file_dir, '..', '..', 'config', filename),
                    os.path.join(os.getcwd(), 'config', filename),
                    os.path.join(os.path.dirname(os.getcwd()), 'config', filename)
                ]

                for path in possible_paths:
                    abs_path = os.path.abspath(path)
                    if os.path.exists(abs_path):
                        config_path = abs_path
                        break
                else:
                    # Create default config directory if not found
                    config_dir = os.path.join(project_root, 'config')
                    os.makedirs(config_dir, exist_ok=True)
                    config_path = os.path.join(config_dir, filename)
                    log.warning(f"Config file not found. Expected path: {config_path}")
                    return {}

            log.info(f"Loading capabilities from: {config_path}")

            with open(config_path, 'r') as f:
                caps = json.load(f)

            # Determine the correct key to use based on execution mode
            if self.execution_mode == 'local':
                config_key = 'local'
            elif self.execution_mode == 'cloud':
                # For cloud execution, use the cloud provider as the key
                config_key = self.cloud_provider
            else:
                config_key = self.execution_mode

            # Process environment variable placeholders in capabilities
            if config_key in caps and isinstance(caps[config_key], dict):
                caps_str = json.dumps(caps[config_key])
                template = Template(caps_str)
                processed_caps_str = template.safe_substitute(os.environ)
                processed_caps = json.loads(processed_caps_str)

                log.info(f"Successfully loaded capabilities for {config_key} mode")
                return processed_caps
            else:
                log.warning(f"No capabilities found for configuration key: {config_key}")
                log.info(f"Available configuration keys in {filename}: {list(caps.keys())}")
                return {}

        except FileNotFoundError:
            log.error(f"Capabilities file not found: {filename}")
            return {}
        except json.JSONDecodeError as e:
            log.error(f"Invalid JSON in capabilities file {filename}: {str(e)}")
            return {}
        except Exception as e:
            log.error(f"Error loading capabilities from {filename}: {str(e)}")
            return {}

    def initialize_driver(self):
        """
        Initialize driver instance based on test type and configuration.

        Returns:
            webdriver or None: Driver instance for UI/Mobile, None for API
        """
        log.info(f"Initializing driver for test type: {self.test_type}")

        try:
            if self.test_type == 'ui':
                self.driver = self._initialize_web_driver()
            elif self.test_type == 'mobile':
                self.driver = self._initialize_mobile_driver()

            elif self.test_type == 'api':
                log.info("API test type - no driver initialization needed")
                return None
            else:
                log.warning(f"Unknown test type: {self.test_type}")
                return None

            # Configure driver
            if self.driver:
                self.driver.implicitly_wait(self.implicit_wait)
                log.info(f"Successfully initialized driver for {self.test_type}")

            return self.driver

        except WebDriverException as e:
            log.error(f"Failed to initialize driver: {str(e)}")
            raise
        except Exception as e:
            log.error(f"Unexpected error initializing driver: {str(e)}")
            raise

    def _initialize_web_driver(self):
        """
        Initialize web driver instance based on execution mode.

        Returns:
            webdriver: Web driver instance
        """
        if self.execution_mode == 'cloud':
            return self._initialize_remote_web_driver()
        else:
            return self._initialize_local_web_driver()

    def _initialize_local_web_driver(self):
        """
        Initialize local web driver instance.

        Returns:
            webdriver: Local web driver instance
        """
        log.info(f"Initializing local {self.browser} WebDriver")

        if self.browser == "chrome":
            options = ChromeOptions()
            if self.headless:
                options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--log-level=3")  # Suppress warnings
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")

            driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=options
            )

        elif self.browser == "firefox":
            options = FirefoxOptions()
            if self.headless:
                options.add_argument("--headless")

            driver = webdriver.Firefox(
                service=FirefoxService(GeckoDriverManager().install()),
                options=options
            )

        elif self.browser == "edge":
            options = EdgeOptions()
            if self.headless:
                options.add_argument("--headless")

            driver = webdriver.Edge(
                service=EdgeService(EdgeChromiumDriverManager().install()),
                options=options
            )

        else:
            log.error(f"Unsupported browser: {self.browser}")
            raise ValueError(f"Unsupported browser: {self.browser}")

        # Configure WebDriver
        driver.maximize_window()

        log.info(f"Initialized local {self.browser} WebDriver")
        return driver

    def _initialize_remote_web_driver(self):
        """
        Initialize remote web driver instance for cloud testing.

        Returns:
            webdriver: Remote web driver instance
        """
        log.info(f"Initializing remote {self.browser} WebDriver on {self.cloud_provider}")

        remote_url = self._get_cloud_url()
        options = self._get_browser_options()

        # Add cloud provider specific capabilities
        if self.cloud_provider == "browserstack":
            bs_options = {
                "userName": os.getenv('BS_USERNAME'),
                "accessKey": os.getenv('BS_ACCESS_KEY'),
                "resolution": os.getenv('RESOLUTION', '1920x1080'),
                "projectName": "Automation Framework",
                "buildName": "Build 1.0",
                "sessionName": f"{self.browser} Test",
                "local": "false",
                "seleniumVersion": "4.0.0",
            }

            options.set_capability("browserName", self.browser)
            options.set_capability("browserVersion", os.getenv('BROWSER_VERSION', 'latest'))

            options.set_capability("platformName", "Windows 11")

            options.set_capability("bstack:options", bs_options)


        elif self.cloud_provider == "saucelabs":
            sl_options = {
                "username": os.getenv('BS_USERNAME'),  # Reusing the same env vars
                "accessKey": os.getenv('BS_ACCESS_KEY'),
                "resolution": os.getenv('RESOLUTION', '1920x1080'),
                "project": "Automation Framework",
                "build": "Build 1.0",
                "name": f"{self.browser} Test",
                "selenium_version": "4.0.0",
            }

            options.set_capability("browserName", self.browser)
            options.set_capability("browserVersion", os.getenv('BROWSER_VERSION', 'latest'))
            options.set_capability("platformName", os.getenv('PLATFORM', 'Windows'))
            options.set_capability("sauce:options", sl_options)



        try:
            # Initialize remote WebDriver
            driver = webdriver.Remote(
                command_executor=remote_url,
                options=options
            )
            print("****************************************8")
            print(options.capabilities.get('platformName', 'Not set'))
            print(options.capabilities.get('browserName', 'Not set'))
            print("****************************************9")

            log.info(f"Successfully initialized remote {self.browser} WebDriver on {self.cloud_provider}")
            log.info(f"Session ID: {driver.session_id}")
            return driver

        except Exception as e:
            log.error(f"Failed to initialize remote WebDriver: {str(e)}")
            log.error(f"URL: {remote_url}")
            log.error(f"Browser: {self.browser}")
            log.error(f"Platform: {options.capabilities.get('platformName', 'Not set')}")
            raise

    def _get_cloud_url(self):
        """Get cloud provider URL."""
        if self.cloud_provider == 'browserstack':
            return os.getenv('REMOTE_URL', 'https://hub-cloud.browserstack.com/wd/hub')
        elif self.cloud_provider == 'saucelabs':
            return os.getenv('REMOTE_URL', 'https://ondemand.us-west-1.saucelabs.com/wd/hub')
        else:
            raise ValueError(f"Unsupported cloud provider: {self.cloud_provider}")

    def _get_browser_options(self):
        """
        Get browser-specific options.

        Returns:
            Options: Browser options
        """
        if self.browser == "chrome":
            options = ChromeOptions()
            if self.headless:
                options.add_argument("--headless=new")
            return options

        elif self.browser == "firefox":
            options = FirefoxOptions()
            if self.headless:
                options.add_argument("--headless")
            return options

        elif self.browser == "edge":
            options = EdgeOptions()
            if self.headless:
                options.add_argument("--headless")
            return options

        else:
            raise ValueError(f"Unsupported browser: {self.browser}")

    def _initialize_mobile_driver(self):
        """
        Initialize mobile driver instance based on execution mode.

        Returns:
            webdriver: Mobile driver instance
        """
        log.info(f"Initializing {self.platform} driver in {self.execution_mode} mode")

        if self.execution_mode == 'local':
            return self._initialize_local_mobile_driver()
        else:
            return self._initialize_cloud_mobile_driver()

    def _initialize_local_mobile_driver(self):
        """
        Initialize local mobile driver instance.

        Returns:
            webdriver: Local mobile driver instance
        """
        client_config = AppiumClientConfig(
            remote_server_addr=self.server_url,
            keep_alive=False
        )

        if self.platform == 'android':
            options = UiAutomator2Options()
            caps = self.android_caps.copy()

            # Override app path if provided
            if self.app_path:
                caps['app'] = self.app_path

            options.load_capabilities(caps)
            return appium_webdriver.Remote(options=options, client_config=client_config)

        elif self.platform == 'ios':
            # options = XCUITestOptions()
            # caps = self.ios_caps.copy()
            #
            # # Override app path if provided
            # if self.app_path:
            #     caps['app'] = self.app_path
            #
            # options.load_capabilities(caps)
            # return appium_webdriver.Remote(options=options, client_config=client_config)
            raise NotImplementedError("iOS support not implemented yet")
        else:
            raise ValueError(f"Unsupported platform: {self.platform}")

    def _initialize_cloud_mobile_driver(self):
        """
        Initialize cloud mobile driver instance.

        Returns:
            webdriver: Cloud mobile driver instance
        """
        cloud_url = self._get_mobile_cloud_url()

        client_config = AppiumClientConfig(
            remote_server_addr=cloud_url,
            keep_alive=False
        )

        if self.platform == 'android':
            options = UiAutomator2Options()
            caps = self.android_caps.copy()

            # Override app path/ID if provided for cloud execution
            if self.app_path:
                caps['app'] = self.app_path

            options.load_capabilities(caps)
            driver=appium_webdriver.Remote(options=options, client_config=client_config)
            print("***************************88888888888888888888")
            print(driver.session_id)
            return driver

        elif self.platform == 'ios':
            # options = XCUITestOptions()
            # caps = self.ios_caps.copy()
            #
            # # Override app path/ID if provided for cloud execution
            # if self.app_path:
            #     caps['app'] = self.app_path
            #
            # options.load_capabilities(caps)
            # return appium_webdriver.Remote(options=options, client_config=client_config)
            raise NotImplementedError("iOS support not implemented yet")
        else:
            raise ValueError(f"Unsupported platform: {self.platform}")

    def _get_mobile_cloud_url(self):
        """Get mobile cloud provider URL."""
        if self.cloud_provider == 'browserstack':
            return "https://hub.browserstack.com/wd/hub"
        elif self.cloud_provider == 'saucelabs':
            return "https://ondemand.us-west-1.saucelabs.com/wd/hub"
        else:
            raise ValueError(f"Unsupported mobile cloud provider: {self.cloud_provider}")

    def quit_driver(self):
        """Quit driver instance."""
        if self.driver:
            log.info(f"Quitting {self.test_type} driver")
            try:
                self.driver.quit()
            except Exception as e:
                log.warning(f"Error quitting driver: {str(e)}")
            finally:
                self.driver = None

    # API Methods Integration
    def make_request(self, base_url: str, api_endpoint: str, method: str = 'GET',
                    path_params: Optional[Dict] = None, **kwargs) -> Any:
        """
        Generic method to make API requests based on the specified method.

        Args:
            base_url: Base URL of the API
            api_endpoint: API endpoint (may contain placeholders like {id})
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            path_params: Dictionary to replace path placeholders in api_endpoint
            **kwargs: Additional arguments to pass to the request method

        Returns:
            Response object

        Raises:
            ValueError: If unsupported HTTP method is provided or session not available
            KeyError: If path_params is missing a required placeholder
        """
        if self.test_type != 'api':
            raise ValueError(f"API requests are only supported for test_type='api', current type: {self.test_type}")

        if not self.session:
            raise ValueError("Session is required for API requests. Please provide session during initialization.")

        method = method.upper()
        if method not in self.method_map:
            raise ValueError(f"Unsupported HTTP method: {method}")

        if path_params:
            try:
                log.info(f"Before replacement: {api_endpoint}, path_params: {path_params}")
                api_endpoint = api_endpoint.format(**path_params)
                log.info(f"After replacement: {api_endpoint}")
            except KeyError as e:
                log.error(f"Missing path parameter: {e}")
                raise
            except Exception as e:
                log.error(f"Error formatting path parameters: {e}")
                raise

        log.info(f"Making {method} request to {base_url}{api_endpoint}")
        return self.method_map[method](base_url, api_endpoint, **kwargs)

    def get_request(self, base_url: str, api_endpoint: str, header: Optional[Dict] = None,
                    query_params: Optional[Dict] = None) -> Any:
        """
        Perform a GET request.

        Args:
            base_url: Base URL of the API
            api_endpoint: API endpoint
            header: Optional headers
            query_params: Optional query parameters

        Returns:
            Response object
        """
        try:
            log.info(f"Request Method: GET")
            url = f"{base_url}{api_endpoint}"
            log.info(f"Constructed URL: {url}")

            if query_params:
                log.info(f"Query Parameters: {query_params}")
            else:
                log.info("No query parameters provided.")

            if header:
                log.info(f"Request Headers: {header}")
            else:
                log.info("No headers provided.")

            response = self.session.get(url, headers=header, params=query_params, timeout=None)
            return response

        except Exception as e:
            log.error(f"An error occurred during the GET request: {str(e)}")
            raise

    def post_request(self, base_url: str, api_endpoint: str, header: Optional[Dict] = None,
                     param: Optional[Dict] = None, payload: Optional[Union[Dict, str]] = None,
                     file: Optional[Dict] = None) -> Any:
        """
        Perform a POST request.

        Args:
            base_url: Base URL of the API
            api_endpoint: API endpoint
            header: Optional headers
            param: Optional query parameters
            payload: Optional request payload
            file: Optional files to upload

        Returns:
            Response object
        """
        url = f"{base_url}{api_endpoint}"
        log.info(f"Request Type: POST")
        log.info(f"Request URL: {url}")

        if header:
            log.info(f"Request Headers: {header}")
        else:
            log.warning("No headers provided.")

        if param:
            log.info(f"Query Parameters: {param}")
        else:
            log.warning("No query parameters provided.")

        if payload:
            log.info(f"Request Payload: {payload}")
        else:
            log.warning("No payload provided.")

        if file:
            log.info("File included in the request.")
        else:
            log.info("No file included in the request.")

        try:
            if file is not None:
                response = self.session.post(url, headers=header, data=payload,
                                             params=param, files=file, timeout=None)
            else:
                response = self.session.post(url, headers=header, data=json.dumps(payload),
                                             params=param, timeout=None)
            return response

        except Exception as e:
            log.error(f"Error occurred during the POST request: {str(e)}")
            raise

    def put_request(self, base_url: str, api_endpoint: str, header: Optional[Dict] = None,
                    payload: Optional[Dict] = None, param: Optional[Dict] = None) -> Any:
        """
        Perform a PUT request.

        Args:
            base_url: Base URL of the API
            api_endpoint: API endpoint
            header: Optional headers
            payload: Optional request payload
            param: Optional query parameters

        Returns:
            Response object
        """
        url = f"{base_url}{api_endpoint}"
        log.info(f"Request Type: PUT")
        log.info(f"Request URL: {url}")

        if header:
            log.info(f"Request Headers: {header}")
        else:
            log.warning("No headers provided.")

        if param:
            log.info(f"Query Parameters: {param}")
        else:
            log.warning("No query parameters provided.")

        if payload:
            log.info(f"Request Payload: {payload}")
        else:
            log.warning("No payload provided.")

        try:
            response = self.session.put(url, headers=header, data=json.dumps(payload),
                                        params=param, timeout=None)
            return response

        except Exception as e:
            log.error(f"Error occurred during the PUT request to {url}: {str(e)}")
            raise

    def patch_request(self, base_url: str, api_endpoint: str, header: Optional[Dict] = None,
                      payload: Optional[Dict] = None) -> Any:
        """
        Perform a PATCH request.

        Args:
            base_url: Base URL of the API
            api_endpoint: API endpoint
            header: Optional headers
            payload: Optional request payload

        Returns:
            Response object
        """
        url = f"{base_url}{api_endpoint}"
        log.info(f"Request Type: PATCH")
        log.info(f"Request URL: {url}")

        if header:
            log.info(f"Request Headers: {header}")
        else:
            log.warning("No headers provided.")

        if payload:
            log.info(f"Request Payload: {payload}")
        else:
            log.warning("No payload provided.")

        try:
            response = self.session.patch(url, headers=header, data=json.dumps(payload), timeout=None)
            return response

        except Exception as e:
            log.error(f"Error occurred during the PATCH request to {url}: {str(e)}")
            raise

    def delete_request(self, base_url: str, api_endpoint: str, header: Optional[Dict] = None,
                       payload: Optional[Dict] = None, query_params: Optional[Dict] = None) -> Any:
        """
        Perform a DELETE request.

        Args:
            base_url: Base URL of the API
            api_endpoint: API endpoint
            header: Optional headers
            payload: Optional request payload
            query_params: Optional query parameters

        Returns:
            Response object
        """
        url = f"{base_url}{api_endpoint}"
        log.info(f"Request Type: DELETE")
        log.info(f"Request URL: {url}")

        if header:
            log.info(f"Request Headers: {header}")
        else:
            log.warning("No headers provided.")

        if payload:
            log.info(f"Request Payload: {payload}")
        else:
            log.warning("No payload provided.")

        if query_params:
            log.info(f"Query Parameters: {query_params}")
        else:
            log.warning("No query parameters provided.")

        try:
            response = self.session.delete(url, headers=header, params=query_params, timeout=None)
            return response

        except Exception as e:
            log.error(f"Error occurred during the DELETE request to {url}: {str(e)}")
            raise