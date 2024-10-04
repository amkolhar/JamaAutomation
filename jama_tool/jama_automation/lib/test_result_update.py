

"""
Script to upload test result into Jama
"""

import argparse
import datetime

import pandas as pd
from JamaAutomation.lib.JamaLib import JamaLib


class TestResultUpdate(JamaLib):
    def __init__(
        self, test_report, test_group_name, test_cycle_name, test_plan_id
    ):
        super().__init__()

        self.test_report = test_report
        self.test_group_name = test_group_name
        self.test_cycle_name = test_cycle_name
        self.test_plan_id = test_plan_id

    def get_testcase_list(self):
        """
        Create test run dataframe from the test report (*.csv) and test details json file
        return: pandas dataframe conatsinig test_JAMA_id and result
        """
        try:
            # Create a Dataframe for testcase id and result
            test_dataframe = pd.read_csv(self.test_report, sep=",")

            # Check any test_JAMA_id or result has None values
            NaN_test_dataframe = test_dataframe[
                test_dataframe[["test_JAMA_id", "result"]].isna().any(axis=1)
            ]

            test_details_missing = "\n".join(
                NaN_test_dataframe["Name"].to_list()
            )

            if len(NaN_test_dataframe) > 0:
                self.logger.warn(
                    f"The following test cases have not been updated in Jama because the test ID or result is missing.\n{test_details_missing}"
                )

            # Select the columns
            df = test_dataframe[["test_JAMA_id", "result"]]

            # Drop Rows with NaN Values in DataFrame
            df = df.dropna()

            return df

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
            test_result = str(
                test_cases_details.loc[
                    test_cases_details["test_JAMA_id"].str.contains(
                        str(test_id)
                    ),
                    "result",
                ].item()
            )

            result = test_result.upper()

            if result == "PASS":
                status = "PASSED"
            elif result == "FAIL":
                status = "FAILED"
            else:
                status = result

            if (status == "FAILED") or (status == "PASSED"):
                testrun_details = {
                    "testrun_id": int(run_id),
                    "fields": {
                        "testRunStatus": status,
                        "actualResults": "",
                    },
                }

                self.update_test_run(testrun_details)
                self.logger.info(
                    f"Testcase id {test_id} has updated with result {result}"
                )
            else:
                self.logger.error(
                    f"Testcase id {test_id} has not updated result, since result is {result}"
                )

    def update_result(self):
        """
        -Create/Update test group under test paln
        -Add test cases to test group
        -create test cycle and test runid
        -update test result
        """

        try:
            # get test_id and result list
            test_df = self.get_testcase_list()

            # test_id list
            test_cases_id = test_df["test_JAMA_id"].values.tolist()

            # get test group id
            test_group_id = self.get_test_group(self.test_plan_id)

            # add test cases to test group
            self.update_testgroup(
                self.test_plan_id, test_group_id, test_cases_id
            )

            # Create test cycle
            test_cycle_id = self.create_cycle(self.test_plan_id, test_group_id)

            # create test run id
            if test_cycle_id is not None:
                testrun_id = self.get_testcase_testrun_id(test_cycle_id)

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
        "--test_group",
        type=str,
        required=True,
        help="Test group name from JAMA",
    )
    arg_parser.add_argument(
        "--release",
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
        args.test_report, args.test_group, args.release, args.test_plan
    )

    test_exec_obj.update_result()
