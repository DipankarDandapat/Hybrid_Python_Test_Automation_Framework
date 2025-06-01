import os
import time
import datetime
from functools import wraps

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotVisibleException,
    StaleElementReferenceException,
    ElementNotInteractableException,
    WebDriverException
)

from src.utils import logger
log = logger.customLogger()

# --- Retry Decorator ---
def retry_on_timeout(retries=1, delay=30):
    """Decorator to retry a function call if TimeoutException occurs."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts <= retries:
                try:
                    return func(*args, **kwargs)
                except (TimeoutException, WebDriverException) as e:
                    attempts += 1
                    if attempts > retries:
                        log.error(f"Operation failed after {retries} retry. Error: {str(e)}")
                        raise
                    log.warning(
                        f"Timeout caught (attempt {attempts}/{retries}). Retrying in {delay}s...")
                    time.sleep(delay)

        return wrapper

    return decorator

class BasePage:
    """Enhanced Base Page class for all page objects."""

    def __init__(self, driver):
        """Initialize BasePage with driver and configuration."""
        self.driver = driver
        try:
            self.explicit_wait_timeout = int(os.getenv("EXPLICIT_WAIT", "20"))
        except ValueError:
            log.warning("Invalid EXPLICIT_WAIT env var. Using default: 20s")
            self.explicit_wait_timeout = 20

        self.default_base_url = os.getenv("AUTOMATIONEXERCISE_BASE_URL", "https://google.com")
        self.screenshots_dir = os.getenv("SCREENSHOTS_DIR", "reports/screenshots")
        os.makedirs(self.screenshots_dir, exist_ok=True)
        log.info(f"Initialized BasePage. Base URL: {self.default_base_url}, Default Wait: {self.explicit_wait_timeout}s")

    # --- Private Helper Methods ---

    def _wait_for_condition(self, locator, condition, timeout=None, message=""):
        """
        Internal helper to wait for a specific expected condition on an element.
        Handles TimeoutException and logs appropriately.

        Args:
            locator (tuple): Locator tuple (By, value)
            condition (callable): Expected condition function from selenium.webdriver.support.expected_conditions
            timeout (int, optional): Specific timeout for this wait. Defaults to self.explicit_wait_timeout.
            message (str, optional): Custom message for TimeoutException.

        Returns:
            WebElement or list[WebElement] or bool: Result from the condition.

        Raises:
            TimeoutException: If the condition is not met within the timeout.
        """
        timeout = timeout if timeout is not None else self.explicit_wait_timeout
        wait = WebDriverWait(self.driver, timeout,ignored_exceptions=[NoSuchElementException, ElementNotVisibleException,StaleElementReferenceException])
        try:
            element = wait.until(condition(locator), message)
            condition_name = condition.__name__ if hasattr(condition, "__name__") else "custom condition"
            log.info(f"Condition {condition_name} met for locator: {locator}")
            return element
        except TimeoutException:
            condition_name = condition.__name__ if hasattr(condition, "__name__") else "custom condition"
            error_msg = f"TimeoutException ({timeout}s): Condition {condition_name} not met for locator: {locator}. {message}"
            log.error(error_msg)
            self.take_screenshot("timeout_exception")
            raise TimeoutException(error_msg)
        except Exception as e:
            log.error(f"An unexpected error occurred during wait for {locator}: {str(e)}")
            self.take_screenshot("wait_exception")
            raise

    def _highlight(self, element, effect_time=0.1, color="red", border=3):
        """
        Highlights (blinks) a Selenium WebDriver element. Useful for debugging.
        (Helper method - consider making it public if needed for debugging steps)
        """
        try:
            original_style = element.get_attribute("style")
            highlight_style = f"border: {border}px solid {color};"
            self.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, highlight_style)
            time.sleep(effect_time)
            self.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, original_style)
        except WebDriverException:
            log.warning("Could not highlight element, possibly due to page refresh or element becoming stale.")

    # --- Core Interaction Methods ---

    def open(self,base_url_env_key=None,url_path="" ):
        """
        Open the full URL by combining base URL and path.
        :param url_path: Optional path to be appended to base URL.
        :param base_url_env_key: Optional env key like 'UI_BASE_URL1', 'UI_BASE_URL2' to override base URL.
        """
        # Fetch the base URL from env if a key is provided
        if base_url_env_key:
            base_url = os.getenv(base_url_env_key)
            if not base_url:
                raise ValueError(f"Environment variable '{base_url_env_key}' not found.")
        else:
            base_url = self.default_base_url

        full_url = f"{base_url.rstrip('/')}/{url_path.lstrip('/')}"
        log.info(f"Opening URL: {full_url}")
        try:
            self.driver.get(full_url)
            log.info(f"Opened URL successfully: {full_url}")
        except Exception as e:
            log.error(f"Failed to open URL {full_url}: {str(e)}")
            raise
        return self

    @retry_on_timeout()
    def find_element(self, locator, timeout=None):
        """
        Find a single element using the specified locator and wait condition.

        Args:
            locator (tuple): Locator tuple (By, value)
            timeout (int, optional): Specific timeout for this wait.

        Returns:
            WebElement: The found element.
        """
        log.info(f"Finding element: {locator}")
        return self._wait_for_condition(locator, EC.presence_of_element_located, timeout)

    @retry_on_timeout()
    def find_elements(self, locator, timeout=None):
        """
        Find multiple elements using the specified locator.

        Args:
            locator (tuple): Locator tuple (By, value)
            timeout (int, optional): Specific timeout for this wait.

        Returns:
            list[WebElement]: A list of found elements.
        """
        log.info(f"Finding elements: {locator}")
        return self._wait_for_condition(locator, EC.presence_of_all_elements_located, timeout)

    @retry_on_timeout()
    def click(self, locator, timeout=None, use_js_fallback=True):
        """
        Clicks an element after ensuring it is clickable.
        Optionally uses JavaScript click as a fallback.

        Args:
            locator (tuple): Locator tuple (By, value)
            timeout (int, optional): Specific timeout for this wait.
            use_js_fallback (bool): If True, attempts JS click if normal click fails.

        Returns:
            BasePage: self for chaining.
        """
        log.info(f"Attempting to click element: {locator}")
        try:
            element = self._wait_for_condition(locator, EC.element_to_be_clickable, timeout)
            self._highlight(element)  # Highlight before clicking
            element.click()
            log.info(f"Clicked element successfully: {locator}")
        except ElementNotInteractableException as e:
            log.warning(f"Element {locator} not interactable using standard click: {str(e)}")
            if use_js_fallback:
                log.info(f"Attempting JavaScript click fallback for element: {locator}")
                try:
                    element = self.find_element(locator, timeout=5)  # Re-find element
                    self.execute_script("arguments[0].click();", element)
                    log.info(f"Clicked element using JavaScript fallback: {locator}")
                except Exception as js_e:
                    log.error(f"JavaScript click fallback also failed for element {locator}: {str(js_e)}")
                    self.take_screenshot("click_failed")
                    raise js_e  # Re-raise the JS exception
            else:
                self.take_screenshot("click_failed")
                raise e  # Re-raise the original exception if no fallback
        except Exception as e:
            log.error(f"Failed to click element {locator}: {str(e)}")
            self.take_screenshot("click_failed")
            raise
        return self

    @retry_on_timeout()
    def input_text(self, locator, text, clear_first=True, timeout=None):
        """
        Inputs text into an element after ensuring it is visible.

        Args:
            locator (tuple): Locator tuple (By, value)
            text (str): Text to input.
            clear_first (bool): Clear the field before inputting text. Defaults to True.
            timeout (int, optional): Specific timeout for this wait.

        Returns:
            BasePage: self for chaining.
        """
        log.info(f"Inputting text into element: {locator}")
        try:
            element = self._wait_for_condition(locator, EC.visibility_of_element_located, timeout)
            self._highlight(element)
            if clear_first:
                element.clear()
                log.debug(f"Cleared existing text in element: {locator}")
            element.send_keys(text)
            log.info(f"Entered text '{text}' into element: {locator}")
        except Exception as e:
            log.error(f"Failed to input text into element {locator}: {str(e)}")
            self.take_screenshot("input_text_failed")
            raise
        return self


    @retry_on_timeout()
    def get_text(self, locator, timeout=None):
        """
        Gets the text content of an element.

        Args:
            locator (tuple): Locator tuple (By, value)
            timeout (int, optional): Specific timeout for this wait.

        Returns:
            str: The text content of the element.
        """
        log.info(f"Getting text from element: {locator}")
        try:
            element = self._wait_for_condition(locator, EC.visibility_of_element_located, timeout)
            text = element.text
            masked_text = "********" if "password" in str(locator).lower() else f"\"{text}\""
            log.info(f"Got text {masked_text} from element: {locator}")
            return text
        except Exception as e:
            log.error(f"Failed to get text from element {locator}: {str(e)}")
            self.take_screenshot("get_text_failed")
            raise

    @retry_on_timeout()
    def get_attribute(self, locator, attribute_name, timeout=None):
        """
        Gets the value of a specified attribute of an element.

        Args:
            locator (tuple): Locator tuple (By, value)
            attribute_name (str): Name of the attribute (e.g., "value", "href", "class").
            timeout (int, optional): Specific timeout for this wait.

        Returns:
            str or None: The value of the attribute, or None if not found.
        """
        log.info(f"Getting attribute ", {attribute_name}, f" from element: {locator}")
        try:
            element = self._wait_for_condition(locator, EC.presence_of_element_located, timeout)
            value = element.get_attribute(attribute_name)
            log.info(f"Attribute ", {attribute_name}, f" value: ",
                     "********" if "password" in str(locator).lower() and attribute_name == "value" else f"\"{value}\"",
                     f" for element: {locator}")
            return value
        except Exception as e:
            log.error(f"Failed to get attribute ", {attribute_name}, f" from element {locator}: {str(e)}")
            self.take_screenshot("get_attribute_failed")
            # Return None instead of raising? Depends on desired behavior.
            return None

            # --- State Checking Methods ---

    def is_element_present(self, locator, timeout=1):
        """
        Checks if an element is present in the DOM (may not be visible).
        Uses a short timeout by default for quick checks.

        Args:
            locator (tuple): Locator tuple (By, value)
            timeout (int, optional): Specific timeout for this check. Defaults to 1.

        Returns:
            bool: True if the element is present, False otherwise.
        """
        log.info(f"Checking if element is present: {locator} (timeout={timeout}s)")
        try:
            self._wait_for_condition(locator, EC.presence_of_element_located, timeout)
            log.info(f"Element is present: {locator}")
            return True
        except TimeoutException:
            log.info(f"Element not present: {locator}")
            return False

    def is_element_visible(self, locator, timeout=1):
        """
        Checks if an element is present and visible on the page.
        Uses a short timeout by default for quick checks.

        Args:
            locator (tuple): Locator tuple (By, value)
            timeout (int, optional): Specific timeout for this check. Defaults to 1.

        Returns:
            bool: True if the element is visible, False otherwise.
        """
        log.info(f"Checking if element is visible: {locator} (timeout={timeout}s)")
        try:
            self._wait_for_condition(locator, EC.visibility_of_element_located, timeout)
            log.info(f"Element is visible: {locator}")
            return True
        except TimeoutException:
            log.info(f"Element not visible: {locator}")
            return False

    def is_element_invisible(self, locator, timeout=1):
        """
        Checks if an element is invisible or not present in the DOM.
        Uses a short timeout by default for quick checks.

        Args:
            locator (tuple): Locator tuple (By, value)
            timeout (int, optional): Specific timeout for this check. Defaults to 1.

        Returns:
            bool: True if the element is invisible, False otherwise.
        """
        log.info(f"Checking if element is invisible: {locator} (timeout={timeout}s)")
        try:
            self._wait_for_condition(locator, EC.invisibility_of_element_located, timeout)
            log.info(f"Element is invisible: {locator}")
            return True
        except TimeoutException:
            log.info(f"Element is still visible or present: {locator}")
            return False

    @retry_on_timeout()
    def is_element_enabled(self, locator, timeout=None):
        """
        Checks if an element is enabled.

        Args:
            locator (tuple): Locator tuple (By, value)
            timeout (int, optional): Specific timeout for this wait.

        Returns:
            bool: True if the element is enabled, False otherwise.
        """
        log.info(f"Checking if element is enabled: {locator}")
        try:
            element = self._wait_for_condition(locator, EC.presence_of_element_located, timeout)
            is_enabled = element.is_enabled()
            log.info(f"Element {locator} enabled status: {is_enabled}")
            return is_enabled
        except Exception as e:
            log.error(f"Failed to check if element {locator} is enabled: {str(e)}")
            return False  # Return False on error

    @retry_on_timeout()
    def is_element_selected(self, locator, timeout=None):
        """
        Checks if a checkbox or radio button element is selected.

        Args:
            locator (tuple): Locator tuple (By, value)
            timeout (int, optional): Specific timeout for this wait.

        Returns:
            bool: True if the element is selected, False otherwise.
        """
        log.info(f"Checking if element is selected: {locator}")
        try:
            element = self._wait_for_condition(locator, EC.presence_of_element_located, timeout)
            is_selected = element.is_selected()
            log.info(f"Element {locator} selected status: {is_selected}")
            return is_selected
        except Exception as e:
            log.error(f"Failed to check if element {locator} is selected: {str(e)}")
            return False  # Return False on error

    # --- Explicit Wait Methods ---

    def wait_for_element_visible(self, locator, timeout=None):
        """Waits for an element to be visible."""
        log.info(f"Waiting for element to be visible: {locator}")
        return self._wait_for_condition(locator, EC.visibility_of_element_located, timeout)

    def wait_for_element_present(self, locator, timeout=None):
        """Waits for an element to be present in the DOM."""
        log.info(f"Waiting for element to be present: {locator}")
        return self._wait_for_condition(locator, EC.presence_of_element_located, timeout)

    def wait_for_element_clickable(self, locator, timeout=None):
        """Waits for an element to be clickable."""
        log.info(f"Waiting for element to be clickable: {locator}")
        return self._wait_for_condition(locator, EC.element_to_be_clickable, timeout)

    def wait_for_element_invisible(self, locator, timeout=None):
        """Waits for an element to become invisible or not present."""
        log.info(f"Waiting for element to be invisible: {locator}")
        return self._wait_for_condition(locator, EC.invisibility_of_element_located, timeout)

    def wait_for_text_in_element(self, locator, text, timeout=None):
        """Waits for specific text to be present in an element."""
        log.info(f"Waiting for text ", {text}, f" in element: {locator}")
        return self._wait_for_condition(locator, EC.text_to_be_present_in_element(locator, text), timeout)

    def wait_for_attribute_value(self, locator, attribute, expected_value, timeout=None):
        """
        Waits for an element's attribute to have a specific value.

        Args:
            locator (tuple): Locator tuple (By, value)
            attribute (str): Attribute name.
            expected_value (str): Expected value of the attribute.
            timeout (int, optional): Specific timeout for this wait.

        Returns:
            bool: True if condition met, raises TimeoutException otherwise.
        """
        log.info(f"Waiting for attribute '{attribute}' of element {locator} to be '{expected_value}'")

        # Custom condition since EC.attribute_to_be doesn't exist directly
        def attribute_value_matches(driver):
            try:
                element = driver.find_element(*locator)
                actual_value = element.get_attribute(attribute)
                return actual_value == expected_value
            except (NoSuchElementException, StaleElementReferenceException):
                return False
            except Exception as e:
                log.warning(f"Error checking attribute '{attribute}' for {locator}: {e}")
                return False

        wait = WebDriverWait(self.driver, timeout if timeout is not None else self.explicit_wait_timeout)
        try:
            return wait.until(
                attribute_value_matches,
                message=f"Attribute '{attribute}' for {locator} did not become '{expected_value}'"
            )
        except TimeoutException:
            log.error(f"Timeout waiting for attribute '{attribute}' of {locator} to be '{expected_value}'")
            self.take_screenshot("wait_attribute_failed")
            raise


    def wait_for_page_load_complete(self, timeout=None):
        """
        Waits for the page's document.readyState to be "complete".

        Args:
            timeout (int, optional): Specific timeout for this wait.
        """
        timeout = timeout if timeout is not None else self.explicit_wait_timeout
        log.info(f"Waiting for page load to complete (document.readyState === 'complete') for {timeout}s")
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            log.info("Page load complete.")
        except TimeoutException:
            log.error(f"Page did not reach readyState 'complete' within {timeout} seconds.")
            self.take_screenshot("page_load_timeout")
            # Optionally raise, or just log the warning
            # raise
        except Exception as e:
            log.error(f"Error waiting for page load: {str(e)}")
            # raise

    # --- Dropdown Methods ---

    @retry_on_timeout()
    def select_dropdown_option_by_text(self, locator, visible_text, timeout=None):
        """Selects an option from a dropdown by its visible text."""
        log.info(f"Selecting dropdown option by text: '{visible_text}' for locator: {locator}")
        try:
            element = self._wait_for_condition(locator, EC.visibility_of_element_located, timeout)
            select = Select(element)
            select.select_by_visible_text(visible_text)
            log.info(f"Selected option '{visible_text}' successfully.")
        except Exception as e:
            log.error(f"Failed to select dropdown option by text '{visible_text}' for {locator}: {str(e)}")
            self.take_screenshot("dropdown_select_failed")
            raise
        return self

    @retry_on_timeout()
    def select_dropdown_option_by_value(self, locator, value, timeout=None):
        """Selects an option from a dropdown by its value attribute."""
        log.info(f"Selecting dropdown option by value: '{value}' for locator: {locator}")
        try:
            element = self._wait_for_condition(locator, EC.visibility_of_element_located, timeout)
            select = Select(element)
            select.select_by_value(value)
            log.info(f"Selected option with value '{value}' successfully.")
        except Exception as e:
            log.error(f"Failed to select dropdown option by value '{value}' for {locator}: {str(e)}")
            self.take_screenshot("dropdown_select_failed")
            raise
        return self

    @retry_on_timeout()
    def select_dropdown_option_by_index(self, locator, index, timeout=None):
        """Selects an option from a dropdown by its index (0-based)."""
        log.info(f"Selecting dropdown option by index: {index} for locator: {locator}")
        try:
            element = self._wait_for_condition(locator, EC.visibility_of_element_located, timeout)
            select = Select(element)
            select.select_by_index(index)
            log.info(f"Selected option at index {index} successfully.")
        except Exception as e:
            log.error(f"Failed to select dropdown option by index {index} for {locator}: {str(e)}")
            self.take_screenshot("dropdown_select_failed")
            raise
        return self

    @retry_on_timeout()
    def get_dropdown_selected_option_text(self, locator, timeout=None):
        """Gets the text of the currently selected option in a dropdown."""
        log.info(f"Getting selected option text from dropdown: {locator}")
        try:
            element = self._wait_for_condition(locator, EC.visibility_of_element_located, timeout)
            select = Select(element)
            selected_text = select.first_selected_option.text
            log.info(f"Selected dropdown option text: ", {selected_text}, "")
            return selected_text
        except Exception as e:
            log.error(f"Failed to get selected dropdown text for {locator}: {str(e)}")
            return None

    @retry_on_timeout()
    def get_dropdown_options_texts(self, locator, timeout=None):
        """Gets the text of all options in a dropdown."""
        log.info(f"Getting all option texts from dropdown: {locator}")
        try:
            element = self._wait_for_condition(locator, EC.visibility_of_element_located, timeout)
            select = Select(element)
            options_texts = [option.text for option in select.options]
            log.info(f"Found {len(options_texts)} options in dropdown {locator}")
            return options_texts
        except Exception as e:
            log.error(f"Failed to get dropdown options texts for {locator}: {str(e)}")
            return []

    # --- ActionChains Methods ---

    @retry_on_timeout()
    def hover_over_element(self, locator, timeout=None):
        """Hovers the mouse cursor over an element."""
        log.info(f"Hovering over element: {locator}")
        try:
            element = self._wait_for_condition(locator, EC.visibility_of_element_located, timeout)
            self._highlight(element)
            actions = ActionChains(self.driver)
            actions.move_to_element(element).perform()
            log.info(f"Hovered over element {locator} successfully.")
            # Removed time.sleep(1) - wait for subsequent element if needed
        except Exception as e:
            log.error(f"Failed to hover over element {locator}: {str(e)}")
            self.take_screenshot("hover_failed")
            raise
        return self

    def _get_key(self, key_str_or_obj):
        """
        Convert a string like 'ENTER', 'ARROW_DOWN' to the corresponding selenium Keys constant.
        """
        if isinstance(key_str_or_obj, str):
            key_upper = key_str_or_obj.upper()
            if hasattr(Keys, key_upper):
                return getattr(Keys, key_upper)
            else:
                raise ValueError(
                    f"Invalid key string: '{key_str_or_obj}'. Must match Keys attributes like 'ENTER', 'TAB'.")
        return key_str_or_obj  # already a Keys constant

    def press_key(self, key, locator=None, timeout=None):
        try:
            key_obj = self._get_key(key)
            action = ActionChains(self.driver)

            if locator:
                element = self._wait_for_condition(locator, EC.visibility_of_element_located, timeout)
                action.send_keys_to_element(element, key_obj).perform()
            else:
                action.send_keys(key_obj).perform()
        except Exception as e:
            log.error(f"Failed to press key '{key}': {e}")
            raise

    def press_key_down(self, key, locator=None, timeout=None):
        """
        Press and hold any key, optionally on a specific element.

        :param key: Key as string (e.g., 'ENTER', 'ARROW_DOWN') or Keys.<key>
        :param locator: Optional Tuple(By.<method>, "locator")
        :param timeout: Optional max wait time for element
        """
        try:
            key_obj = self._get_key(key)
            action_chains = ActionChains(self.driver)

            if locator:
                log.info(f"Pressing key '{key}' down on element: {locator}")
                element = self._wait_for_condition(locator, EC.visibility_of_element_located, timeout)

                action_chains.key_down(key_obj, element).perform()
                log.info(f"Successfully pressed key '{key}' down on element: {locator}")
            else:
                log.info(f"Pressing key '{key}' down")
                action_chains.key_down(key_obj).perform()
                log.info(f"Successfully pressed key '{key}' down")
        except Exception as e:
            log.error(f"Failed to press key '{key}' down: {str(e)}")
            raise

    def press_key_up(self, key, locator=None, timeout=None):
        """
        Release any held key, optionally on a specific element.

        :param key: Key as string (e.g., 'ENTER', 'ARROW_DOWN') or Keys.<key>
        :param locator: Optional Tuple(By.<method>, "locator")
        :param timeout: Optional max wait time for element
        """
        try:
            key_obj = self._get_key(key)
            action_chains = ActionChains(self.driver)

            if locator:
                log.info(f"Releasing key '{key}' on element: {locator}")
                element = self._wait_for_condition(locator, EC.visibility_of_element_located, timeout)
                action_chains.key_up(key_obj, element).perform()
                log.info(f"Successfully released key '{key}' on element: {locator}")
            else:
                log.info(f"Releasing key '{key}'")
                action_chains.key_up(key_obj).perform()
                log.info(f"Successfully released key '{key}'")
        except Exception as e:
            log.error(f"Failed to release key '{key}': {str(e)}")
            raise



    def double_click(self, locator, timeout=None):
        """Double-clicks on an element."""
        log.info(f"Double-clicking element: {locator}")
        try:
            element = self._wait_for_condition(locator, EC.element_to_be_clickable, timeout)
            self._highlight(element)
            actions = ActionChains(self.driver)
            actions.double_click(element).perform()
            log.info(f"Double-clicked element {locator} successfully.")
        except Exception as e:
            log.error(f"Failed to double-click element {locator}: {str(e)}")
            self.take_screenshot("double_click_failed")
            raise
        return self


    def right_click(self, locator, timeout=None):
        """Right-clicks (context clicks) on an element."""
        log.info(f"Right-clicking element: {locator}")
        try:
            element = self._wait_for_condition(locator, EC.element_to_be_clickable, timeout)
            self._highlight(element)
            actions = ActionChains(self.driver)
            actions.context_click(element).perform()
            log.info(f"Right-clicked element {locator} successfully.")
        except Exception as e:
            log.error(f"Failed to right-click element {locator}: {str(e)}")
            self.take_screenshot("right_click_failed")
            raise
        return self


    def drag_and_drop(self, source_locator, target_locator, timeout=None):
        """Drags an element from the source locator and drops it onto the target locator."""
        log.info(f"Dragging element {source_locator} to {target_locator}")
        try:
            source_element = self._wait_for_condition(source_locator, EC.visibility_of_element_located, timeout)
            target_element = self._wait_for_condition(target_locator, EC.visibility_of_element_located, timeout)
            self._highlight(source_element)
            self._highlight(target_element)
            actions = ActionChains(self.driver)
            actions.drag_and_drop(source_element, target_element).perform()
            log.info(f"Dragged {source_locator} to {target_locator} successfully.")
        except Exception as e:
            log.error(f"Failed to drag and drop from {source_locator} to {target_locator}: {str(e)}")
            self.take_screenshot("drag_drop_failed")
            raise
        return self

    # --- Scrolling Methods ---

    def scroll_to_element(self, locator, align_to_top=True, timeout=None):
        """
        Scrolls the page until the element is in view.

        Args:
            locator (tuple): Locator tuple (By, value)
            align_to_top (bool): If True (default), aligns element to the top of the viewport.
                               If False, aligns to the bottom.
            timeout (int, optional): Specific timeout for this wait.
        """
        log.info(f"Scrolling to element: {locator} (align_to_top={align_to_top})")
        try:
            element = self._wait_for_condition(locator, EC.presence_of_element_located, timeout)
            # Use scrollIntoView with boolean argument
            self.execute_script("arguments[0].scrollIntoView(arguments[1]);", element, align_to_top)
            # Alternative: scrollIntoView({block: "start"/"end"})
            # block_arg = "start" if align_to_top else "end"
            # self.execute_script(f"arguments[0].scrollIntoView({{block: \"{block_arg}\", behavior: \"smooth\"}});", element)
            self._highlight(element)
            log.info(f"Scrolled to element {locator} successfully.")
        except Exception as e:
            log.error(f"Failed to scroll to element {locator}: {str(e)}")
            self.take_screenshot("scroll_to_element_failed")
            raise
        return self

    def scroll_to_element_by_location(self, locator, timeout=None):
        """
        Scroll automatically to a specific element based on its position on the page.
        :param locator: Tuple(By.<method>, "locator")
        :param timeout: Max time to wait for element
        """
        try:
            log.info(f"Waiting for element to be present with locator: {locator}")
            element = self._wait_for_condition(locator, EC.presence_of_element_located, timeout)

            element_location = element.location
            element_y = element_location['y']
            element_x = element_location['x']

            current_scroll_y = self.driver.execute_script("return window.pageYOffset;")
            current_scroll_x = self.driver.execute_script("return window.pageXOffset;")

            log.info(f"Element location (X: {element_x}, Y: {element_y})")
            log.info(f"Current scroll position (X: {current_scroll_x}, Y: {current_scroll_y})")

            # Decide vertical scroll
            if element_y > current_scroll_y:
                log.info("Scrolling down to the element")
            elif element_y < current_scroll_y:
                log.info("Scrolling up to the element")

            # Decide horizontal scroll
            if element_x > current_scroll_x:
                log.info("Scrolling right to the element")
            elif element_x < current_scroll_x:
                log.info("Scrolling left to the element")
            # Final scroll into view
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'center'});", element)
            log.info(f"Successfully scrolled to element with locator: {locator}")

        except Exception as e:
            log.error(f"Failed to scroll to element with locator: {locator}. Exception: {str(e)}")
            self.take_screenshot("scroll_to_element_failed")
            raise
        return self

    def scroll_page(self, direction="down", pixels=None):
        """
        Scrolls the page window.

        Args:
            direction (str): "up", "down", "top", "bottom". Defaults to "down".
            pixels (int, optional): Number of pixels to scroll by (for "up"/"down").
                                   If None, scrolls by one viewport height.
        """
        log.info(f"Scrolling page {direction}", f" by {pixels}px" if pixels else "")
        try:
            if direction == "down":
                scroll_amount = pixels if pixels is not None else self.driver.get_window_size()["height"]
                self.execute_script(f"window.scrollBy(0, {scroll_amount});")
            elif direction == "up":
                scroll_amount = pixels if pixels is not None else self.driver.get_window_size()["height"]
                self.execute_script(f"window.scrollBy(0, -{scroll_amount});")
            elif direction == "bottom":
                self.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            elif direction == "top":
                self.execute_script("window.scrollTo(0, 0);")
            else:
                log.warning(f"Invalid scroll direction: {direction}")
                return self
            log.info(f"Scrolled page {direction} successfully.")
            time.sleep(0.5)  # Small pause to allow rendering after scroll
        except Exception as e:
            log.error(f"Failed to scroll page {direction}: {str(e)}")
            # No screenshot here as it might not be a critical failure
        return self

    # --- Alert, Frame, Window Handling ---
    # (Keeping original methods, adding minor logging/error handling improvements if needed)
    # Note: Corrected frame switching logic

    def wait_for_alert(self, timeout=None):
        """Waits for an alert to be present and returns it."""
        timeout = timeout if timeout is not None else self.explicit_wait_timeout
        log.info(f"Waiting for alert ({timeout}s)")
        try:
            alert = WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
            log.info("Alert is present")
            return alert
        except TimeoutException:
            log.error(f"TimeoutException: No alert appeared within {timeout} seconds")
            self.take_screenshot("alert_timeout")
            raise

    def accept_alert(self, timeout=None):
        """Accepts (clicks OK) on an alert."""
        log.info("Accepting alert")
        try:
            alert = self.wait_for_alert(timeout)
            alert_text = alert.text  # Get text before accepting
            log.info(f"Alert text: {alert_text}")
            alert.accept()
            log.info("Alert accepted successfully")
        except Exception as e:
            log.error(f"Failed to accept alert: {str(e)}")
            raise
        return self

    def dismiss_alert(self, timeout=None):
        """Dismisses (clicks Cancel) on an alert."""
        log.info("Dismissing alert")
        try:
            alert = self.wait_for_alert(timeout)
            alert_text = alert.text  # Get text before dismissing
            log.info(f"Alert text: {alert_text}")
            alert.dismiss()
            log.info("Alert dismissed successfully")
        except Exception as e:
            log.error(f"Failed to dismiss alert: {str(e)}")
            raise
        return self

    def get_alert_text(self, timeout=None):
        """Gets the text from an alert."""
        log.info("Getting alert text")
        try:
            alert = self.wait_for_alert(timeout)
            text = alert.text
            log.info(f"Alert text: {text}")
            return text
        except Exception as e:
            log.error(f"Failed to get alert text: {str(e)}")
            raise

    def send_text_to_alert(self, text, timeout=None):
        """Sends text to an alert prompt."""
        log.info(f"Sending text '{text}' to alert")
        try:
            alert = self.wait_for_alert(timeout)
            alert.send_keys(text)
            log.info(f"Sent text '{text}' to alert successfully.")
            # Usually followed by alert.accept() or alert.dismiss()
        except Exception as e:
            log.error(f"Failed to send text to alert: {str(e)}")
            raise
        return self

    def switch_to_frame(self, frame_reference, timeout=None):
        """
        Switches to a frame using index, name, ID, locator, or WebElement.

        Args:
            frame_reference: Index (int), Name/ID (str), Locator (tuple), or WebElement.
            timeout (int, optional): Specific timeout for this wait.
        """
        timeout = timeout if timeout is not None else self.explicit_wait_timeout
        log.info(f"Switching to frame using reference: {frame_reference}")
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.frame_to_be_available_and_switch_to_it(frame_reference)
            )
            log.info(f"Switched to frame {frame_reference} successfully.")
        except TimeoutException:
            log.error(f"TimeoutException: Frame {frame_reference} not available or could not switch within {timeout}s.")
            self.take_screenshot("frame_switch_timeout")
            raise
        except Exception as e:
            log.error(f"Failed to switch to frame {frame_reference}: {str(e)}")
            self.take_screenshot("frame_switch_failed")
            raise
        return self

    def switch_to_default_content(self):
        """Switches back to the main document from a frame."""
        log.info("Switching to default content")
        try:
            self.driver.switch_to.default_content()
            log.info("Switched to default content successfully.")
        except Exception as e:
            log.error(f"Failed to switch to default content: {str(e)}")
            # May not be in a frame
        return self

    def switch_to_parent_frame(self):
        """Switches to the parent frame from a nested frame."""
        log.info("Switching to parent frame")
        try:
            self.driver.switch_to.parent_frame()
            log.info("Switched to parent frame successfully.")
        except Exception as e:
            log.error(f"Failed to switch to parent frame: {str(e)}")
            # May already be at top level or default content
        return self

    def get_window_handles(self):
        """Gets handles of all currently open windows/tabs."""
        try:
            handles = self.driver.window_handles
            log.info(f"Found {len(handles)} window handles: {handles}")
            return handles
        except Exception as e:
            log.error(f"Failed to get window handles: {str(e)}")
            return []

    def get_current_window_handle(self):
        """Gets the handle of the currently focused window/tab."""
        try:
            handle = self.driver.current_window_handle
            log.info(f"Current window handle: {handle}")
            return handle
        except Exception as e:
            log.error(f"Failed to get current window handle: {str(e)}")
            return None

    def switch_to_window_by_handle(self, handle):
        """Switches focus to the window/tab with the given handle."""
        log.info(f"Switching to window with handle: {handle}")
        try:
            self.driver.switch_to.window(handle)
            log.info(f"Switched to window {handle} successfully.")
        except Exception as e:
            log.error(f"Failed to switch to window {handle}: {str(e)}")
            raise
        return self

    def switch_to_window_by_index(self, index):
        """Switches focus to a window/tab by its index (0-based)."""
        log.info(f"Switching to window with index: {index}")
        try:
            handles = self.get_window_handles()
            if 0 <= index < len(handles):
                self.switch_to_window_by_handle(handles[index])
            else:
                raise IndexError(f"Invalid window index: {index}, total windows: {len(handles)}")
        except Exception as e:
            log.error(f"Failed to switch to window index {index}: {str(e)}")
            raise
        return self

    def switch_to_new_window_after_action(self, action_func, timeout=None):
        """
        Performs an action that opens a new window/tab and switches to it.

        Args:
            action_func (callable): The function/method that triggers the new window.
            timeout (int, optional): Max time to wait for the new window.
        Ex: self.switch_to_new_window_after_action(lambda: self.click(self.locators.switchWindows))
        """
        timeout = timeout if timeout is not None else self.explicit_wait_timeout
        log.info("Performing action and waiting for new window...")
        original_handles = set(self.get_window_handles())
        try:
            action_func()  # Execute the action that opens the new window

            # Wait for the new window handle
            WebDriverWait(self.driver, timeout).until(
                lambda driver: set(driver.window_handles) - original_handles
            )

            new_handles = set(self.get_window_handles()) - original_handles
            if new_handles:
                new_handle = list(new_handles)[0]
                log.info(f"New window detected: {new_handle}. Switching...")
                self.switch_to_window_by_handle(new_handle)
            else:
                # This part should ideally not be reached if WebDriverWait worked
                raise TimeoutException(f"No new window appeared within {timeout}s after action.")
        except TimeoutException:
            log.error(f"TimeoutException: No new window appeared within {timeout}s after action.")
            self.take_screenshot("new_window_timeout")
            raise
        except Exception as e:
            log.error(f"Error during action or switching to new window: {str(e)}")
            self.take_screenshot("new_window_failed")
            raise
        return self

    def close_current_window_and_switch_back(self, original_handle=None):
        """
        Closes the current window/tab and switches back to the original one,
        or the first remaining if not provided.
        """
        log.info("Closing current window...")
        current_handle = self.get_current_window_handle()
        try:
            self.driver.close()
            log.info(f"Closed window: {current_handle}")
            remaining_handles = self.get_window_handles()

            if not remaining_handles:
                log.warning("No windows remain open.")
                return self

            target_handle = (
                original_handle if original_handle in remaining_handles else remaining_handles[0]
            )
            log.info(f"Switching back to window: {target_handle}")
            self.switch_to_window_by_handle(target_handle)

        except Exception as e:
            log.error(f"Error closing current window or switching back: {str(e)}")
        return self

    def open_new_tab_and_switch(self):
        """Opens a new tab and switches to it."""
        log.info("Opening a new tab...")
        try:
            self.driver.switch_to.new_window('tab')
            new_handle = self.get_current_window_handle()
            log.info(f"Switched to new tab with handle: {new_handle}")
        except Exception as e:
            log.error(f"Failed to open and switch to new tab: {str(e)}")
            raise
        return self

    def open_new_window_and_switch(self):
        """Opens a new window and switches to it."""
        log.info("Opening a new window...")
        try:
            self.driver.switch_to.new_window('window')
            new_handle = self.get_current_window_handle()
            log.info(f"Switched to new window with handle: {new_handle}")
        except Exception as e:
            log.error(f"Failed to open and switch to new window: {str(e)}")
            raise
        return self

    def switch_to_non_original_window(self, original_handle):
        """
        Switches to a window/tab that is not the original one.
        Useful after opening a new tab/window.
        """
        try:
            handles = self.get_window_handles()
            for handle in handles:
                if handle != original_handle:
                    self.switch_to_window_by_handle(handle)
                    log.info(f"Switched to new window/tab: {handle}")
                    return self
            log.warning("No other window/tab found to switch.")
        except Exception as e:
            log.error(f"Failed to switch to non-original window: {str(e)}")
            raise
        return self

    # --- Browser/Page Information ---

    def get_title(self):
        """Gets the title of the current page."""
        try:
            title = self.driver.title
            log.info(f"Current page title: ", {title}, "")
            return title
        except Exception as e:
            log.error(f"Failed to get page title: {str(e)}")
            return None

    def get_url(self):
        """Gets the current URL of the page."""
        try:
            url = self.driver.current_url
            log.info(f"Current page URL: {url}")
            return url
        except Exception as e:
            log.error(f"Failed to get current URL: {str(e)}")
            return None

    def refresh_page(self):
        """Refreshes the current page."""
        log.info("Refreshing the current page")
        try:
            self.driver.refresh()
            self.wait_for_page_load_complete()  # Wait after refresh
            log.info("Page refreshed successfully.")
        except Exception as e:
            log.error(f"Failed to refresh page: {str(e)}")
            self.take_screenshot("refresh_failed")
            raise
        return self

    def navigate_back(self):
        """Navigates back in the browser history."""
        log.info("Navigating back in browser history")
        try:
            self.driver.back()
            self.wait_for_page_load_complete()  # Wait after navigation
            log.info("Navigated back successfully.")
        except Exception as e:
            log.error(f"Failed to navigate back: {str(e)}")
            self.take_screenshot("navigate_back_failed")
            raise
        return self

    def navigate_forward(self):
        """Navigates forward in the browser history."""
        log.info("Navigating forward in browser history")
        try:
            self.driver.forward()
            self.wait_for_page_load_complete()  # Wait after navigation
            log.info("Navigated forward successfully.")
        except Exception as e:
            log.error(f"Failed to navigate forward: {str(e)}")
            self.take_screenshot("navigate_forward_failed")
            raise
        return self

    # --- JavaScript Execution ---

    def execute_script(self, script, *args):
        """
        Executes JavaScript in the context of the currently selected frame or window.

        Args:
            script (str): The JavaScript code to execute.
            *args: Arguments to pass to the script. These will be available as arguments[0], arguments[1], etc.

        Returns:
            Any: The value returned by the script.
        """
        log.debug(f"Executing JavaScript: {script[:100]}...", f" with args: {args}" if args else "")
        try:
            result = self.driver.execute_script(script, *args)
            log.debug("JavaScript execution completed.")
            return result
        except Exception as e:
            log.error(f"Failed to execute JavaScript: {str(e)}")
            self.take_screenshot("javascript_error")
            raise

    def execute_async_script(self, script, *args):
        """
        Executes asynchronous JavaScript in the context of the currently selected frame or window.

        Args:
            script (str): The asynchronous JavaScript code to execute. Must call the callback (arguments[len(args)-1]) to signal completion.
            *args: Arguments to pass to the script.

        Returns:
            Any: The value passed to the callback in the script.
        """
        log.debug(f"Executing async JavaScript: {script[:100]}...", f" with args: {args}" if args else "")
        try:
            result = self.driver.execute_async_script(script, *args)
            log.debug("Async JavaScript execution completed.")
            return result
        except Exception as e:
            log.error(f"Failed to execute async JavaScript: {str(e)}")
            self.take_screenshot("async_javascript_error")
            raise

    # --- Cookies ---

    def get_cookies(self):
        """Gets all cookies visible to the current page."""
        log.info("Getting all cookies")
        try:
            cookies = self.driver.get_cookies()
            log.info(f"Retrieved {len(cookies)} cookies.")
            return cookies
        except Exception as e:
            log.error(f"Failed to get cookies: {str(e)}")
            return []

    def get_cookie(self, name):
        """Gets a single cookie by name."""
        log.info(f"Getting cookie: {name}")
        try:
            cookie = self.driver.get_cookie(name)
            log.info(f"Retrieved cookie ", {name}, f": {cookie}")
            return cookie
        except Exception as e:
            log.error(f"Failed to get cookie ", {name}, f": {str(e)}")
            return None

    def add_cookie(self, cookie_dict):
        """
        Adds a single cookie to the current session.

        Args:
            cookie_dict (dict): A dictionary specifying the cookie properties (e.g., {"name": "foo", "value": "bar"}).
        """
        log.info(f"Adding cookie: {cookie_dict.get("name")}")
        try:
            self.driver.add_cookie(cookie_dict)
            log.info(f"Added cookie ", {cookie_dict.get("name")}, f" successfully.")
        except Exception as e:
            log.error(f"Failed to add cookie ", {cookie_dict.get("name")}, f": {str(e)}")
            raise
        return self

    def delete_cookie(self, name):
        """Deletes a single cookie by name."""
        log.info(f"Deleting cookie: {name}")
        try:
            self.driver.delete_cookie(name)
            log.info(f"Deleted cookie ", {name}, f" successfully.")
        except Exception as e:
            log.error(f"Failed to delete cookie ", {name}, f": {str(e)}")
            # Don"t raise, maybe cookie didn"t exist
        return self

    def delete_all_cookies(self):
        """Deletes all cookies for the current session."""
        log.info("Deleting all cookies")
        try:
            self.driver.delete_all_cookies()
            log.info("Deleted all cookies successfully.")
        except Exception as e:
            log.error(f"Failed to delete all cookies: {str(e)}")
            raise
        return self

    # --- File Upload ---


    def upload_file(self, locator, file_path, timeout=None):
        """
        Uploads a file using an input element (type="file").

        Args:
            locator (tuple): Locator for the input[type="file"] element.
            file_path (str): Absolute path to the file to upload.
            timeout (int, optional): Specific timeout for this wait.
        """
        log.info(f"Uploading file ", {file_path}, f" to element: {locator}")
        if not os.path.isabs(file_path):
            log.error(f"File path must be absolute: {file_path}")
            raise ValueError(f"File path must be absolute: {file_path}")
        if not os.path.exists(file_path):
            log.error(f"File not found at path: {file_path}")
            raise FileNotFoundError(f"File not found at path: {file_path}")

        try:
            # Input elements of type file are often not visible, wait for presence
            element = self._wait_for_condition(locator, EC.presence_of_element_located, timeout)
            element.send_keys(file_path)
            log.info(f"Sent file path ", {file_path}, f" to element {locator} successfully.")
        except Exception as e:
            log.error(f"Failed to upload file ", {file_path}, f" to element {locator}: {str(e)}")
            self.take_screenshot("upload_file_failed")
            raise
        return self

    # --- Utility Methods ---

    def take_screenshot(self, name_prefix="screenshot"):
        """
        Takes a screenshot and saves it to the configured directory with a timestamp.

        Args:
            name_prefix (str): Prefix for the screenshot filename.

        Returns:
            str: The full path to the saved screenshot file, or None if failed.
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        file_name = f"{name_prefix}_{timestamp}.png"
        file_path = os.path.join(self.screenshots_dir, file_name)
        log.info(f"Taking screenshot: {file_path}")
        try:
            if self.driver.save_screenshot(file_path):
                log.info(f"Screenshot saved successfully: {file_path}")
                return file_path
            else:
                log.error(f"Failed to save screenshot to {file_path} (driver returned false)")
                return None
        except Exception as e:
            log.error(f"Failed to take screenshot: {str(e)}")
            return None


    def get_element_size(self, locator, timeout=None):
        """Gets the size (width, height) of an element."""
        log.info(f"Getting size of element: {locator}")
        try:
            element = self._wait_for_condition(locator, EC.visibility_of_element_located, timeout)
            size = element.size
            log.info(f"Element {locator} size: {size}")
            return size  # Returns dict {"width": W, "height": H}
        except Exception as e:
            log.error(f"Failed to get size of element {locator}: {str(e)}")
            return None


    def get_element_location(self, locator, timeout=None):
        """Gets the location (x, y coordinates) of an element relative to the top-left corner of the page."""
        log.info(f"Getting location of element: {locator}")
        try:
            element = self._wait_for_condition(locator, EC.visibility_of_element_located, timeout)
            location = element.location
            log.info(f"Element {locator} location: {location}")
            return location  # Returns dict {"x": X, "y": Y}
        except Exception as e:
            log.error(f"Failed to get location of element {locator}: {str(e)}")
            return None


    def find_and_click_element_by_text(self, locator, text_to_match, exact_match=True, timeout=None):
        """
        Finds elements matching the locator and clicks the one whose text matches.
        Improved version of find_all_elements_click_based_on_text.
        """
        log.info(f"Finding elements with locator {locator} and clicking based on text: {text_to_match}")
        try:
            log.info(f"Finding all elements with locator: {locator}")
            elements = self.find_elements(locator, timeout)
            log.info(f"Found {len(elements)} potential elements.")

            clicked = False
            for element in elements:
                try:
                    element_text = element.text.strip()
                    if not element_text:
                        element_text = element.get_attribute("innerText").strip()
                    if not element_text:
                        element_text = element.get_attribute("value").strip()

                    log.debug(f"Checking element text: {element_text}")
                    match = (exact_match and element_text == text_to_match) or \
                            (not exact_match and text_to_match in element_text)

                    if match:
                        log.info(f"Match found. Clicking element with text: {element_text}")
                        self._highlight(element)
                        element.click()
                        clicked = True
                        break
                except StaleElementReferenceException:
                    log.warning("Element became stale while checking text, continuing search...")
                    continue
                except Exception as check_err:
                    log.warning(f"Error checking or clicking element: {check_err}")
                    continue

            if not clicked:
                error_msg = f"No element found with locator {locator} and matching text '{text_to_match}'"
                log.error(error_msg)
                self.take_screenshot("click_by_text_failed")
                raise NoSuchElementException(error_msg)

        except TimeoutException:
            error_msg = f"Timeout: No elements found with locator {locator} within timeout."
            log.error(error_msg)
            self.take_screenshot("click_by_text_timeout")
            raise NoSuchElementException(error_msg)
        except Exception as e:
            log.error(f"Error finding/clicking element by text '{text_to_match}': {str(e)}")
            self.take_screenshot("click_by_text_error")
            raise
        return self

    def verifyTextMatch(self, actualText, expectedText):
        """
        Verify text match

        :param actualText: Actual Text
        :param expectedText: Expected Text
        """
        log.info("Actual Text From Application Web UI --> :: " + actualText)
        log.info("Expected Text From Application Web UI --> :: " + expectedText)
        if expectedText.lower() == actualText.lower():
            log.info("### VERIFICATIONS MATCHED !!!")
            return True
        else:
            log.error("### VERIFICATIONS DID NOT MATCH !!!")
            assert False, f"Text mismatch: Expected '{expectedText}', but got '{actualText}'"

    def verifyPageTitle(self, titleToVerify):
        """
        Verify the page Title

        :param titleToVerify: Title on the page that needs to be verified
        """
        try:
            actualTitle = self.get_title()
            return self.verifyTextMatch(actualTitle, titleToVerify)
        except Exception as e:
            log.error(f"Failed to get page title: {e}")
            assert False, f"Failed to get page title or mismatch with expected '{titleToVerify}'"

    #To support Static and Dynamic Web Tables effectively in your framework without hardcoding XPath or column/row indexes
    def get_table_headers(self, table_locator,header_locator):
        """Returns the header titles as a list from the table."""
        headers = []
        element = self._wait_for_condition(table_locator, EC.visibility_of_element_located)
        header_elements = element.find_elements(*header_locator)
        for header in header_elements:
            headers.append(header.text.strip())
        return headers

    def get_table_data(self, table_locator, header_locator, row_locator, cell_locator):
        """
        Returns all table data as a list of dictionaries (header: value).

        Args:
            table_locator (tuple): Locator for the <table> element.
            header_locator (tuple): Locator for header cells (th).
            row_locator (tuple): Locator for all table rows (tr).
            cell_locator (tuple): Locator for all cells within a row (td).

        Returns:
            list[dict]: List of row dictionaries with header: value mapping.
        """
        table = self._wait_for_condition(table_locator, EC.visibility_of_element_located)

        headers = [header.text.strip() for header in table.find_elements(*header_locator)]
        rows = table.find_elements(*row_locator)
        data = []

        for row in rows:
            cells = row.find_elements(*cell_locator)
            row_data = {
                headers[i]: cells[i].text.strip() if i < len(cells) else ""
                for i in range(len(headers))
            }
            data.append(row_data)

        return data

    def get_row_by_column_value(self, table_locator,header_locator, row_locator, cell_locator, column_name, value):
        """
        Returns the first row where the given column matches the specified value.
        """
        matching_rows = []
        all_rows = self.get_table_data(table_locator,header_locator, row_locator, cell_locator)
        for row in all_rows:
            if row.get(column_name) == value:
                matching_rows.append(row)

        return matching_rows

    def get_cell_text(self,table_locator,header_locator, row_locator, cell_locator, row_index, column_name):
        """
        Returns text of a cell based on row index and column header.
        Row index is 0-based.
        """
        data = self.get_table_data(table_locator, header_locator, row_locator, cell_locator)
        if 0 <= row_index < len(data):
            return data[row_index].get(column_name)
        return None

    def get_column_values_sum(self, table_locator, header_locator, row_locator, cell_locator, column_name):
        """
        Returns the sum of all numeric values in a specified column of the table.

        Args:
            table_locator (tuple): Locator for the table.
            header_locator (tuple): Locator for header elements (relative to table).
            row_locator (tuple): Locator for row elements (relative to table).
            cell_locator (tuple): Locator for cell elements (relative to row).
            column_name (str): Name of the column to sum values from.

        Returns:
            float: Sum of the values in the column.
        """
        table = self._wait_for_condition(table_locator, EC.visibility_of_element_located)
        headers = [th.text.strip() for th in table.find_elements(*header_locator)]
        rows = table.find_elements(*row_locator)

        total = 0
        for row in rows:
            cells = row.find_elements(*cell_locator)
            if len(cells) != len(headers):
                continue  # Skip malformed rows
            row_data = dict(zip(headers, [cell.text.strip() for cell in cells]))
            value = row_data.get(column_name, "").replace("$", "").strip()
            if value.isdigit():
                total += int(value)
            else:
                try:
                    total += float(value)
                except ValueError:
                    continue  # Skip non-numeric values

        return total