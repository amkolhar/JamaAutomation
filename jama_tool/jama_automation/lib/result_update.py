

"""
Script to upload test result into Jama
"""

import argparse
import datetime
import json
import os
from os import listdir

import pandas as pd
from data import constants
from JamaAutomation.lib.JamaLib import JamaLib


class ResultUpdate(JamaLib):
    def __init__(
        self,
        test_report,
        test_group_name,
        test_cycle_name,
    ):
        super().__init__()

        self.test_report = test_report
        self.test_group_name = test_group_name
        self.test_cycle_name = test_cycle_name
        self.test_cycle_id = None
        self.test_list = []

    def get_testcase_list(self, res_file):
        """
        Create test run dataframe from the test report (*.csv) and test details json file
        return: pandas dataframe conatsinig test_id and result
        """
        try:
            # Open and read test details JSON file
            root_dir = "/tmp/Jama_Automation"
            if os.path.exists(root_dir):
                json_file = f"{root_dir}/{constants.UNIT_TEST_LIB_FILE}"

                json_data = open(json_file)

                # create a dictionary from json file
                data = json.load(json_data)

                # Create a Dataframe for testcase name and result
                test_dataframe = pd.read_csv(res_file, sep=",")

                # Select the columns
                test_dataframe = test_dataframe[constants.COLUMNS_TO_SELECT]

                # get Testcase id for given test name
                for name, result in test_dataframe.iterrows():
                    test_dict = {}
                    flag = False
                    for test in data:
                        if (
                            result[constants.TEST_CASE_NAME]
                            == test[constants.NAME]
                        ):
                            test_dict[constants.UNIT_TEST_ID] = test[
                                constants.UNIT_TEST_ID
                            ]
                            test_dict[constants.TEST_RESULT] = result[
                                constants.TEST_RESULT
                            ]
                            self.test_list.append(test_dict)
                            flag = True
                    if flag == False:
                        self.logger.error(
                            f"{result[constants.TEST_CASE_NAME]} test case is not present in Unit test JSON file, please update run Unit test updation script "
                        )
            else:
                self.logger.error(
                    "JSON file not present in /tmp/Jama_Automation, please run Unit test updation script before update result"
                )

        except Exception as e:
            self.logger.error(e)
            self.logger.debug(e, exc_info=True)

    def get_test_group(self, test_plan_id):
        """
        Check given test group present in test paln if present return group id else create new group
        param: test_plan_id
        return: test_group_id
        """

        # get test groups under given test paln
        test_groups_id = self.get_test_group_id(test_plan_id)

        group_keys = test_groups_id.keys()

        # create test group if not exists or return existing group id
        if self.test_group_name not in group_keys:
            test_group_id = self.create_test_group(
                test_plan_id, self.test_group_name
            )
        else:
            test_group_id = test_groups_id[self.test_group_name]

        return test_group_id

    def create_cycle(self, test_plan_id, test_group_id):
        """
        Create test cycle under test group
        param: test_plan_id, test_group_id
        return: test_cycle_id
        """

        test_cycle_details = {
            "testplan_id": test_plan_id,
            "name": f"{self.test_group_name}-{self.test_cycle_name}",
            "test_group": test_group_id,
        }

        start_date = datetime.datetime.today().strftime("%Y-%m-%d")

        end_date = (datetime.datetime.today() + datetime.timedelta(1)).strftime(
            "%Y-%m-%d"
        )

        # create test cycle
        test_cycle_id = self.create_test_cycle(
            test_cycle_details, start_date, end_date
        )

        return test_cycle_id

    def update_test_result(self, testrun_id, test_cases_details):
        """
        Update test result under given testrun id
        param: testrun_id
        return:
        """
        for test_id, run_id in testrun_id.items():
            # get result for test case id
            test_result = (
                test_cases_details[constants.TEST_RESULT]
                .loc[test_cases_details[constants.UNIT_TEST_ID] == test_id]
                .to_string(index=False)
            )

            # update result
            if (test_result.upper() == "FAILED") or (
                test_result.upper() == "PASSED"
            ):
                testrun_details = {
                    "testrun_id": int(run_id),
                    "fields": {
                        "testRunStatus": test_result.upper(),
                        "actualResults": "",
                    },
                }

                self.update_test_run(testrun_details)
                self.logger.info(
                    f"Testcase id {test_id} is updated with result {test_result.upper()}"
                )

    def find_csv_filenames(self):
        """
        fimd all test result files under given directory
        param: path_to_dir
        return: list of csv files
        """

        suffix = ".csv"

        filenames = listdir(self.test_report)

        return [filename for filename in filenames if filename.endswith(suffix)]

    def update_result(self):
        """
        -Create/Update test group under test paln
        -Add test cases to test group
        -create test cycle and test runid
        -update test result
        """

        # get test paln id from config file
        test_plan_id = self.config[constants.PROJECT][constants.TEST_PLAN_ID]

        try:
            # get all csv files from dir
            result_files_list = self.find_csv_filenames()

            for file_name in result_files_list:
                # get test cases from input files
                res_file_path = f"{self.test_report}/{file_name}"

                self.get_testcase_list(res_file_path)

            # create data frame
            test_result_df = pd.DataFrame(self.test_list)

            if test_result_df.empty:
                self.logger.error(
                    "Test cases from input file are not mached with unit-test cases"
                )
            else:
                # get test case list
                test_cases_id = test_result_df[
                    constants.UNIT_TEST_ID
                ].values.tolist()

                # add test cases to test group
                # get test group id
                test_group_id = self.get_test_group(test_plan_id)

                # update test group with test list
                self.update_testgroup(
                    test_plan_id, test_group_id, test_cases_id
                )

                # Create test cycle
                test_cycle_id = self.create_cycle(test_plan_id, test_group_id)

                # create test run id
                if test_cycle_id is not None:
                    testrun_id = self.get_testcase_testrun_id(test_cycle_id)

                # update test result
                self.update_test_result(testrun_id, test_result_df)

        except Exception as e:
            self.logger.error(e)
            self.logger.debug(e, exc_info=True)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description="Upload the test results to JAMA Project"
    )

    arg_parser.add_argument(
        "--test_report", type=str, help="Test results in the *.csv format"
    )
    arg_parser.add_argument(
        "--test_group", type=str, help="Test group name from JAMA"
    )
    arg_parser.add_argument(
        "--release",
        type=str,
        help="release name will be used for create test cycle",
    )
    args = arg_parser.parse_args()

    if (
        (args.test_report is not None)
        and (args.test_group is not None)
        and (args.release is not None)
    ):
        test_exec_obj = ResultUpdate(
            args.test_report, args.test_group, args.release
        )

        test_exec_obj.update_result()

    else:
        arg_parser.error(
            "Check command line arguments and pass valid test report path, group name and release"
        )
