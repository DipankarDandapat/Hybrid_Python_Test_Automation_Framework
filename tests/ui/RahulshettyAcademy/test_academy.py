import allure
import pytest
from src.pages.ui.RahulshettyAcademyPage.Academy_page import AcademyPage
from src.utils import logger

log = logger.customLogger()

@allure.epic("UI Testing")
@allure.feature("Academy Page Features")
class TestAcademy:

    @pytest.mark.Positive
    @pytest.mark.ui
    def test_academy_radio_button(self, driver):
        allure.dynamic.story("Radio Button Interaction")
        allure.dynamic.title("Test Academy Radio Button Selection")
        allure.dynamic.description("Verify user can select a specific radio button on the academy page.")

        academy_page = AcademyPage(driver)
        with allure.step("Open academy page"):
            academy_page.open_academyPage_page()
        with allure.step("Select radio button by name"):
            academy_page.clickRadioButtonBaseonName("Radio2")

    @pytest.mark.Positive
    @pytest.mark.ui
    def test_academy_select_country(self, driver):
        allure.dynamic.story("Autocomplete Feature")
        allure.dynamic.title("Test Academy Country Autocomplete")
        allure.dynamic.description("Verify user can enter and select a country using the autocomplete field.")

        academy_page = AcademyPage(driver)
        with allure.step("Open academy page"):
            academy_page.open_academyPage_page()
        with allure.step("Enter and auto-select country"):
            academy_page.enterandAutoselectCountry("india")

    @pytest.mark.Negative
    @pytest.mark.ui
    def test_academy_select_dropdown(self, driver):
        allure.dynamic.story("Dropdown Feature")
        allure.dynamic.title("Test Academy Dropdown Selection")
        allure.dynamic.description("Verify user can select an option from the dropdown menu.")

        academy_page = AcademyPage(driver)
        with allure.step("Open academy page"):
            academy_page.open_academyPage_page()
        with allure.step("Select dropdown option by value"):
            academy_page.selectDropdownByValue("option3")

    @pytest.mark.Negative
    @pytest.mark.ui
    def test_academy_select_checkBox(self, driver):
        allure.dynamic.story("Checkbox Feature")
        allure.dynamic.title("Test Academy Checkbox Selection")
        allure.dynamic.description("Verify user can select the checkbox.")

        academy_page = AcademyPage(driver)
        with allure.step("Open academy page"):
            academy_page.open_academyPage_page()
        with allure.step("Select checkbox"):
            academy_page.selectCheckBox()


    @pytest.mark.Negative
    @pytest.mark.ui
    def test_academy_switch_windows(self, driver):
        allure.dynamic.story("Window Handling")
        allure.dynamic.title("Test Academy Switch Between Windows")
        allure.dynamic.description("Verify switching between windows works correctly.")

        academy_page = AcademyPage(driver)
        with allure.step("Open academy page"):
            academy_page.open_academyPage_page()
        with allure.step("Switch to new window"):
            academy_page.switchWindows()


    @pytest.mark.Negative
    @pytest.mark.ui
    def test_academy_open_tab(self, driver):
        allure.dynamic.story("Tab Handling")
        allure.dynamic.title("Test Academy Open New Tab")
        allure.dynamic.description("Verify opening and switching to a new browser tab.")

        academy_page = AcademyPage(driver)
        with allure.step("Open academy page"):
            academy_page.open_academyPage_page()
        with allure.step("Open and switch to new tab"):
            academy_page.switchOpenTab()

    @pytest.mark.Negative
    @pytest.mark.ui
    def test_academy_open_alert(self, driver):
        allure.dynamic.story("Alert Handling")
        allure.dynamic.title("Test Academy Handle Alert Box")
        allure.dynamic.description("Verify handling of browser alert with input.")

        academy_page = AcademyPage(driver)
        with allure.step("Open academy page"):
            academy_page.open_academyPage_page()
        with allure.step("Handle alert with name input"):
            academy_page.switchAlert("dipankar")

    @pytest.mark.Semantic
    @pytest.mark.ui
    def test_academy_mouseHover(self, driver):
        allure.dynamic.story("Mouse Hover")
        allure.dynamic.title("Test Academy Mouse Hover Action")
        allure.dynamic.description("Verify mouse hover displays additional UI elements.")

        academy_page = AcademyPage(driver)
        with allure.step("Open academy page"):
            academy_page.open_academyPage_page()
        with allure.step("Perform mouse hover"):
            academy_page.mouseHover()

    @pytest.mark.Semantic
    @pytest.mark.ui
    def test_academy_coursesIframe(self, driver):
        allure.dynamic.story("Iframe Handling")
        allure.dynamic.title("Test Academy Courses in Iframe")
        allure.dynamic.description("Verify switching to iframe and interacting with its content.")

        academy_page = AcademyPage(driver)
        with allure.step("Open academy page"):
            academy_page.open_academyPage_page()
        with allure.step("Interact with courses iframe"):
            academy_page.coursesIframe()

    @pytest.mark.Semantic
    @pytest.mark.ui
    def test_academy_webviewTable(self, driver):
        allure.dynamic.story("Web Table Handling")
        allure.dynamic.title("Test Academy Web Table")
        allure.dynamic.description("Verify reading and computing data from web tables.")

        academy_page = AcademyPage(driver)
        with allure.step("Open academy page"):
            academy_page.open_academyPage_page()
        with allure.step("Calculate sum of price from web table"):
            sumofprice = academy_page.webTable()
            allure.attach(str(sumofprice), name="Sum of Prices", attachment_type=allure.attachment_type.TEXT)