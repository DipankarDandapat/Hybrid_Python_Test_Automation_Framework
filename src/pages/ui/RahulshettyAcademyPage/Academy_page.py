from src.pages.ui.ui_base_page import BasePage
from src.pages.ui.ui_locators import AutomationPracticeLocators
from src.utils import logger



log = logger.customLogger()

class AcademyPage(BasePage):
    """Login Page class for handling login functionality."""

    def __init__(self, driver):
        """
        Initialize Login Page with WebDriver instance.

        Args:
            driver: WebDriver instance
        """
        super().__init__(driver)
        self.locators = AutomationPracticeLocators
        log.info("Initialized AcademyPage")

    def open_academyPage_page(self):
        log.info("Opening AcademyPage page")
        self.open("RAHULSHETTYACADEMY_BASE_URL",url_path="AutomationPractice")
        return self

    def clickRadioButtonBaseonName(self, buttonName):
        if buttonName=="Radio1":
            self.click(self.locators.redioButton1)
        elif buttonName=="Radio2":
            self.click(self.locators.redioButton2)
        else:
            self.click(self.locators.redioButton3)


    def enterandAutoselectCountry(self,country):
        self.input_text(self.locators.autocomplete,country)
        self.press_key("ARROW_DOWN")
        self.press_key("ARROW_DOWN")
        self.press_key("ENTER")


    def selectDropdownByValue(self,dropdownvalue):
        self.select_dropdown_option_by_value(locator=self.locators.dropdown,value=dropdownvalue)


    def selectCheckBox(self):
        if not self.is_element_selected(self.locators.option1checkbox):
            self.click(self.locators.option1checkbox)


    def switchWindows(self):
        self.click(self.locators.switchWindows)
        # l=self.get_window_handles()
        # self.switch_to_window_by_handle(l[1])
        self.switch_to_window_by_index(1)
        self.click(self.locators.logo)
        self.close_current_window_and_switch_back()

    def switchOpenTab(self):
        self.click(self.locators.opentab)
        self.switch_to_window_by_index(1)
        self.click(self.locators.logo)
        self.open_new_tab_and_switch()
        self.close_current_window_and_switch_back()

    def switchAlert(self,name):
        self.input_text(self.locators.alertName,name)
        self.click(self.locators.alertButton)
        self.wait_for_alert()
        self.get_alert_text()
        #self.accept_alert()
        self.dismiss_alert()


    def mouseHover(self):
        self.hover_over_element(self.locators.mouseHover)
        self.click(self.locators.topPage)


    def coursesIframe(self):
        self.switch_to_frame(self.locators.coursesIframe)
        self.click(self.locators.Iframelogo)
        self.switch_to_default_content()
        self.selectCheckBox()

    def webTable(self):

        # headers=self.get_table_headers(self.locators.tableName,self.locators.header_locator)
        # print(headers)

        #table_data=self.get_table_data(self.locators.tableName,self.locators.header_locator,self.locators.row_locator,self.locators.cell_locator)
        #print(table_data)

        # column_value=self.get_row_by_column_value(self.locators.tableName,self.locators.header_locator,self.locators.row_locator,self.locators.cell_locator,"Price","20")
        # print(column_value)

        # cell_text=self.get_cell_text(self.locators.tableName,self.locators.header_locator,self.locators.row_locator,self.locators.cell_locator,1,"Price")
        # print(cell_text)

        sum_of_price= self.get_column_values_sum(self.locators.tableName,self.locators.header_locator,self.locators.row_locator,self.locators.cell_locator,"Price")
        return sum_of_price
