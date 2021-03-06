# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from nose.plugins.attrib import attr
from framework.base_test import BaseTest
from framework.utils.data_fetcher import fetch_, from_
from pages.createquestionnairepage.create_questionnaire_page import CreateQuestionnairePage
from pages.lightbox.light_box_page import LightBox
from pages.loginpage.login_page import LoginPage
from pages.previewnavigationpage.preview_navigation_page import PreviewNavigationPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.editquestionnairetests.edit_questionnaire_data import *

@attr('suit_2')
class TestEditQuestionnaire(BaseTest):
    def prerequisites_of_edit_questionnaire(self):
        # doing successful login with valid credentials
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)

        # going on all project page
        all_project_page = global_navigation.navigate_to_view_all_project_page()
        project_overview_page = all_project_page.navigate_to_project_overview_page(
            fetch_(PROJECT_NAME, from_(VALID_PROJECT_DATA)))
        edit_project_page = project_overview_page.navigate_to_edit_project_page()
        edit_project_page.continue_create_project()
        return CreateQuestionnairePage(self.driver)

    def prerequisites_of_questionnaire_tab(self):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)

        # going on all project page
        all_project_page = global_navigation.navigate_to_view_all_project_page()
        project_overview_page = all_project_page.navigate_to_project_overview_page("Clinic test project")
        return project_overview_page.navigate_to_questionnaire_tab()

    @attr('functional_test', 'smoke')
    def test_successful_questionnaire_editing(self):
        """
        Function to test the successful editing of a Questionnaire with given details
        """
        create_questionnaire_page = self.prerequisites_of_edit_questionnaire()
        questions = fetch_(QUESTIONS, from_(QUESTIONNAIRE_DATA))
        create_questionnaire_page.select_question_link(2)
        self.assertEqual(questions[0], create_questionnaire_page.get_word_type_question())
        create_questionnaire_page.select_question_link(3)
        self.assertEqual(questions[1], create_questionnaire_page.get_number_type_question())
        create_questionnaire_page.select_question_link(4)
        self.assertEqual(questions[2], create_questionnaire_page.get_date_type_question())
        create_questionnaire_page.select_question_link(5)
        self.assertEqual(questions[3], create_questionnaire_page.get_list_of_choices_type_question())
        create_questionnaire_page.select_question_link(6)
        self.assertEqual(questions[4], create_questionnaire_page.get_list_of_choices_type_question())

    @attr('functional_test')
    def test_sms_preview_of_questionnaire_on_the_questionnaire_tab(self):
        self.prerequisites_of_questionnaire_tab()
        preview_navigation_page = PreviewNavigationPage(self.driver)
        sms_questionnaire_preview_page = preview_navigation_page.sms_questionnaire_preview()

        self.assertIsNotNone(sms_questionnaire_preview_page.sms_questionnaire())
        self.assertEqual(sms_questionnaire_preview_page.get_project_name(), "clinic test project")
        self.assertIsNotNone(sms_questionnaire_preview_page.get_sms_instruction())
        
        sms_questionnaire_preview_page.close_preview()
        self.assertFalse(sms_questionnaire_preview_page.sms_questionnaire_exist())


    @attr('functional_test')
    def test_web_preview_of_questionnaire_on_the_questionnaire_tab(self):
        self.prerequisites_of_questionnaire_tab()
        preview_navigation_page = PreviewNavigationPage(self.driver)
        web_questionnaire_preview_page = preview_navigation_page.web_questionnaire_preview()
        
        self.assertIsNotNone(web_questionnaire_preview_page.get_web_instruction())

    @attr('functional_test')
    def test_smart_phone_preview_of_questionnaire_on_the_questionnaire_tab(self):
        self.prerequisites_of_questionnaire_tab()
        preview_navigation_page = PreviewNavigationPage(self.driver)
        smart_phone_preview_page = preview_navigation_page.smart_phone_preview()

        self.assertIsNotNone(smart_phone_preview_page.get_smart_phone_instruction())

    @attr('functional_test')
    def test_change_date_format_of_report_period_should_show_warning_message_and_clear_submissions(self):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)

        # going on all project page
        all_project_page = global_navigation.navigate_to_view_all_project_page()
        project_overview_page = all_project_page.navigate_to_project_overview_page("clinic6 test project")
        edit_project_page = project_overview_page.navigate_to_edit_project_page()
        edit_project_page.continue_create_project()
        create_questionnaire_page = CreateQuestionnairePage(self.driver)
        create_questionnaire_page.select_question_link(4)
        create_questionnaire_page.change_date_type_question(MM_YYYY)
        light_box = LightBox(self.driver)
        self.assertEquals(light_box.get_title_of_light_box(), fetch_(TITLE, from_(LIGHT_BOX_DATA)))
        self.assertEquals(light_box.get_message_from_light_box(), fetch_(MESSAGE, from_(LIGHT_BOX_DATA)))
        light_box.continue_change_date_format()
        project_overview_page = create_questionnaire_page.save_and_create_project_successfully( )
        data_analysis_page = project_overview_page.navigate_to_data_page( )
        self.assertEqual(1, len(data_analysis_page.get_all_data_records()))

