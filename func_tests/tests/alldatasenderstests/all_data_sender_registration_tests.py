# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest
from framework.utils.data_fetcher import fetch_, from_
from framework.base_test import  setup_driver, teardown_driver
from pages.alldatasenderspage.all_data_senders_page import AllDataSendersPage
from pages.loginpage.login_page import LoginPage
from pages.adddatasenderspage.add_data_senders_page import AddDataSenderPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, DATA_WINNER_CREATE_DATA_SENDERS, DATA_WINNER_ALL_DATA_SENDERS_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.alldatasenderstests.add_data_senders_data import *

@attr('suit_1')
class TestAllDataSender(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(cls.driver)
        login_page.do_successful_login_with(VALID_CREDENTIALS)

    def setUp(self):
        TestAllDataSender.driver.refresh()
        self.driver.go_to(DATA_WINNER_CREATE_DATA_SENDERS)
        self.current_page = AddDataSenderPage(self.driver)

    def tearDown(self):
        import sys

        exception_info = sys.exc_info()
        if exception_info != (None, None, None):
            import os
            if not os.path.exists("screenshots"):
                os.mkdir("screenshots")
            self.driver.get_screenshot_as_file("screenshots/screenshot-%s-%s.png" % (self.__class__.__name__, self._testMethodName))

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    @attr('functional_test', 'smoke')
    def test_successful_addition_editing_of_data_sender(self):
        """
        Function to test the successful Addition of DataSender with given
        details e.g. first name, last name, telephone number and commune
        """
        add_data_sender_page = self.current_page
        add_data_sender_page.enter_data_sender_details_from(VALID_DATA)

        self.assertRegexpMatches(add_data_sender_page.get_success_message(),
                                 fetch_(SUCCESS_MSG, from_(VALID_DATA)))
        self.driver.go_to(DATA_WINNER_ALL_DATA_SENDERS_PAGE)
        all_data_senders_page = AllDataSendersPage(self.driver)
        all_data_senders_page.select_a_data_sender_by_mobile(VALID_DATA[MOBILE_NUMBER_WITHOUT_HYPHENS])
        all_data_senders_page.select_edit_action()
        self.current_page.enter_data_sender_details_from(VALID_EDIT_DATA)
        self.assertRegexpMatches(self.current_page.get_success_message(),
            fetch_(SUCCESS_MSG, from_(VALID_EDIT_DATA)))

    @attr('functional_test', 'smoke')
    def test_successful_addition_of_data_sender_with_email_address(self):
        """
        Function to test the successful Addition of DataSender with given
        details e.g. first name, last name, telephone number and commune
        """
        add_data_sender_page = self.current_page
        add_data_sender_page.select_web_device()
        add_data_sender_page.enter_email(VALID_DATA_WITH_EMAIL)
        add_data_sender_page.enter_data_sender_details_from(VALID_DATA_WITH_EMAIL)

        self.assertRegexpMatches(add_data_sender_page.get_success_message(),
                                 fetch_(SUCCESS_MSG, from_(VALID_DATA_WITH_EMAIL)))

    @attr('functional_test', 'smoke')
    def test_addition_of_data_sender_without_email_address(self):
        """
        Function to test the successful Addition of DataSender with given
        details e.g. first name, last name, telephone number and commune
        """
        add_data_sender_page = self.current_page
        add_data_sender_page.select_web_device()
        add_data_sender_page.enter_data_sender_details_from(VALID_DATA_WITHOUT_EMAIL)

        self.assertRegexpMatches(add_data_sender_page.get_error_message(),
                                 fetch_(ERROR_MSG, from_(VALID_DATA_WITHOUT_EMAIL)))

    @attr('functional_test')
    def test_addition_of_data_sender_without_entering_data(self):
        """
        Function to test the Addition of DataSender without giving any data
        """
        add_data_sender_page = self.current_page
        add_data_sender_page.enter_data_sender_details_from(BLANK_FIELDS)
        self.assertEqual(add_data_sender_page.get_error_message(),
                         fetch_(ERROR_MSG, from_(BLANK_FIELDS)))

    @attr('functional_test')
    def test_addition_of_data_sender_with_existing_data(self):
        """
        Function to test the Addition of DataSender with given existing
        details e.g. first name, last name, telephone number and commune
        """
        add_data_sender_page = self.current_page
        add_data_sender_page.enter_data_sender_details_from(EXISTING_DATA)
        self.assertEqual(add_data_sender_page.get_error_message(),
                         fetch_(ERROR_MSG, from_(EXISTING_DATA)))


    @attr('functional_test')
    def test_addition_of_data_sender_without_location_name(self):
        """
        Function to test the Addition of DataSender without giving location name
        """
        add_data_sender_page = self.current_page
        add_data_sender_page.enter_data_sender_details_from(WITHOUT_LOCATION_NAME)
        self.assertRegexpMatches(add_data_sender_page.get_success_message(),
                                 fetch_(SUCCESS_MSG, from_(WITHOUT_LOCATION_NAME)))

    @attr('functional_test')
    def test_addition_of_data_sender_without_gps(self):
        """
        Function to test the Addition of DataSender with invalid GPS
        """
        add_data_sender_page = self.current_page
        add_data_sender_page.enter_data_sender_details_from(WITHOUT_GPS)
        self.assertRegexpMatches(add_data_sender_page.get_success_message(),
                                 fetch_(SUCCESS_MSG, from_(WITHOUT_GPS)))

    @attr('functional_test')
    def test_addition_of_data_sender_with_invalid_gps(self):
        """
        Function to test the Addition of DataSender with invalid GPS
        """
        add_data_sender_page = self.current_page
        add_data_sender_page.enter_data_sender_details_from(INVALID_GPS)
        self.assertEqual(add_data_sender_page.get_error_message(),
                         fetch_(ERROR_MSG, from_(INVALID_GPS)))

    @attr('functional_test')
    def test_addition_of_data_sender_with_invalid_latitude_gps(self):
        """
        Function to test the Addition of DataSender with invalid GPS
        """
        add_data_sender_page = self.current_page
        add_data_sender_page.enter_data_sender_details_from(INVALID_LATITUDE_GPS)
        self.assertEqual(add_data_sender_page.get_error_message(),
                         fetch_(ERROR_MSG, from_(INVALID_LATITUDE_GPS)))

    @attr('functional_test')
    def test_addition_of_data_sender_with_invalid_longitude_gps(self):
        """
        Function to test the Addition of DataSender with invalid GPS
        """
        add_data_sender_page = self.current_page
        add_data_sender_page.enter_data_sender_details_from(INVALID_LONGITUDE_GPS)
        self.assertEqual(add_data_sender_page.get_error_message(),
                         fetch_(ERROR_MSG, from_(INVALID_LONGITUDE_GPS)))

    @attr('functional_test')
    def test_addition_of_data_sender_with_unicode_in_gps(self):
        """
        Function to test the Addition of DataSender with invalid GPS
        """
        add_data_sender_page = self.current_page
        add_data_sender_page.enter_data_sender_details_from(WITH_UNICODE_IN_GPS)
        self.assertEqual(add_data_sender_page.get_error_message(),
                         fetch_(ERROR_MSG, from_(WITH_UNICODE_IN_GPS)))

    @SkipTest
    def test_addition_of_data_sender_with_invalid_gps_with_comma(self):
        """
        Function to test the Addition of DataSender with invalid GPS
        """
        add_data_sender_page = self.current_page
        add_data_sender_page.enter_data_sender_details_from(INVALID_GPS_WITH_COMMA)
        self.assertEqual(add_data_sender_page.get_error_message(),
                         fetch_(ERROR_MSG, from_(INVALID_GPS_WITH_COMMA)))
