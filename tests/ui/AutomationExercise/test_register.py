import time

import pytest
from src.pages.ui.AutomationExercisePage.register_user_page import RegisterUserPage
from src.utils import logger
from src.utils.file_reader import read_file

log = logger.customLogger()

testcasedata = read_file("AutomationExerciseData", 'register.json')

class TestRegister:
    """Test class for Register functionality."""

    @pytest.mark.Positive
    @pytest.mark.ui
    @pytest.mark.parametrize("case", testcasedata["Positive"])
    def test_register(self, driver,case):

        register_user = RegisterUserPage(driver)
        register_user.open_automationexercise_page()

        register_user.enterName(case["register_user_name"])
        register_user.enterEmail(case["register_user_email"])
        register_user.clickSignupButton()
        register_user.clickUserTitle(case["register_user_title"])
        register_user.enterPassword(case["register_user_password"])
        register_user.selectDate(case["register_user_birthDay"])
        register_user.selectmonth(case["register_user_birthMonth"])
        register_user.selectyear(case["register_user_birthYear"])
        register_user.clickNewsletterBox()
        register_user.clickSpecialoffersBox()
        register_user.enterAddressfirstName(case["register_user_addressfirstName"])
        register_user.enterAddresslastName(case["register_user_addresslastName"])
        register_user.enterAddresscompany(case["register_user_addressCompany"])
        register_user.enterStreetaddress(case["register_user_streetAddress"])
        register_user.enterAddress(case["register_user_address"])

        register_user.selectCountry(case["register_user_selectCountry"])
        register_user.enterState(case["register_user_state"])
        register_user.enterCity(case["register_user_city"])
        register_user.enterZipcode(case["register_user_zipcode"])
        register_user.enterMobilenumber(case["register_user_mobilenumber"])
        register_user.clickCreateaccountButton()
        Accountcreatedmessage=register_user.getAccountcreatedmessage()
        register_user.verifiytheCreateAccountmessage(Accountcreatedmessage,"ACOUNT CREATED!")







