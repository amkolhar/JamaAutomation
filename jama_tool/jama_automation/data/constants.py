

# Constants

# Config File
COMPANY_JAMA_URL = "company_jama_url"
USER = "User"
USERNAME = "username"
PASSWORD = "password"
JAMA_DETAILS = "jama_details"
PROJECT = "Project"
ID = "id"
ASSIGNED_TO = "assigned_to"
TESTCASE_ITEM_ID = "testcase_item_id"
FOLDER_ITEM_ID = "folder_item_id"
TESTSUITE_LOC_ID = "testsuite_loc_id"
REQUIREMENT_LOC_ID = "requirement_loc_id"
DETAIL_DESIGN_LOC_ID = "detail_design_loc_id"
UNIT_TEST_LOC_ID = "unit_test_loc_id"
DOMAIN = "https://bitbucket.org/"
PATH_FIRST = "/aevainc/lpc-sw/src/"
FGARMENT = "#lines-"
SOURCE_CODE_URL = "souce_code_url"
TEST_PLAN_ID = "test_plan_id"
TEST_SUITE = "test_suite"

FIELDS = "fields"
ITEM_TYPE = "itemType"
NAME = "name"
DESCRIPTION = "description"
TESTCASESTEPS = "testCaseSteps"
PARENT_LOCATION = "parent_location"
LOCATION = 'location'
PARENT = "parent"
CHILD_ITEM_ID = "child_item_id"
TESTCASE_ID = "testcase_id"
SW_REQ_ID = "sw_req_id"
CRITERIA = "criteria"
CLASS_NAME = "Class name"
TEST_NAME = "Test name"
JIRA_ID = "Jira id"

# TESTCASE FIELDS
JIRA_TICKET = "jira_ticket$144"
JIRATICKET = "jira_ticket$%s"
JIRA_URL = "jira_url$%s"
VERIFY_METHOD = "verification_method$%s"
TEST_CADENCE = "test_cadence$%s"
RELEASE = "release"
TEST_TYPE = "test_type$144"
COMPONENT = "component$144"
OBJECT_TYPE = "object_type$%s"
SYSQT_VERIFICATION_METHOD = "verification1_method$%s"

REQUIREMENTS = "requirement_id"
TEST_LEVEL = "test_level"

# DETAIL DESIGN FIELDS
DD_ITEM_TYPE = "item_type$153"
DD_OBJECT_TYPE = "object_type$153"
DD_SOURCE_CODE = "source_code$153"
DD_VERIFICATION_METHOD = "verification_method$153"
UNIT_TEST_SOUCE_CODE = "source_code$192"


SOURCE_CODE = "source_code$%s"
PASSFAIL_CRITERIA = "passfail_criteria$%s"

# JSON FILE LOCATION
TESTCASE_LIB_FILE = "testcase_lib.json"
REQUIREMENT_LIB_FILE = "requirement.json"
DETAIL_DESIGN_LIB_FILE = "detail_desing.json"
UNIT_TEST_LIB_FILE = "unit_test.json"
INTEGRATION_TEST_LIB_FILE = "integration_test.json"
QUALIFICATION_TEST_LIB_FILE = "qualification_test.json"


# Columns from the test report csv file
TEST_CASE_NAME = "Test Case Name"
TEST_RESULT = "Test Result"
COLUMNS_TO_SELECT = [TEST_CASE_NAME, TEST_RESULT]

# JAMA IDS
DETAIL_DESIGN_ITEM_TYPE_JAMA_ID = 933
DETAIL_DESIGN_OBJECT_TYPE_JAMA_ID = 657
DETAIL_DESIGN_VERIFICATION_METHOD_JAMA_ID = 650

SOFTWARE_REQ_ITEM_JAMA_ID = 149
DETAIL_DESIGN_ITEM_JAM_ID = 153
INTEGRATION_TEST_ITEM_JAMA_ID = 193
QUALIFICATION_TEST_ITEM_JAMA_ID = 194
TESTCASE_ITEM_JAMA_ID = 144
UNIT_TESTCASE_ITEM_JAMA_ID = 192
FOLDER_ITEM_JAMA_ID = 32
SW_REQUIREMENT_OBJECT_TYPE = 625
TEST_OBJECT_TYPE = 663  # TEST
TEST_VERIFICATION_TYPE = 650  # TEST
VERIFIED_BY = 18
PRIORITY = {"Unassigned": 658, "LOW": 659, "MEDIUM": 660, "HIGH": 661}
VERIFICATION_METHOD = {
    "INSPECTION": 648,
    "DEMONSTRATION": 649,
    "TEST": 650,
    "ANALYSIS": 651,
}

# DETAIL_DESIGN TAGS
DETAIL_DESIGN_ID = "detail_design_id"
ARCH_DOC_ID = "arch_doc_id"
UNIT_TEST_ID = "unit_test_id"
SDD_ID = "SDD_ID"
TEST_ID = "test_id"
REQUIREMENT_ID = "requirement_id"
SUV_ID = "SUV_ID"
REQ_ID = "req_id"

# print lines in colors, warning, failure and header indications
OKGREEN = "\033[92m"
OKBLUE = "\033[94m"
ENDC = "\033[0m"
BOLD = "\033[1m"

HEADER = "\033[95m"
WARNING = "\033[93m"
FAIL = "\033[91m"
