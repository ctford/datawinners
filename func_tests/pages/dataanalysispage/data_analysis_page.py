# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import time
from pages.dataanalysispage.data_analysis_locator import *
from pages.page import Page
from pages.submissionlogpage.submission_log_page import SubmissionLogPage
from pages.websubmissionpage.web_submission_page import WebSubmissionPage
from tests.dataanalysistests.data_analysis_data import CURRENT_MONTH, LAST_MONTH, YEAR_TO_DATE, DAILY_DATE_RANGE, MONTHLY_DATE_RANGE
import datetime

BTN_DONE_ = '//div[contains(@class, "ui-daterangepickercontain")]//button[contains(@class, "btnDone")]'

class DataAnalysisPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)
        self.date_range_dict = {CURRENT_MONTH: self.select_current_month,
                           LAST_MONTH: self.select_last_month,
                           YEAR_TO_DATE: self.select_year_to_date,
                           DAILY_DATE_RANGE: self.select_daily_date_range,
                           MONTHLY_DATE_RANGE: self.select_monthly_date_range}

    def navigate_to_all_data_record_page(self):
        """
        Function to navigate all data record page

        Return data all data record
         """
        self.driver.find(ALL_DATA_RECORDS_LINK).click()
        return SubmissionLogPage(self.driver)

    def get_data_from_row(self, row_web_element):
        """
        Function to fetch the data of given row

        Args:
        row_web_element is web element object for the row

        Return row data
        """
        return row_web_element.text

    def get_data_rows(self):
        """
        Function to fetch the number of data rows

        return list of web elements
        """
        return self.driver.find_elements_(DATA_ROWS)

    def get_question(self, question_number):
        """
        Function to fetch the question text of given question number

        Args:
        question_number is question number

        Return question text
        """
        return self.driver.find(by_css(QUESTION_LABEL_CSS % (question_number + 1))).text

    def get_all_data_records(self):
        """
        Function to fetch the data of all the available rows

        Args:
        row_web_element is web element object for the row

        Return list of data
        """
        rows = self.get_data_rows()
        data_record_list = []
        for row_web_element in rows:
            data_record_list.append(self.get_data_from_row(row_web_element))
        return data_record_list

    def get_all_data_records_from_multiple_pages(self):
        data_record_list = []
        while True:
            data_record_list.extend(self.get_all_data_records())
            if self.driver.is_element_present(NEXT_BUTTON_DISABLED) :
                break
            self.go_to_next_page()
        return data_record_list

    def get_number_of_rows(self):
        """
        Function to get the number of data records

        Return number of rows
        """
        return self.get_data_rows().__len__()

    def get_all_question_labels(self):
        """
        Function to get all the questions

        Return list of web element
        """
        return self.driver.find_elements_(QUESTION_LABELS)

    def get_number_of_questions(self):
        """
        Function to get the number of questions

        Return number of questions
        """
        return self.get_data_rows().__len__()
    
    def get_all_questions(self):
        """
        Function to get all the questions

        Return list of web element
        """
        return [unicode(each.text) for each in (self.get_all_question_labels())]

    def select_current_month(self):
        """
        Function to select the date range from the drop down
        """
        self.driver.find_text_box(DATE_RANGE_PICKER_TB).click()
        self.driver.find(CURRENT_MONTH_LABEL).click()

    def get_reporting_period(self):
        return self.driver.find_text_box(DATE_RANGE_PICKER_TB).text

    def select_last_month(self):
        """
        Function to select the date range from the drop down
        """
        self.driver.find_text_box(DATE_RANGE_PICKER_TB).click()
        self.driver.find(LAST_MONTH_LABEL).click()

    def select_year_to_date(self):
        """
        Function to select the date range from the drop down
        """
        self.driver.find_text_box(DATE_RANGE_PICKER_TB).click()
        self.driver.find(YEAR_TO_DATE_LABEL).click()

    def filter_data(self):
        """
        Function to filter the data according to date range
        """
        self.driver.find(FILTER_BUTTON).click()
        self.driver.wait_until_element_is_not_present(20, LOADING_GIF)

    def go_to_next_page(self):
        """
        Function to navigate on next data records page
        """
        self.driver.find(NEXT_BUTTON).click()

    def navigate_to_web_submission_tab(self):
        self.driver.find(by_css('.secondary_tab>li:nth-child(4) a')).click()
        return WebSubmissionPage(self.driver)

    def select_page_size(self, size_str="10"):
        self.driver.find_drop_down(PAGE_SIZE_SELECT).set_selected(size_str)

    def select_daily_date_range(self):
        self.driver.find_text_box(DATE_RANGE_PICKER_TB).click()
        self.driver.find(DAILY_DATE_RANGE_LABEL).click()

    def select_monthly_date_range(self):
        self.driver.find_text_box(DATE_RANGE_PICKER_TB).click()
        self.driver.find(MONTHLY_DATE_RANGE_LABEL).click()

    def select_month_range(self, start_year, start_month, end_year, end_month):
        curr_year = datetime.datetime.today().year
        for i in range(curr_year-start_year):
            self.driver.wait_for_element(20, by_xpath('//span[contains(@class,"prev_year") and position()=1]'), want_visible=True).click()
        for i in range(curr_year-end_year):
            self.driver.wait_for_element(20, by_xpath('//span[contains(@class,"next_year") and position()=2]'), want_visible=True).click()

        self.driver.wait_for_element(20, by_xpath('//div[@id="monthpicker_start"]//td[@data-month="%d"]' % start_month), want_visible=True).click()
        self.driver.wait_for_element(20, by_xpath('//div[@id="monthpicker_end"]//td[@data-month="%d"]' % end_month)).click()

        self.driver.wait_for_element(20, by_xpath(BTN_DONE_), want_visible=True).click()

    def select_date_range(self,start_year, start_month, start_day, end_year, end_month, end_day):
        curr_year = datetime.datetime.today().year
        curr_month = datetime.datetime.today().month
        for i in range((curr_year-start_year)*12 + (curr_month-start_month)):
            self.driver.wait_for_element(20, by_xpath('//div[contains(@class,"range-start")]//a[contains(@class,"ui-datepicker-prev")]'), want_visible=True).click()
            time.sleep(0.01)
        for i in range((curr_year-end_year)*12 + (curr_month-end_month)):
            self.driver.wait_for_element(20, by_xpath('//div[contains(@class,"range-end")]//a[contains(@class,"ui-datepicker-prev")]'), want_visible=True).click()
            time.sleep(0.01)

        self.driver.wait_for_element(20, by_xpath('//div[contains(@class,"range-start")]//a[contains(@class, "ui-state-default") and text()="%d"]/..' % start_day), want_visible=True).click()
        self.driver.wait_for_element(20, by_xpath('//div[contains(@class,"range-end")]//a[contains(@class, "ui-state-default") and text()="%d"]/..' % end_day), want_visible=True).click()

        self.driver.wait_for_element(20, by_xpath(BTN_DONE_), want_visible=True).click()

    def select_for_subject_type(self, subject_name):
        self.driver.wait_for_element(20, by_xpath('//span[contains(@class, "ui-dropdownchecklist-selector")]')).click()
        self.driver.wait_for_element(20, by_xpath('//input[@value="%s"]' % subject_name)).click()
        self.driver.wait_for_element(20, by_xpath('//div[contains(@class, "ui-dropdownchecklist-close")]//button[contains(@class, "btnDone")]')).click()
        pass