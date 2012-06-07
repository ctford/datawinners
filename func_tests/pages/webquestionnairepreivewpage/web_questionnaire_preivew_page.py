from framework.utils.common_utils import by_css
from pages.page import Page
from pages.smsquestionnairepreviewpage.sms_questionnaire_preview_locator import QUESTIONNAIRE_PREVIEW

class WebQuestionnairePreviewPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def web_questionnaire(self):
        return self.driver.find(QUESTIONNAIRE_PREVIEW)