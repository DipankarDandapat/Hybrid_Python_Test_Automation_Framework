"""
Mobile Base Page Module.

This module provides a base page class for mobile automation with common mobile interactions.
It supports both Android and iOS platforms and integrates with the Appium Python client.
"""
import os
import time
from functools import wraps
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    ElementNotVisibleException,
    ElementNotInteractableException,
    WebDriverException
)

from src.utils import logger
log = logger.customLogger()

# --- Retry Decorator ---
def retry_on_timeout(retries=1, delay=5):
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

class MobileBasePage:
    """Base Page class for mobile automation with common mobile interactions."""

    def __init__(self, driver):
        """Initialize MobileBasePage with driver and configuration."""
        self.driver = driver
        self.platform = os.getenv('PLATFORM', 'android').lower()
        self.explicit_wait_timeout = int(os.getenv('EXPLICIT_WAIT', '20'))
        self.screenshots_dir = os.getenv('SCREENSHOTS_DIR', 'reports/screenshots')
        os.makedirs(self.screenshots_dir, exist_ok=True)
        log.info(f"Initialized MobileBasePage for platform: {self.platform}")

    # --- Private Helper Methods ---

    def _wait_for_condition(self, locator, condition, timeout=None, message=""):
        """
        Internal helper to wait for a specific expected condition on an element.
        Handles TimeoutException and logs appropriately.

        Args:
            locator (tuple): Locator tuple (AppiumBy, value)
            condition (callable): Expected condition function from selenium.webdriver.support.expected_conditions
            timeout (int, optional): Specific timeout for this wait. Defaults to self.explicit_wait_timeout.
            message (str, optional): Custom message for TimeoutException.

        Returns:
            WebElement or list[WebElement] or bool: Result from the condition.

        Raises:
            TimeoutException: If the condition is not met within the timeout.
        """
        timeout = timeout if timeout is not None else self.explicit_wait_timeout
        wait = WebDriverWait(
            self.driver, 
            timeout,
            ignored_exceptions=[
                NoSuchElementException, 
                ElementNotVisibleException,
                StaleElementReferenceException
            ]
        )
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
        """
        try:
            original_style = element.get_attribute("style")
            highlight_style = f"border: {border}px solid {color};"
            self.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, highlight_style)
            time.sleep(effect_time)
            self.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, original_style)
        except WebDriverException:
            log.warning("Could not highlight element, possibly due to page refresh or element becoming stale.")

    # --- Core Element Interaction Methods ---

    @retry_on_timeout()
    def find_element(self, locator, timeout=None):
        """
        Find a single element using the specified locator and wait condition.

        Args:
            locator (tuple): Locator tuple (AppiumBy, value)
            timeout (int, optional): Specific timeout for this wait. Defaults to self.explicit_wait_timeout.

        Returns:
            WebElement: Found element

        Raises:
            TimeoutException: If element is not found within the timeout.
        """
        return self._wait_for_condition(locator, EC.presence_of_element_located, timeout)

    @retry_on_timeout()
    def find_elements(self, locator, timeout=None):
        """
        Find multiple elements using the specified locator.

        Args:
            locator (tuple): Locator tuple (AppiumBy, value)
            timeout (int, optional): Specific timeout for this wait. Defaults to self.explicit_wait_timeout.

        Returns:
            list[WebElement]: List of found elements

        Raises:
            TimeoutException: If no elements are found within the timeout.
        """
        return self._wait_for_condition(locator, EC.presence_of_all_elements_located, timeout)

    @retry_on_timeout()
    def wait_for_visibility(self, locator, timeout=None):
        """
        Wait for element to be visible.

        Args:
            locator (tuple): Locator tuple (AppiumBy, value)
            timeout (int, optional): Specific timeout for this wait. Defaults to self.explicit_wait_timeout.

        Returns:
            WebElement: Visible element

        Raises:
            TimeoutException: If element is not visible within the timeout.
        """
        return self._wait_for_condition(locator, EC.visibility_of_element_located, timeout)

    @retry_on_timeout()
    def wait_for_clickable(self, locator, timeout=None):
        """
        Wait for element to be clickable.

        Args:
            locator (tuple): Locator tuple (AppiumBy, value)
            timeout (int, optional): Specific timeout for this wait. Defaults to self.explicit_wait_timeout.

        Returns:
            WebElement: Clickable element

        Raises:
            TimeoutException: If element is not clickable within the timeout.
        """
        return self._wait_for_condition(locator, EC.element_to_be_clickable, timeout)

    def is_element_present(self, locator, timeout=5):
        """
        Check if element is present.

        Args:
            locator (tuple): Locator tuple (AppiumBy, value)
            timeout (int, optional): Specific timeout for this wait. Defaults to 5 seconds.

        Returns:
            bool: True if element is present, False otherwise.
        """
        try:
            self.find_element(locator, timeout)
            return True
        except TimeoutException:
            return False

    def is_element_visible(self, locator, timeout=5):
        """
        Check if element is visible.

        Args:
            locator (tuple): Locator tuple (AppiumBy, value)
            timeout (int, optional): Specific timeout for this wait. Defaults to 5 seconds.

        Returns:
            bool: True if element is visible, False otherwise.
        """
        try:
            self.wait_for_visibility(locator, timeout)
            return True
        except TimeoutException:
            return False

    def get_element_text(self, locator, timeout=None):
        """
        Get element text.

        Args:
            locator (tuple): Locator tuple (AppiumBy, value)
            timeout (int, optional): Specific timeout for this wait. Defaults to self.explicit_wait_timeout.

        Returns:
            str: Element text

        Raises:
            TimeoutException: If element is not found within the timeout.
        """
        element = self.find_element(locator, timeout)
        return element.text

    def get_element_attribute(self, locator, attribute, timeout=None):
        """
        Get element attribute.

        Args:
            locator (tuple): Locator tuple (AppiumBy, value)
            attribute (str): Attribute name
            timeout (int, optional): Specific timeout for this wait. Defaults to self.explicit_wait_timeout.

        Returns:
            str: Attribute value

        Raises:
            TimeoutException: If element is not found within the timeout.
        """
        element = self.find_element(locator, timeout)
        return element.get_attribute(attribute)

    # --- Mobile-Specific Interaction Methods ---

    def tap(self, locator, timeout=None):
        """
        Tap on element.

        Args:
            locator (tuple): Locator tuple (AppiumBy, value)
            timeout (int, optional): Specific timeout for this wait. Defaults to self.explicit_wait_timeout.

        Raises:
            TimeoutException: If element is not clickable within the timeout.
        """
        element = self.wait_for_clickable(locator, timeout)
        element.click()
        log.info(f"Tapped on element: {locator}")

    def tap_by_coordinates(self, x, y):
        """
        Tap by coordinates.

        Args:
            x (int): X coordinate
            y (int): Y coordinate
        """
        actions = self.driver.action()
        actions.tap_point(x=x, y=y).perform()
        log.info(f"Tapped at coordinates: ({x}, {y})")

    def input_text(self, locator, text, timeout=None, clear_first=True):
        """
        Input text into element.

        Args:
            locator (tuple): Locator tuple (AppiumBy, value)
            text (str): Text to input
            timeout (int, optional): Specific timeout for this wait. Defaults to self.explicit_wait_timeout.
            clear_first (bool, optional): Whether to clear field before input. Defaults to True.

        Raises:
            TimeoutException: If element is not found within the timeout.
        """
        element = self.find_element(locator, timeout)
        if clear_first:
            element.clear()
        element.send_keys(text)
        log.info(f"Input text '{text}' into element: {locator}")

    def swipe(self, start_x, start_y, end_x, end_y, duration=None):
        """
        Swipe from one point to another.

        Args:
            start_x (int): Starting X coordinate
            start_y (int): Starting Y coordinate
            end_x (int): Ending X coordinate
            end_y (int): Ending Y coordinate
            duration (int, optional): Swipe duration in milliseconds. Defaults to None.
        """
        actions = self.driver.action()
        actions.pointer_action.move_to_location(start_x, start_y)
        actions.pointer_action.pointer_down()
        actions.pointer_action.pause(duration if duration else 500)
        actions.pointer_action.move_to_location(end_x, end_y)
        actions.pointer_action.release()
        actions.perform()
        log.info(f"Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y})")

    def scroll_down(self):
        """
        Scroll down on the screen.
        """
        size = self.driver.get_window_size()
        start_x = size['width'] // 2
        start_y = size['height'] * 0.8
        end_x = start_x
        end_y = size['height'] * 0.2
        self.swipe(start_x, start_y, end_x, end_y)
        log.info("Scrolled down")

    def scroll_up(self):
        """
        Scroll up on the screen.
        """
        size = self.driver.get_window_size()
        start_x = size['width'] // 2
        start_y = size['height'] * 0.2
        end_x = start_x
        end_y = size['height'] * 0.8
        self.swipe(start_x, start_y, end_x, end_y)
        log.info("Scrolled up")

    def scroll_to_text(self, text):
        """
        Scroll to element with text.

        Args:
            text (str): Text to scroll to
        """
        if self.platform == 'android':
            self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 
                                    f'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(new UiSelector().text("{text}"))')
        elif self.platform == 'ios':
            # iOS doesn't have a direct method like Android
            # We'll need to implement a custom scroll logic
            max_swipes = 10
            for _ in range(max_swipes):
                page_source = self.driver.page_source
                if text in page_source:
                    break
                self.scroll_down()
        log.info(f"Scrolled to text: {text}")

    def long_press(self, locator, duration=1000):
        """
        Long press on element.

        Args:
            locator (tuple): Locator tuple (AppiumBy, value)
            duration (int, optional): Press duration in milliseconds. Defaults to 1000.

        Raises:
            TimeoutException: If element is not found within the timeout.
        """
        element = self.find_element(locator)
        actions = self.driver.action()
        actions.pointer_action.move_to(element)
        actions.pointer_action.pointer_down()
        actions.pointer_action.pause(duration)
        actions.pointer_action.release()
        actions.perform()
        log.info(f"Long pressed on element: {locator} for {duration}ms")

    def take_screenshot(self, name=None):
        """
        Take screenshot.

        Args:
            name (str, optional): Screenshot name. Defaults to None.

        Returns:
            str: Screenshot path
        """
        if name is None:
            name = f"screenshot_{int(time.time())}"
        
        file_name = f"{name}.png"
        file_path = os.path.join(self.screenshots_dir, file_name)
        
        try:
            self.driver.save_screenshot(file_path)
            log.info(f"Screenshot saved to: {file_path}")
            return file_path
        except Exception as e:
            log.error(f"Failed to take screenshot: {str(e)}")
            return None

    # --- App Management Methods ---

    def launch_app(self):
        """
        Launch the app.
        """
        self.driver.launch_app()
        log.info("Launched app")

    def close_app(self):
        """
        Close the app.
        """
        self.driver.close_app()
        log.info("Closed app")

    def reset_app(self):
        """
        Reset the app.
        """
        self.driver.reset()
        log.info("Reset app")

    def background_app(self, seconds):
        """
        Put app in background.

        Args:
            seconds (int): Number of seconds to keep app in background
        """
        self.driver.background_app(seconds)
        log.info(f"Put app in background for {seconds} seconds")

    def get_page_source(self):
        """
        Get page source.

        Returns:
            str: Page source
        """
        return self.driver.page_source

    # --- Context Handling Methods ---

    def get_contexts(self):
        """
        Get available contexts.

        Returns:
            list: Available contexts
        """
        return self.driver.contexts

    def get_current_context(self):
        """
        Get current context.

        Returns:
            str: Current context
        """
        return self.driver.context

    def switch_to_context(self, context_name):
        """
        Switch to context.

        Args:
            context_name (str): Context name
        """
        self.driver.switch_to.context(context_name)
        log.info(f"Switched to context: {context_name}")

    def switch_to_native(self):
        """
        Switch to native context.
        """
        self.driver.switch_to.context('NATIVE_APP')
        log.info("Switched to native context")

    def switch_to_webview(self):
        """
        Switch to first available webview context.
        """
        contexts = self.get_contexts()
        for context in contexts:
            if 'WEBVIEW' in context:
                self.switch_to_context(context)
                log.info(f"Switched to webview context: {context}")
                return
        log.warning("No webview context found")
