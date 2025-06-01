from src.pages.ui.ui_base_page import BasePage
from src.pages.ui.ui_locators import RegisterUserPageLocators
from src.utils import logger
log = logger.customLogger()


class RegisterUserPage(BasePage):

    def __init__(self, driver):
        """
        Initialize Register Page with WebDriver instance.

        Args:
            driver: WebDriver instance
        """
        super().__init__(driver)
        self.locators = RegisterUserPageLocators
        log.info("Initialized RegisterUserPageLocators")

    def open_automationexercise_page(self):
        log.info("Opening AcademyPage page")
        self.open("AUTOMATIONEXERCISE_BASE_URL", url_path="login")
        return self

    def enterName(self,Name):
        self.input_text(self.locators.signup_Name,Name)

    def enterEmail(self,Email):
        self.input_text(self.locators.signup_Email,Email)

    def clickSignupButton(self):
        self.click(self.locators.signup_Button)

    def clickUserTitle(self,title):
        self.find_and_click_element_by_text(self.locators.user_title,title)

    def enterPassword(self,password):
        self.input_text(self.locators.password,password)

    def selectDate(self,value):
        self.select_dropdown_option_by_value(self.locators.Date_of_Birth_day,value)
    def selectmonth(self,value):
        self.select_dropdown_option_by_value(self.locators.Date_of_Birth_month,value)

    def selectyear(self,value):
        self.select_dropdown_option_by_value(self.locators.Date_of_Birth_year,value)

    def clickNewsletterBox(self):
        if not self.is_element_selected(self.locators.newsletter):
            self.click(self.locators.newsletter)

    def clickSpecialoffersBox(self):
        if not self.is_element_selected(self.locators.special_offers):
            self.click(self.locators.special_offers)

    def enterAddressfirstName(self, address_firstName):
        self.input_text(self.locators.address_firstName, address_firstName)

    def enterAddresslastName(self, address_lastName):
        self.input_text(self.locators.address_lastName, address_lastName)

    def enterAddresscompany(self, address_company):
        self.input_text(self.locators.address_company, address_company)

    def enterStreetaddress(self, street_address):
        self.input_text(self.locators.street_address, street_address)

    def enterAddress(self, address_2):
        self.input_text(self.locators.address_2, address_2)

    def selectCountry(self, country_value):
        self.select_dropdown_option_by_value(self.locators.country,country_value)


    def enterState(self, state):
        self.input_text(self.locators.state, state)

    def enterCity(self, city):
        self.input_text(self.locators.city, city)

    def enterZipcode(self, zipcode):
        self.input_text(self.locators.zipcode, zipcode)

    def enterMobilenumber(self, mobile_number):
        self.input_text(self.locators.mobile_number, mobile_number)

    def clickCreateaccountButton(self):
        self.click(self.locators.create_account)

    def getAccountcreatedmessage(self):
        return self.get_text(self.locators.account_created_message)


    def verifiytheCreateAccountmessage(self,actualText, expectedText):
        self.verifyTextMatch(actualText, expectedText)


    def scrollToAdress(self):
        self.scroll_to_element_by_location(self.locators.address_2)

