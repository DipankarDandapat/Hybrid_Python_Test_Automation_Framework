
import logging
from src.pages.mobile.mobile_base_page import MobileBasePage
from src.pages.mobile.mobile_locators import AndroidHomePageLocators
from src.pages.mobile.FakeBankPage.login_page import AndroidLoginPage

from src.utils import logger
log = logger.customLogger()


class AndroidHomePage(MobileBasePage):
    """Android implementation of the home page."""
    
    def __init__(self, driver):
        """Initialize AndroidHomePage with driver."""
        super().__init__(driver)
        # Using locators from separate class
        self.locators = AndroidHomePageLocators
        
    def get_welcome_message(self):
        """
        Get welcome message text.
        
        Returns:
            str: Welcome message text
        """
        return self.get_element_text(self.locators.WELCOME_MESSAGE)
        
    def open_menu(self):
        """
        Open menu.
        
        Returns:
            AndroidHomePage: Self reference for method chaining
        """
        self.tap(self.locators.MENU_BUTTON)
        log.info("Opened menu")
        return self
        
    def navigate_to_profile(self):
        """
        Navigate to profile.
        
        Returns:
            AndroidHomePage: Self reference for method chaining
        """
        self.tap(self.locators.PROFILE_BUTTON)
        log.info("Navigated to profile")
        # This would return a different page in a real application
        return self
        
    def navigate_to_settings(self):
        """
        Navigate to settings.
        
        Returns:
            AndroidHomePage: Self reference for method chaining
        """
        self.tap(self.locators.SETTINGS_BUTTON)
        log.info("Navigated to settings")
        # This would return a different page in a real application
        return self
        
    def logout(self):
        """
        Perform logout.
        
        Returns:
            AndroidLoginPage: Login page after logout
        """
        self.open_menu()
        self.tap(self.locators.LOGOUT_BUTTON)
        log.info("Logged out")
        return AndroidLoginPage(self.driver)
        
    def is_user_logged_in(self):
        """
        Check if user is logged in.
        
        Returns:
            bool: True if user is logged in, False otherwise
        """
        return self.is_element_visible(self.locators.WELCOME_MESSAGE)
