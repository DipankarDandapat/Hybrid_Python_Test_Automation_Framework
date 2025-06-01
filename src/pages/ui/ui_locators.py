"""
Page Locators Module.

This module contains all UI element locators used in page objects.
Locators are organized by page for easy maintenance.
"""
from selenium.webdriver.common.by import By


class RegisterUserPageLocators:
    """Register Page Locators."""

    signup_Name = (By.XPATH, "//input[@placeholder='Name']")
    signup_Email = (By.XPATH, "//input[@data-qa='signup-email']")
    signup_Button= (By.XPATH, "//button[normalize-space()='Signup']")
    user_title=    (By.XPATH, "//div[@class='radio-inline']")
    password=    (By.XPATH, "//input[@id='password']")
    Date_of_Birth_day=    (By.XPATH, "//select[@id='days']")
    Date_of_Birth_month=    (By.XPATH, "//select[@id='months']")
    Date_of_Birth_year=    (By.XPATH, "//select[@id='years']")
    newsletter=    (By.XPATH, "//input[@id='newsletter']")
    special_offers=    (By.XPATH, "//input[@id='optin']")
    address_firstName=    (By.XPATH, "//input[@id='first_name']")
    address_lastName=    (By.XPATH, "//input[@id='last_name']")
    address_company=    (By.XPATH, "//input[@id='company']")
    street_address=    (By.XPATH, "//input[@id='address1']")
    address_2=    (By.XPATH, "//input[@id='address2']")
    country=    (By.XPATH, "//select[@id='country']")
    state=    (By.XPATH, "//input[@id='state']")
    city=    (By.XPATH, "//input[@id='city']")
    zipcode=    (By.XPATH, "//input[@id='zipcode']")
    mobile_number=    (By.XPATH, "//input[@id='mobile_number']")
    create_account=    (By.XPATH, "//button[@data-qa='create-account']")
    account_created_message=    (By.XPATH, "//h2[@class='title text-center']/b")





class LoginPageLocators:
    """Login Page Locators."""
    
    USERNAME_INPUT = (By.ID, "username")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".error-message")
    REMEMBER_ME_CHECKBOX = (By.ID, "rememberMe")
    FORGOT_PASSWORD_LINK = (By.LINK_TEXT, "Forgot Password?")


class DashboardPageLocators:
    """Dashboard Page Locators."""
    
    WELCOME_MESSAGE = (By.CSS_SELECTOR, ".welcome-message")
    LOGOUT_BUTTON = (By.ID, "logout-button")
    PROFILE_DROPDOWN = (By.ID, "profile-dropdown")
    SETTINGS_LINK = (By.ID, "settings-link")
    NOTIFICATION_ICON = (By.ID, "notification-icon")
    NOTIFICATION_COUNT = (By.CSS_SELECTOR, ".notification-count")
    SEARCH_INPUT = (By.ID, "search-input")
    SEARCH_BUTTON = (By.ID, "search-button")
    MENU_ITEMS = (By.CSS_SELECTOR, ".menu-item")
    USER_AVATAR = (By.CSS_SELECTOR, ".user-avatar")



class AutomationPracticeLocators:
    redioButton1 = (By.XPATH, "//input[@value='radio1']")
    redioButton2 = (By.XPATH, "//input[@value='radio2']")
    redioButton3 = (By.XPATH, "//input[@value='radio3']")
    autocomplete = (By.XPATH, "//input[@id='autocomplete']")
    dropdown =     (By.XPATH, "//select[@id='dropdown-class-example']")
    option1checkbox =     (By.XPATH, "//input[@id='checkBoxOption1']")
    switchWindows =     (By.XPATH, "//button[@id='openwindow']")
    logo =     (By.XPATH, "//a[@href='https://www.qaclickacademy.com']//img[@alt='Logo']")
    opentab =     (By.XPATH, "//a[@id='opentab']")
    alertName =     (By.XPATH, "//input[@id='name']")
    alertButton =     (By.XPATH, "//input[@id='alertbtn']")
    mouseHover =     (By.XPATH, "//button[@id='mousehover']")
    topPage =       (By.XPATH, "//a[contains(@href,'#top')]")
    coursesIframe =   (By.XPATH, "//iframe[@id='courses-iframe']")
    Iframelogo =   (By.XPATH, "//div[@class='logo']//a")

    tableName =   (By.XPATH, "//table[@name='courses']")
    header_locator = (By.XPATH, ".//tbody/tr[1]/th")
    row_locator = (By.XPATH, ".//tbody//tr")
    cell_locator = (By.TAG_NAME, "td")




