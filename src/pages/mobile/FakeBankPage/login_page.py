
import logging
from src.pages.mobile.mobile_base_page import MobileBasePage
from src.pages.mobile.mobile_locators import AndroidLoginPageLocators

from src.utils import logger
log = logger.customLogger()


class AndroidLoginPage(MobileBasePage):
    """Android implementation of the login page."""
    
    def __init__(self, driver):
        """Initialize AndroidLoginPage with driver."""
        super().__init__(driver)
        # Using locators from separate class
        self.locators = AndroidLoginPageLocators
        
    def enter_username(self, username):
        """
        Enter username.
        
        Args:
            username (str): Username to enter
            
        Returns:
            AndroidLoginPage: Self reference for method chaining
        """
        self.input_text(self.locators.USERNAME_FIELD, username)
        log.info(f"Entered username: {username}")
        return self
        
    def enter_password(self, password):
        """
        Enter password.
        
        Args:
            password (str): Password to enter
            
        Returns:
            AndroidLoginPage: Self reference for method chaining
        """
        self.input_text(self.locators.PASSWORD_FIELD, password)
        log.info(f"Entered password: {'*' * len(password)}")
        return self
        
    def click_login(self):
        """
        Click login button.

        Returns:
            AndroidHomePage: Home page after successful login
        """
        self.tap(self.locators.MOBILE_NUMBER)


    def login(self, username, password):
        """
        Perform login with username and password.
        
        Args:
            username (str): Username
            password (str): Password
            
        Returns:
            AndroidHomePage: Home page after successful login
        """
        self.enter_username(username)
        self.enter_password(password)
        return self.click_login()
        
    def get_error_message(self):
        """
        Get error message text.
        
        Returns:
            str: Error message text
        """
        return self.get_element_text(self.locators.ERROR_MESSAGE)
        
    def click_forgot_password(self):
        """
        Click forgot password link.
        
        Returns:
            AndroidLoginPage: Self reference for method chaining
        """
        self.tap(self.locators.FORGOT_PASSWORD_LINK)
        log.info("Clicked forgot password link")
        # This would return a different page in a real application
        return self
        
    def is_page_displayed(self):
        """
        Check if login page is displayed.
        
        Returns:
            bool: True if login page is displayed, False otherwise
        """
        #and self.is_element_visible(self.locators.LOGIN_BUTTON)
        return self.is_element_visible(self.locators.MOBILE_NUMBER)
