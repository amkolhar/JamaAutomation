# Copyright Aeva 2024

"""
Script to upload manual test result into Jama

Example usage:
python manual_test_result_update.py --test_report path_of_manual_test_results.csv --test_cycle test_cycle_name --test_plan 482273
"""

import argparse

import numpy as np
import pandas as pd
from data import constants
from JamaAutomation.lib.JamaLib import JamaLib


class TestResultUpdate(JamaLib):
    def __init__(self, test_report, test_cycle_name, test_plan_id):
        super().__init__()

        self.test_report = test_report
        self.test_cycle_name = test_cycle_name
        self.test_plan_id = test_plan_id
        self.testcase_data = list()

    def get_testcase_list(self):
        """
        Create test run dataframe from the test report (*.csv) and test details json file
        return: pandas dataframe conatsinig test_JAMA_id and result
        """
        try:
            # Create a Dataframe for testcase id and result
            test_dataframe = pd.read_csv(self.test_report, header=0)

            test_dataframe = test_dataframe.replace(np.NaN, "-")
            name = test_dataframe.loc[0]["Testcase Name"]
            testcase_id = test_dataframe.loc[0]["test_JAMA_id"]
            description = test_dataframe.loc[0]["Description"]
            sw_req_id = test_dataframe.loc[0]["requirement_JAMA_id"]
            steps = []
            testcase_details = []

            last_index = test_dataframe.tail(1).index.item()
            for index, row in test_dataframe.iterrows():
                new_name = row["Testcase Name"]
                if name != new_name:
                    testcase_details.append(
                        {
                            constants.NAME: name,
                            constants.TESTCASE_ID: testcase_id,
                            constants.SW_REQ_ID: sw_req_id,
                            constants.DESCRIPTION: description,
                            constants.TESTCASESTEPS: steps,
                        }
                    )
                    steps = []
                    testcase_id = row["test_JAMA_id"]
                    sw_req_id = row["requirement_JAMA_id"]

                name = new_name
                individual_step = {
                    "action": row["Step Action"],
                    "expectedResult": row["Expected Results"],
                    "notes": row["Notes"],
                    "status": row["Test Results"],
                }
                steps.append(individual_step)
                if last_index == index:
                    testcase_details.append(
                        {
                            constants.NAME: name,
                            constants.TESTCASE_ID: testcase_id,
                            constants.SW_REQ_ID: sw_req_id,
                            constants.DESCRIPTION: description,
                            constants.TESTCASESTEPS: steps,
                        }
                    )

            self.testcase_data = testcase_details

            return self.testcase_data

        except Exception as e:
            self.logger.error(e)
            self.logger.debug(e, exc_info=True)

    def check_test_cycle_exist(self):
        """
        check if test cycle is already exist in Test plan
        param:
        return: Ture if present else False
        """
        test_cycles = self.get_test_cycle_details(self.test_plan_id)
        for cycle in test_cycles:
            if self.test_cycle_name in cycle["name"]:
                return cycle["id"]
        return False

    def update_test_result(self, testrun_id, test_cases_details):
        """
        Update test result under given testrun id
        param: testrun_id
        return:
        """

        testRunSteps = list()

        for test in test_cases_details:
            # get status for each step in testcase
            test_id = test["testcase_id"]

            # get step stutus if PASS or FAIL
            for steps in test["testCaseSteps"]:
                status_val = {"test_id": "", "status": ""}

                status_val["test_id"] = test_id

                test_result = steps["status"]

                if test_result == "PASS":
                    test_result = "PASSED"
                elif test_result == "FAIL":
                    test_result = "FAILED"
                else:
                    test_result = "NOT_RUN"

                status_val["status"] = test_result
                testRunSteps.append(status_val)

        # create list with steps and status
        for test_id, run_id in testrun_id.items():
            status_list = list()

            for result in testRunSteps:
                status_dict = dict()

                if (
                    result["test_id"] != "-"
                    and "MISSING" not in str(result["test_id"])
                ):
                    if int(test_id) == int(result["test_id"]):
                        status_dict["status"] = result["status"]
                        status_list.append(status_dict)

            # check if test_id in created list
            found = False
            for testcase in testRunSteps:
                if str(test_id) in str(testcase["test_id"]):
                    found = True

            # update testcase status
            if found and "NOT_RUN" not in str(status_list):
                testrun_details = {
                    "testrun_id": int(run_id),
                    "fields": {
                        "testRunSteps": status_list,
                        "actualResults": "",
                    },
                }

                # get latest test case steps in test run
                self.get_latest_test_steps_in_test_run(int(run_id))

                # update test result
                self.update_test_run(testrun_details)

                over_all_status = "Passed"

                if "FAILED" in str(status_list):
                    over_all_status = "Failed"

                self.logger.info(
                    f"Testcase id {test_id} has updated with result {over_all_status}"
                )

    def update_result(self):
        """
        -Create/Update test group under test paln
        -Add test cases to test group
        -create test cycle and test runid
        -update test result
        """
        try:
            # Check test cycle already exist
            cycle = self.check_test_cycle_exist()

            # update results if test cycle exist
            if not cycle:
                self.logger.warning(
                    "Test cycle you're trying to update not exists in the Test plan."
                )
                self.logger.error("Test results are not updated")
            else:
                # get test_id and results
                test_df = self.get_testcase_list()

                # get test run id
                testrun_id = self.get_testcase_testrun_id(cycle)

                # update test result
                self.update_test_result(testrun_id, test_df)

        except Exception as e:
            self.logger.error(e)
            self.logger.debug(e, exc_info=True)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description="Upload the test results to JAMA Project"
    )

    arg_parser.add_argument(
        "--test_report",
        type=str,
        required=True,
        help="Test results file in the *.csv format",
    )
    arg_parser.add_argument(
        "--test_cycle",
        type=str,
        required=True,
        help="release name will be used for create test cycle",
    )
    arg_parser.add_argument(
        "--test_plan",
        type=str,
        required=True,
        help="Jama api Id for Test plan",
    )
    args = arg_parser.parse_args()

    test_exec_obj = TestResultUpdate(
        args.test_report, args.test_cycle, args.test_plan
    )

    test_exec_obj.update_result()
