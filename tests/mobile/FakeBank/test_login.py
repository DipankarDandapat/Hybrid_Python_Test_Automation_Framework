import os
import json
import time

import pytest
import logging


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




# class TestLogin:
#
#     def test_valid_login(self,driver):
#         """Test valid login scenario."""
#         # Skip if not mobile test
#         # if os.getenv('TEST_TYPE', 'ui') != 'mobile':
#         #     logger.info("Skipping mobile test as test type is not 'mobile'")
#         #     pytest.skip("This test is only for mobile test type")
#         #
#         # # Check if driver is available
#         # if not hasattr(self, 'driver') or not self.driver:
#         #     pytest.fail("Driver is not available for the test")
#
#         # Get test data
#         test_data = TEST_DATA['login_test_data']['valid_credentials']
#         username = test_data['username']
#         password = test_data['password']
#         expected_welcome = test_data['expected_welcome']
#
#         # Get login page based on platform
#         if os.getenv('PLATFORM', 'android') == 'android':
#             login_page = AndroidLoginPage(self.driver)
#
#             # Verify login page is displayed
#             assert login_page.is_page_displayed(), "Login page is not displayed"
#
#             login_page.click_login()
#             time.sleep(10)
#             print("dddddddddddddddddddddppppppppppppppppppppppppppppppppp")
#             # Perform login
#             #home_page = login_page.login(username, password)
#
#             # Verify successful login
#             #assert home_page.is_user_logged_in(), "User is not logged in"
#
#             # Verify welcome message
#             # welcome_message = home_page.get_welcome_message()
#             # assert welcome_message == expected_welcome, f"Welcome message '{welcome_message}' does not match expected '{expected_welcome}'"
#             #
#             # # Logout
#             # login_page = home_page.logout()
#
#             # Verify back to login page
#             # assert login_page.is_page_displayed(), "Login page is not displayed after logout"
#
#
#     # def test_invalid_login(self,driver):
#     #     # Get login page based on platform
#     #     if os.getenv('PLATFORM', 'android') == 'android':
#     #         login_page = AndroidLoginPage(self.driver)
#     #
#     #         # Verify login page is displayed
#     #         assert login_page.is_page_displayed(), "Login page is not displayed"
#     #
#     #         login_page.click_login()
#     #         time.sleep(10)
#     #         print("dddddddddddddddddddddppppp4555555555555")
