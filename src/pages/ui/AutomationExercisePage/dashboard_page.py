"""
Dashboard Page Module.

This module provides the Dashboard Page class for the Page Object Model pattern.
It contains methods for interacting with the dashboard page.
"""
from src.pages.ui.ui_base_page import BasePage
from src.pages.ui.ui_locators import DashboardPageLocators

from src.utils import logger
log = logger.customLogger()

class DashboardPage(BasePage):
    """Dashboard Page class for handling dashboard functionality."""

    def __init__(self, driver):
        """
        Initialize Dashboard Page with WebDriver instance.

        Args:
            driver: WebDriver instance
        """
        super().__init__(driver)
        self.locators = DashboardPageLocators
        log.info("Initialized DashboardPage")

    def open_dashboard(self):
        """
        Open dashboard page.

        Returns:
            DashboardPage: Self reference for method chaining
        """
        log.info("Opening dashboard page")
        self.open("dashboard")
        return self

    def get_welcome_message(self):
        """
        Get welcome message text.

        Returns:
            str: Welcome message text
        """
        return self.get_text(self.locators.WELCOME_MESSAGE)

    def logout(self):
        """
        Perform logout.

        Returns:
            DashboardPage: Self reference for method chaining
        """
        log.info("Logging out")
        self.click(self.locators.LOGOUT_BUTTON)
        return self

    def open_profile_dropdown(self):
        """
        Open profile dropdown.

        Returns:
            DashboardPage: Self reference for method chaining
        """
        log.info("Opening profile dropdown")
        self.click(self.locators.PROFILE_DROPDOWN)
        return self

    def go_to_settings(self):
        """
        Go to settings page.

        Returns:
            DashboardPage: Self reference for method chaining
        """
        log.info("Going to settings page")
        
        # Open profile dropdown if not already open
        if not self.is_element_visible(self.locators.SETTINGS_LINK, timeout=2):
            self.open_profile_dropdown()
        
        # Click settings link
        self.click(self.locators.SETTINGS_LINK)
        return self

    def get_notification_count(self):
        """
        Get notification count.

        Returns:
            int: Notification count
        """
        if self.is_element_visible(self.locators.NOTIFICATION_COUNT, timeout=2):
            count_text = self.get_text(self.locators.NOTIFICATION_COUNT)
            try:
                return int(count_text)
            except ValueError:
                log.warning(f"Failed to parse notification count: {count_text}")
                return 0
        return 0

    def open_notifications(self):
        """
        Open notifications panel.

        Returns:
            DashboardPage: Self reference for method chaining
        """
        log.info("Opening notifications panel")
        self.click(self.locators.NOTIFICATION_ICON)
        return self

    def search(self, query):
        """
        Perform search.

        Args:
            query (str): Search query

        Returns:
            DashboardPage: Self reference for method chaining
        """
        log.info(f"Searching for: {query}")
        self.input_text(self.locators.SEARCH_INPUT, query)
        self.click(self.locators.SEARCH_BUTTON)
        return self

    def get_menu_items(self):
        """
        Get menu items.

        Returns:
            list: List of menu item elements
        """
        return self.find_elements(self.locators.MENU_ITEMS)

    def get_menu_item_texts(self):
        """
        Get menu item texts.

        Returns:
            list: List of menu item texts
        """
        menu_items = self.get_menu_items()
        return [item.text for item in menu_items]

    def is_dashboard_displayed(self):
        """
        Check if dashboard page is displayed.

        Returns:
            bool: True if dashboard page is displayed, False otherwise
        """
        return (self.is_element_visible(self.locators.WELCOME_MESSAGE) and 
                self.is_element_visible(self.locators.PROFILE_DROPDOWN) and 
                self.is_element_visible(self.locators.LOGOUT_BUTTON))

    def wait_for_dashboard_to_load(self, timeout=None):
        """
        Wait for dashboard to load.

        Args:
            timeout (int, optional): Timeout in seconds. Defaults to None.

        Returns:
            DashboardPage: Self reference for method chaining
        """
        self.wait_for_element(self.locators.WELCOME_MESSAGE, timeout=timeout)
        return self
