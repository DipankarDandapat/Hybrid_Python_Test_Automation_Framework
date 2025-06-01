"""
Android Locators Module.

This module provides locators for Android page objects.
"""
from appium.webdriver.common.appiumby import AppiumBy

class AndroidLoginPageLocators:
    """Locators for Android Login Page."""
    MOBILE_NUMBER = (AppiumBy.XPATH, "//android.view.View[@content-desc='btnContinueWithMobileNumber']")
    PASSWORD_FIELD = (AppiumBy.ID, "com.example.app:id/password")
    LOGIN_BUTTON = (AppiumBy.ID, "com.example.app:id/login")
    ERROR_MESSAGE = (AppiumBy.ID, "com.example.app:id/error_message")
    FORGOT_PASSWORD_LINK = (AppiumBy.ID, "com.example.app:id/forgot_password")

class AndroidHomePageLocators:
    """Locators for Android Home Page."""
    WELCOME_MESSAGE = (AppiumBy.ID, "com.example.app:id/welcome_message")
    MENU_BUTTON = (AppiumBy.ID, "com.example.app:id/menu_button")
    PROFILE_BUTTON = (AppiumBy.ID, "com.example.app:id/profile_button")
    LOGOUT_BUTTON = (AppiumBy.ID, "com.example.app:id/logout_button")
    SETTINGS_BUTTON = (AppiumBy.ID, "com.example.app:id/settings_button")
