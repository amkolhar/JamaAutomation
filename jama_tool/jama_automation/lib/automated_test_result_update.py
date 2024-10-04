

"""
Script to upload automated test case results into Jama

Example usage:
python automated_test_result_update.py --test_plan 482273 --test_cycle test_cycle_name --test_report path_of_results.csv
"""

import argparse

import pandas as pd
from JamaAutomation.lib.JamaLib import JamaLib


class TestResultUpdate(JamaLib):
    def __init__(self, test_plan_id, test_cycle_name, test_report):
        super().__init__()

        self.test_report = test_report
        self.test_cycle_name = test_cycle_name
        self.test_plan_id = test_plan_id

    def get_testcase_list(self):
        """
        Create dataframe from the test report (*.csv)
        return: pandas dataframe conatsinig test_jama_id and result
        """
        try:
            # Create a Dataframe for testcase id and result
            test_dataframe = pd.read_csv(self.test_report, sep=",")
            
            # Convert cvs fileld names to lower case
            test_dataframe.columns = test_dataframe.columns.str.lower()

            # Check any test_jama_id or result has None values
            NaN_test_dataframe = test_dataframe[
                test_dataframe[["test_jama_id", "result"]].isna().any(axis=1)
            ]

            if "name" in NaN_test_dataframe.columns:
                test_details_missing = "\n".join(
                    NaN_test_dataframe["name"].to_list()
                )

            if len(NaN_test_dataframe) > 0:
                self.logger.warn(
                    f"The following test cases have not been updated in Jama because the test ID or result is missing.\n{test_details_missing}"
                )

            # Select the columns
            df = test_dataframe[["test_jama_id", "result"]]

            # Drop Rows with NaN Values in DataFrame
            df = df.dropna()

            return df

        except Exception as e:
            self.logger.error(e)
            self.logger.debug(e, exc_info=True)

    def update_test_result(self, testrun_id, test_cases_details):
        """
        Update test result for given testrun id
        param: testrun_id
        return:
        """
        for test_id, run_id in testrun_id.items():
            # get result for test case id
            for index, test in test_cases_details.iterrows():
                if "MISSING" not in str(test["test_jama_id"]):
                    if int(test_id) == int(
                        str(test["test_jama_id"]).split(".")[0]
                    ):
                        test_result = test["result"]
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

    def update_result(self):
        """
        -Update test results for given test plan and test cycle
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
        "--test_plan",
        type=str,
        required=True,
        help="Jama api Id for Test plan",
    )
    arg_parser.add_argument(
        "--test_cycle",
        type=str,
        required=True,
        help="Name of the test cycle to update result",
    )
    arg_parser.add_argument(
        "--test_report",
        type=str,
        required=True,
        help="Test results file in the *.csv format",
    )
    args = arg_parser.parse_args()

    test_exec_obj = TestResultUpdate(
        args.test_plan, args.test_cycle, args.test_report
    )

    test_exec_obj.update_result()
