

"""
Script to check the static analysis for automated python files

Example usage:
python pytest_static_analysis.py --input_path /path/to/pytest_files --output_path /path/to/static_analysis_logs
"""

import argparse
import logging
import os
import pathlib

from jama_tool.jama_automation.data import constants


class Testcase:
    def __init__(self, file_name):
        self.logger = logging.getLogger("PYTEST")
        self.logger.setLevel(logging.DEBUG)
        handle = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
        )
        handle.setFormatter(formatter)
        handle.setLevel(logging.DEBUG)
        self.logger.addHandler(handle)

        log_handle = logging.FileHandler(file_name, mode="w")
        log_handle.setFormatter(formatter)
        log_handle.setLevel(logging.DEBUG)
        self.logger.addHandler(log_handle)

        self.root_dir = pathlib.Path(
            __file__
        ).parent.parent.parent.parent.resolve()
        self.testcase_data = dict()
        self.testcase_list = list()
        self.result = True

    def get_testcase_details_from_python_file(self, test_case_file):
        """
        Parse the testcase details from the python file using the custom tags.
        # jira_tag : Jira Ticket related to the test case
        # test_level : test_level tag, useful for filtering
        # Test_ID : Test_ID tag, useful for update test case details
        # Requrement_ID : Useful for mapping the test case to requirements
        """
        try:
            with open(test_case_file, "r") as tc_file:
                lines = tc_file.readlines()

            testcase_details = []
            test_info = {
                constants.CLASS_NAME: "",
                constants.TEST_NAME: "",
                constants.JIRA_ID: "",
                constants.TEST_ID: "",
                constants.REQUIREMENT_ID: "",
                constants.TEST_LEVEL: "",
                constants.DESCRIPTION: "",
                constants.CRITERIA: "",
            }

            failed_test_list = list()
            for num in range(len(lines)):
                test_result = "PASSED"
                if "jira_tag" in lines[num]:
                    jira_tag = lines[num].split("jira_tag")[-1].split(":")[-1]
                    test_info[constants.JIRA_ID] = jira_tag

                elif "class Test" in lines[num]:
                    class_name = lines[num].split()[1].split("(")[0]
                    test_info[constants.CLASS_NAME] = class_name

                elif constants.TEST_ID in lines[num]:
                    test_type_tag = (
                        lines[num].split(constants.TEST_ID)[-1].split(":")[-1]
                    )
                    test_info[constants.TEST_ID] = test_type_tag

                elif constants.REQUIREMENT_ID in lines[num]:
                    test_type_tag = (
                        lines[num]
                        .split(constants.REQUIREMENT_ID)[-1]
                        .split(":")[-1]
                    )
                    test_info[constants.REQUIREMENT_ID] = test_type_tag

                elif constants.TEST_LEVEL in lines[num]:
                    test_type_tag = (
                        lines[num]
                        .split(constants.TEST_LEVEL)[-1]
                        .split(":")[-1]
                    )
                    test_type_field = test_type_tag
                    test_info[constants.TEST_LEVEL] = test_type_field

                elif "def test_" in lines[num]:
                    test_name = lines[num].split()[1].split("(")[0]
                    test_info[constants.TEST_NAME] = test_name

                    if "Description" not in (
                        lines[num + 1] + lines[num + 2] + lines[num + 3]
                    ):
                        testcase_details.append(test_info)
                        self.testcase_list.append(test_info)

                        for key, value in test_info.items():
                            updated_value = value.replace(" ", "").replace(
                                "\n", ""
                            )
                            len_value = len(updated_value)
                            if len_value > 0:
                                self.logger.info(
                                    " %s : %s" % (key, value.replace("\n", ""))
                                )
                            else:
                                self.logger.error(
                                    " %s : %s" % (key, value.replace("\n", ""))
                                )
                                test_result = "FAILED"

                        if test_result == "PASSED":
                            self.logger.info(
                                "Static check for test %s : PASSED \n"
                                % test_name
                            )
                        else:
                            failed_test_list.append(
                                test_info[constants.TEST_NAME]
                            )
                            self.logger.error(
                                "Static check for test %s : FAILED \n"
                                % test_name
                            )

                        test_info = {
                            constants.TEST_NAME: "",
                            constants.JIRA_ID: "",
                            constants.TEST_ID: "",
                            constants.REQUIREMENT_ID: "",
                            constants.TEST_LEVEL: "",
                            constants.DESCRIPTION: "",
                            constants.CRITERIA: "",
                        }

                elif "Description" in lines[num]:
                    n = num + 1
                    desc = ""
                    while '"""' not in lines[n]:
                        desc = desc + lines[n]
                        n = n + 1

                    # desc = desc.replace("\n","")
                    description = desc.replace("\n", "")
                    test_info[constants.DESCRIPTION] = description
                    pass_fail_criteria = ""

                    if "Pass/Fail Criteria" in desc:
                        description = desc.split("Pass/Fail Criteria")[0]
                        pass_fail_criteria = desc.split("Pass/Fail Criteria")[
                            1
                        ][1:]

                        test_info[constants.DESCRIPTION] = description
                        test_info[constants.CRITERIA] = pass_fail_criteria

                    if len(test_info[constants.TEST_NAME]) != 0:
                        testcase_details.append(test_info)
                        self.testcase_list.append(test_info)

                        for key, value in test_info.items():
                            updated_value = value.replace(" ", "").replace(
                                "\n", ""
                            )
                            len_value = len(updated_value)
                            if len_value > 0:
                                self.logger.info(
                                    " %s : %s" % (key, value.replace("\n", ""))
                                )
                            else:
                                self.logger.error(
                                    " %s : %s" % (key, value.replace("\n", ""))
                                )
                                test_result = "FAILED"

                        if test_result == "PASSED":
                            self.logger.info(
                                " Static check for test %s : PASSED \n"
                                % test_name
                            )
                        else:
                            failed_test_list.append(
                                test_info[constants.TEST_NAME]
                            )
                            self.logger.error(
                                " Static check for test %s : FAILED \n"
                                % test_name
                            )

                        test_info = {
                            constants.TEST_NAME: "",
                            constants.JIRA_ID: "",
                            constants.TEST_ID: "",
                            constants.REQUIREMENT_ID: "",
                            constants.TEST_LEVEL: "",
                            constants.DESCRIPTION: "",
                            constants.CRITERIA: "",
                        }

            return testcase_details, failed_test_list

        except Exception as e:
            self.logger.error(e)

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

    def create_automated_testsuite_details(self, testsuite_dir):
        """
        Creates a nested dictionary with {testsuite : {testcase : {testcase_detail}}
        for automated tests
        :param testsuite_dir: absolute path to the directory for testsuite
        :return: nested dictionary
        """

        test_suite_dir_path = self.root_dir / testsuite_dir
        python_test_files = self.__get_test_files(test_suite_dir_path)

        test_suite_dict = dict()
        for dir_name, files in python_test_files.items():
            if dir_name not in self.testcase_data:
                self.testcase_data[dir_name] = dict()

            for file in files:
                file_name = os.path.basename(file)
                self.logger.info(
                    "---------------------------------------------------------------------"
                )
                self.logger.info(" Test file : %s" % file_name)
                testsuite_name = file.split("/")[-1].split(".")[0]
                (
                    testcase_detail,
                    test_suite_res,
                ) = self.get_testcase_details_from_python_file(file)
                self.testcase_data[dir_name][testsuite_name] = testcase_detail

                if len(test_suite_res) > 0:
                    self.result = False
                    test_suite_dict[file_name] = test_suite_res
                    # logger.info(" Static check for Test suite %s : %s \n" % (file_name, "PASSED"))
                """ else:
                    self.result = False
                    #logger.error(" Static check for Test suite %s : %s \n" % (file_name, "FAILED"))
                    test_suite_dict[file_name] = test_suite_res """

        self.logger.info(
            " ---------------------------------------------------------------------"
        )
        self.logger.info(" \t\t\t FAILED TEST CASES")
        self.logger.info(
            " ---------------------------------------------------------------------"
        )
        if len(test_suite_dict) > 0:
            for key, value in test_suite_dict.items():
                self.logger.error(" Test_suite :  %s " % key)
                for testcase in value:
                    self.logger.error(" \t\tTestcase : %s " % testcase)
        else:
            self.logger.info(" None of the tests have failed ")

        self.logger.info(" Test result : %s " % self.result)

        return self.result


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description="Update the Intergation test cases to the JAMA Project"
    )

    arg_parser.add_argument(
        "--input_path",
        type=str,
        help="Path to the dir which contains pytest files, absolute path",
        required=True,
    )
    arg_parser.add_argument(
        "--output_path",
        type=str,
        default=".",
        help="Path to the store log file, absolute path",
        required=False,
    )

    args = arg_parser.parse_args()

    log_path = f"{args.output_path}/{'static_analysis.log'}"

    test_tag_obj = Testcase(log_path)

    test_result = test_tag_obj.create_automated_testsuite_details(
        args.input_path
    )
