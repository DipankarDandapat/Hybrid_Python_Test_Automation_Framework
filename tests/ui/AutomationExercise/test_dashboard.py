# """
# Dashboard Test Module.
#
# This module contains tests for the dashboard functionality.
# Tests are parameterized using test testData from JSON files.
# """
# import pytest
# from src.pages.login_page import LoginPage
# from src.pages.dashboard_page import DashboardPage
# from src.utils import logger
# log = logger.customLogger()
#
# class TestDashboard:
#     """Test class for dashboard functionality."""
#
#     @pytest.fixture(autouse=True)
#     def setup(self, driver, ui_test_data):
#         """
#         Setup for dashboard tests.
#
#         This fixture logs in before each test.
#
#         Args:
#             driver: WebDriver fixture
#             ui_test_data: UI test testData fixture
#         """
#         # Get login testData
#         login_data = ui_test_data.get("valid_login", {})
#         username = login_data.get("username", "testuser")
#         password = login_data.get("password", "password123")
#
#         logger.info(f"Setting up dashboard test - logging in with username: {username}")
#
#         # Initialize pages
#         self.login_page = LoginPage(driver)
#         self.dashboard_page = DashboardPage(driver)
#
#         # Login
#         self.login_page.open_login_page()
#         self.login_page.login(username, password)
#
#         # Verify login success
#         assert self.dashboard_page.is_dashboard_displayed(), "Dashboard page is not displayed after login"
#
#         yield
#
#         # Cleanup - logout
#         logger.info("Cleaning up dashboard test - logging out")
#         self.dashboard_page.logout()
#
#     @pytest.mark.ui
#     def test_menu_items(self, ui_test_data):
#         """
#         Test dashboard menu items.
#
#         Args:
#             ui_test_data: UI test testData fixture
#         """
#         # Get test testData
#         expected_menu_items = ui_test_data.get("menu_items", [])
#
#         logger.info("Testing dashboard menu items")
#
#         # Get actual menu items
#         actual_menu_items = self.dashboard_page.get_menu_item_texts()
#
#         # Verify menu items
#         assert len(actual_menu_items) == len(expected_menu_items), \
#             f"Expected {len(expected_menu_items)} menu items, got {len(actual_menu_items)}"
#
#         for expected_item in expected_menu_items:
#             assert expected_item in actual_menu_items, \
#                 f"Expected menu item '{expected_item}' not found in actual menu items: {actual_menu_items}"
#
#         logger.info("Dashboard menu items test passed")
#
#     @pytest.mark.ui
#     def test_notification_count(self, ui_test_data):
#         """
#         Test dashboard notification count.
#
#         Args:
#             ui_test_data: UI test testData fixture
#         """
#         # Get test testData
#         expected_count = ui_test_data.get("notification_count", 0)
#
#         logger.info("Testing dashboard notification count")
#
#         # Get actual notification count
#         actual_count = self.dashboard_page.get_notification_count()
#
#         # Verify notification count
#         assert actual_count == expected_count, \
#             f"Expected notification count {expected_count}, got {actual_count}"
#
#         logger.info("Dashboard notification count test passed")
#
#     @pytest.mark.ui
#     def test_search_functionality(self, ui_test_data):
#         """
#         Test dashboard search functionality.
#
#         Args:
#             ui_test_data: UI test testData fixture
#         """
#         # Get test testData
#         search_query = ui_test_data.get("search_query", "test")
#
#         logger.info(f"Testing dashboard search functionality with query: {search_query}")
#
#         # Perform search
#         self.dashboard_page.search(search_query)
#
#         # Verify search results (this is a placeholder as we don't have actual search results page)
#         # In a real test, you would verify search results are displayed correctly
#         assert self.dashboard_page.wait_for_url_contains("search"), \
#             "URL does not contain 'search' after performing search"
#
#         logger.info("Dashboard search functionality test passed")
