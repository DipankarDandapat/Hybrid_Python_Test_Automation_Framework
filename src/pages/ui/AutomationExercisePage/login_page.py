"""
Login Page Module.

This module provides the Login Page class for the Page Object Model pattern.
It contains methods for interacting with the login page.
"""
from src.pages.ui.ui_base_page import BasePage
from src.pages.ui.ui_locators import LoginPageLocators
from src.utils import logger
log = logger.customLogger()


class LoginPage(BasePage):
    """Login Page class for handling login functionality."""

    def __init__(self, driver):
        """
        Initialize Login Page with WebDriver instance.

        Args:
            driver: WebDriver instance
        """
        super().__init__(driver)
        self.locators = LoginPageLocators
        log.info("Initialized LoginPage")

    def open_login_page(self):
        """
        Open login page.

        Returns:
            LoginPage: Self reference for method chaining
        """
        log.info("Opening login page")
        self.open("login")
        return self

    def login(self, username, password, remember_me=False):
        """
        Perform login with provided credentials.

        Args:
            username (str): Username
            password (str): Password
            remember_me (bool, optional): Whether to check remember me. Defaults to False.

        Returns:
            LoginPage: Self reference for method chaining
        """
        log.info(f"Logging in with username: {username}")
        
        # Enter username
        self.input_text(self.locators.USERNAME_INPUT, username)
        
        # Enter password
        self.input_text(self.locators.PASSWORD_INPUT, password)
        
        # Check remember me if needed
        if remember_me:
            log.info("Checking 'Remember Me' checkbox")
            if not self.is_checkbox_selected(self.locators.REMEMBER_ME_CHECKBOX):
                self.click(self.locators.REMEMBER_ME_CHECKBOX)
        
        # Click login button
        self.click(self.locators.LOGIN_BUTTON)
        
        # Wait for page to load
        self.wait_for_page_load()
        
        return self

    def is_error_message_displayed(self):
        """
        Check if error message is displayed.

        Returns:
            bool: True if error message is displayed, False otherwise
        """
        return self.is_element_visible(self.locators.ERROR_MESSAGE)

    def get_error_message(self):
        """
        Get error message text.

        Returns:
            str: Error message text
        """
        if self.is_error_message_displayed():
            return self.get_text(self.locators.ERROR_MESSAGE)
        return ""

    def click_forgot_password(self):
        """
        Click forgot password link.

        Returns:
            LoginPage: Self reference for method chaining
        """
        log.info("Clicking 'Forgot Password' link")
        self.click(self.locators.FORGOT_PASSWORD_LINK)
        return self

    def is_login_page_displayed(self):
        """
        Check if login page is displayed.

        Returns:
            bool: True if login page is displayed, False otherwise
        """
        return (self.is_element_visible(self.locators.USERNAME_INPUT) and 
                self.is_element_visible(self.locators.PASSWORD_INPUT) and 
                self.is_element_visible(self.locators.LOGIN_BUTTON))

    def is_checkbox_selected(self, locator):
        """
        Check if checkbox is selected.

        Args:
            locator (tuple): Locator tuple (By, value)

        Returns:
            bool: True if checkbox is selected, False otherwise
        """
        element = self.find_element(locator)
        return element.is_selected()
