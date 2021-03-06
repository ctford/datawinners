# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


##Variables
NAME = "name"
MOBILE_NUMBER = "mobile_number"
LOCATION = "location"
GPS = "gps"
SUCCESS_MSG = "message"
ERROR_MSG = "message"
PROJECT_NAME = "project_name"
ASSOCIATE = "associate"
DISSOCIATE = "disassociate"
UID = "uid"
DELETE = "delete"
EDIT = "edit"
SENDER = "from"
RECEIVER = "to"
SMS = "sms"
MESSAGE = "message"
COMMUNE = "commune"
SUCCESS_MESSAGE = "success_message"

ASSOCIATE_SUCCESS_TEXT = "Data Senders associated Successfully. Please Wait...."
DISSOCIATE_SUCCESS_TEXT = "Data Senders dissociated Successfully. Please Wait...."
ERROR_MSG_WITHOUT_SELECTING_DS = u"Please select atleast 1 data sender"
DELETE_SUCCESS_TEXT = "Data Sender(s) successfully deleted."
SMS_ERROR_MESSAGE = "Your telephone number is not yet registered in our system. Please contact your supervisor."

ASSOCIATE_DATA_SENDER = {PROJECT_NAME: "clinic test project",
                         UID: "rep1",
                         MOBILE_NUMBER: "1234567890"}

DISSOCIATE_DATA_SENDER = {PROJECT_NAME: "clinic test project",
                         UID: "rep1",
                         MOBILE_NUMBER: "1234567890"}

DELETE_DATA_SENDER = {PROJECT_NAME: "clinic test project",
                    UID: u"rep8",
                    MOBILE_NUMBER: "919049008976"}

DISSOCIATE_DS_WITHOUT_SELECTING_PROJECT = {UID: "rep1", ERROR_MSG: "Please select atleast 1 Project"}

ASSOCIATE_DS_WITHOUT_SELECTING_PROJECT = {UID: "rep2", ERROR_MSG: "Please select atleast 1 Project"}

DISSOCIATE_DS_WITHOUT_SELECTING_DS = {PROJECT_NAME: "clinic test project", ERROR_MSG: ERROR_MSG_WITHOUT_SELECTING_DS}

ASSOCIATE_DS_WITHOUT_SELECTING_DS = {PROJECT_NAME: "clinic test project", ERROR_MSG: ERROR_MSG_WITHOUT_SELECTING_DS}

DELETE_DS_WITHOUT_SELECTING_DS = {PROJECT_NAME: "clinic test project", ERROR_MSG: ERROR_MSG_WITHOUT_SELECTING_DS}

VALID_SMS = {SENDER: "919049008976",
                RECEIVER: '919880734937',
                SMS: "cli001 .EID cid003 .NA Mr. Pitt .FA 77 .RD 12.03.2007 .BG b .SY ade .GPS 27.178057  -78.007789 .RM ac",
                SUCCESS_MESSAGE: u"Thank you ReRegistered. We received : EID: cid003 NA: Mr. Pitt FA: 77 RD: 12.03.2007 BG: O- SY: Rapid weight loss,Memory loss,Neurological disorders GPS: 27.178057, -78.007789 RM: Hivid,Vidéx EC"}




VALID_DATA = {NAME: "ReRegistered",
              MOBILE_NUMBER: "919049008976",
              COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
              GPS: "-21.7622088847 48.0690991394",
              SUCCESS_MSG: "Registration successful. ID is: rep"}

DATA_SENDER_ID_WITH_WEB_ACCESS = "rep3"
DATA_SENDER_ID_WITHOUT_WEB_ACCESS = "rep5"
