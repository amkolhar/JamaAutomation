

"""
Script to update the testcase details to Jama to fror automated python files

Example usage:
python pytest_to_jama.py --git_branch master --test_path /path/to/pytest_files
"""

import argparse
import json
import os
import pathlib

from data import constants
from JamaAutomation.lib.JamaLib import JamaLib, text_to_rich_text


class Testcase(JamaLib):
    def __init__(self):
        super().__init__()
        self.testcase_data = dict()
        self.testcase_list = list()

    def get_testcase_details_from_python_file(self, test_case_file):
        """
        Parse the testcase details from the python file using the custom tags.
        # jira_tag : Jira Ticket related to the test case
        # test_level : test_level tag, useful for filtering
        # Test_ID : Test_ID tag, useful for update test case details
        # Requrement_ID : Useful for mapping the test case to requirements
        """

        with open(test_case_file, "r") as tc_file:
            lines = tc_file.readlines()

        testcase_details = []
        test_info = {
            constants.JIRA_TICKET: "",
            constants.TEST_ID: "",
            constants.REQUIREMENT_ID: "",
            constants.NAME: "",
            constants.TEST_LEVEL: "",
        }
        class_name = ""

        for num in range(len(lines)):
            if "jira_tag" in lines[num]:
                jira_tag = lines[num].split()[-1]
                jira_field = '<p><a href="%s" target="_blank">%s</a></p>' % (
                    jira_tag,
                    jira_tag,
                )
                test_info[constants.JIRA_TICKET] += jira_field + "\n"
            elif "class Test" in lines[num]:
                class_name = lines[num].split()[1].split("(")[0]

            elif constants.TEST_ID in lines[num]:
                test_type_tag = lines[num].split()[-1]
                test_info[constants.TEST_ID] += test_type_tag

            elif constants.REQUIREMENT_ID in lines[num]:
                test_type_tag = lines[num].split()[-1]
                test_info[constants.REQUIREMENT_ID] += test_type_tag

            elif constants.TEST_LEVEL in lines[num]:
                test_type_tag = lines[num].split()[-1]
                test_type_field = test_type_tag
                test_info[constants.TEST_LEVEL] += test_type_field + "\n"

            elif "def test_" in lines[num]:
                test_name = lines[num].split()[1].split("(")[0]
                test_info["name"] = f"{class_name}.{test_name}"
                url = self.create_ulr(test_case_file, num + 1)
                test_info[constants.SOURCE_CODE_URL] = url

                if "Description" not in (lines[num + 1] + lines[num + 2]):
                    testcase_details.append(test_info)
                    self.testcase_list.append(test_info)
                    test_info = {
                        constants.JIRA_TICKET: "",
                        constants.TEST_ID: "",
                        constants.REQUIREMENT_ID: "",
                        constants.NAME: "",
                        constants.TEST_LEVEL: "",
                    }

            elif "Description" in lines[num]:
                n = num + 1
                desc = ""
                while '"""' not in lines[n]:
                    desc = desc + lines[n]
                    n = n + 1
                if "Pass/Fail Criteria" in desc:
                    description = desc.split("Pass/Fail Criteria")[0]
                    pass_fail_criteria = desc.split("Pass/Fail Criteria")[1][1:]

                    test_info[constants.DESCRIPTION] = text_to_rich_text(
                        description
                    )
                    test_info[constants.CRITERIA] = text_to_rich_text(
                        pass_fail_criteria
                    )

                if len(test_info[constants.NAME]) != 0:
                    testcase_details.append(test_info)
                    self.testcase_list.append(test_info)
                    test_info = {
                        constants.JIRA_TICKET: "",
                        constants.TEST_ID: "",
                        constants.REQUIREMENT_ID: "",
                        constants.NAME: "",
                        constants.TEST_LEVEL: "",
                    }

        return testcase_details

    @staticmethod
    def __get_test_files(testsuite_dir):
        """
        Collect all python test files from the directory and its child directories
        :param testsuite_dir: absolute path to the directory
        :return:
        """

        python_test_files = dict()

        for root, dirs, files in os.walk(testsuite_dir):
            key_root = root.split("/")[-1]

            for filepath in pathlib.Path(root).glob("test_*.py"):
                if key_root not in python_test_files.keys():
                    python_test_files[key_root] = [str(filepath.absolute())]
                else:
                    intmt_list = python_test_files[key_root]
                    intmt_list.append(str(filepath.absolute()))
                    python_test_files[key_root] = intmt_list

        return python_test_files

    def create_ulr(self, file_name, line_num):
        """
        Function to create url to bitbucket master brnach for given file and line number
        param file_name: Path of the dettail-desing
        parma line_num: Line number of function
        return: url to bitbucket master branch
        """

        dir_names = file_name.split("/")
        dir_index = dir_names.index("aeva")
        data = dir_names[dir_index:]
        PATH_LAST = "/".join(data)

        # create url
        line_url = f"{constants.DOMAIN}{constants.PATH_FIRST}{args.git_branch}/{PATH_LAST}{constants.FGARMENT}{str(line_num)}"

        return line_url

    def create_json_file(self):
        """
        create json file
        """
        try:
            # create dir under tmp dir for store json file
            root_dir = r"/tmp"
            final_directory = os.path.join(root_dir, r"Jama_Automation")

            if not os.path.exists(final_directory):
                os.makedirs(final_directory)

            json_file = (
                f"{final_directory}/{constants.INTEGRATION_TEST_LIB_FILE}"
            )

            with open(json_file, "w") as testcase_lib_file:
                json.dump(self.testcase_list, testcase_lib_file, indent=4)

        except Exception as e:
            self.logger.error(e)

    def create_automated_testsuite_details(self, testsuite_dir):
        """
        Creates a nested dictionary with {testsuite : {testcase : {testcase_detail}}
        for automated tests
        :param testsuite_dir: absolute path to the directory for testsuite
        :return: nested dictionary
        """

        python_test_files = self.__get_test_files(testsuite_dir)

        for dir_name, files in python_test_files.items():
            if dir_name not in self.testcase_data:
                self.testcase_data[dir_name] = dict()

            for file in files:
                testsuite_name = file.split("/")[-1].split(".")[0]
                testcase_detail = self.get_testcase_details_from_python_file(
                    file
                )
                self.testcase_data[dir_name][testsuite_name] = testcase_detail

        return self.testcase_data

    def upload_testcase_to_jama(self):
        """
        Function to upload test cases - create / update to JAMA
        """

        for dir_name, test_data in self.testcase_data.items():
            for testsuite, testcases in test_data.items():
                for testcase_detail in testcases:
                    try:
                        testcase_name = testcase_detail[constants.NAME]
                        testcase_id = testcase_detail[constants.TEST_ID]
                        
                        if ("MISSING" in testcase_id) or (testcase_id == ""):
                            self.logger.warning(
                                constants.WARNING
                                + "Function {} doesn't have TEST_ID in description, details won't be updated to JAMA".format(
                                    testcase_name
                                )
                                + constants.ENDC
                            )

                        else:
                            #read existing test data
                            data = self.get_test_detail(testcase_id)
                    
                            field_keys = data[constants.FIELDS].keys()
                            item_type = data[constants.ITEM_TYPE]

                            testcase_details = {
                                constants.FIELDS: {
                                    constants.NAME: testcase_name,
                                    constants.DESCRIPTION: testcase_detail[
                                        constants.DESCRIPTION
                                    ],
                                },
                                constants.TESTCASE_ID: testcase_id,
                                constants.CRITERIA: testcase_detail[
                                    constants.CRITERIA
                                ],
                                constants.SOURCE_CODE_URL: testcase_detail[
                                    constants.SOURCE_CODE_URL
                                ],
                            }
                            testcase_all_details = dict(testcase_details)

                            if constants.SYSQT_VERIFICATION_METHOD %item_type in field_keys:
                                testcase_all_details[constants.FIELDS][constants.SYSQT_VERIFICATION_METHOD %item_type]  = data[constants.FIELDS][(constants.SYSQT_VERIFICATION_METHOD %item_type)]
                            elif item_type == 144:
                                testcase_all_details[constants.FIELDS][constants.SYSQT_VERIFICATION_METHOD %item_type] = [constants.VERIFICATION_METHOD["TEST"]]
                            elif constants.VERIFY_METHOD %item_type in field_keys:
                                testcase_all_details[constants.FIELDS][constants.VERIFY_METHOD %item_type] = data[constants.FIELDS][constants.VERIFY_METHOD %item_type]
                            else:
                                testcase_all_details[constants.FIELDS][constants.VERIFY_METHOD %item_type] = [constants.VERIFICATION_METHOD["TEST"]]

                            if constants.OBJECT_TYPE %item_type in field_keys:
                                testcase_all_details[constants.FIELDS][constants.OBJECT_TYPE %item_type] = data[constants.FIELDS][(constants.OBJECT_TYPE %item_type)]

                            if constants.JIRATICKET %item_type in field_keys:
                                testcase_all_details[constants.FIELDS][
                                    constants.JIRATICKET %item_type] = str(data[constants.FIELDS][(constants.JIRATICKET %item_type)])
                                
                            if constants.JIRA_URL %item_type in field_keys:
                                testcase_all_details[constants.FIELDS][
                                    constants.JIRA_URL %item_type] = data[constants.FIELDS][(constants.JIRA_URL %item_type)]
                                
                            if constants.TEST_CADENCE %item_type in field_keys:
                                testcase_all_details[constants.FIELDS][
                                    constants.TEST_CADENCE %item_type] =  int(data[constants.FIELDS][(constants.TEST_CADENCE %item_type)])
                                        
                            if constants.RELEASE in field_keys:
                                testcase_all_details[constants.FIELDS][
                                    constants.RELEASE] = data[constants.FIELDS][constants.RELEASE]
                            
                            self.update_test_case(testcase_details)

                            if (
                                "MISSING"
                                in testcase_detail[constants.REQUIREMENT_ID]
                            ) or (testcase_detail == ""):
                                self.logger.warning(
                                    constants.WARNING
                                    + "Function {} doesn't have Requrement_ID in description, linking won't be done.".format(
                                        testcase_detail[constants.NAME]
                                    )
                                    + constants.ENDC
                                )

                            else:
                                self.create_testcase_requirement_relationship(
                                    requirement_id=[
                                        testcase_detail[
                                            constants.REQUIREMENT_ID
                                        ]
                                    ],
                                    testcase_id=testcase_id,
                                )

                    except KeyError:
                        self.logger.error(testcase_detail)

        # create json file for test details
        self.create_json_file()


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description="Update the Intergation test cases to the JAMA Project"
    )

    arg_parser.add_argument(
        "--test_path",
        type=str,
        help="Path to the dir which contains pytest files, absolute path",
        required=True,
    )

    arg_parser.add_argument(
        "--git_branch",
        type=str,
        help="Git branch name, eg, master",
        required=True,
        default="master",
    )

    args = arg_parser.parse_args()

    test_tag_obj = Testcase()

    test_tag_obj.create_automated_testsuite_details(args.test_path)

    test_tag_obj.upload_testcase_to_jama()
