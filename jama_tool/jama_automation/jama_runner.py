

"""
Jama Integration Runner
"""
import argparse

from lib.requirements import Requirements
from lib.testcase import Testcase
from lib.testexecution import TestExecution


class JamaRunner:
    def __init__(self, args):
        self.args = args

    def __call__(self):
        # Requirements Uploading
        if self.args.requirements:
            requirements_obj = Requirements()
            requirements_obj.upload_requirements_to_jama(self.args.requirements)

        # Test case uploading / updating
        if self.args.automated_testcase:
            automated_testcase = self.args.automated_testcase

            # Automated Testcase Create / Update
            test_case_obj = Testcase()
            test_case_obj.create_automated_testsuite_details(automated_testcase)
            test_case_obj.upload_testcase_to_jama()

            # Updating the test results to JAMA
            if self.args.test_report:
                test_exec_obj = TestExecution(
                    self.args.test_report,
                    self.args.test_plan,
                    self.args.release,
                )
                test_exec_obj.update_test_group()
                test_exec_obj.update_automated_testrun()

        elif self.args.manual_testcase:
            manual_testcase = self.args.manual_testcase

            # Manual Testcase Creat / Update
            test_case_obj = Testcase()
            test_case_obj.create_manual_testsuite_details(manual_testcase)
            test_case_obj.upload_testcase_to_jama()

            # Updating the test results to JAMA
            if self.args.test_report:
                test_exec_obj = TestExecution(
                    self.args.test_report,
                    self.args.test_plan,
                    self.args.release,
                )
                test_exec_obj.update_automated_testrun()

        # Test Result Uploading
        if self.args.test_report:
            test_exec_obj = TestExecution(
                self.args.test_report, self.args.test_plan, self.args.release
            )
            test_exec_obj.update_automated_testrun()


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description="Upload the test results from the nightly to "
        "the JAMA Project"
    )

    # Requirements Creation
    arg_parser.add_argument(
        "--requirements",
        type=str,
        help="Requirements to upload on jama. Absolute path to the .csv file",
    )

    # Testcase Creation
    arg_parser.add_argument(
        "--automated_testcase",
        type=str,
        help="Path to the directory for " "automated tests, absolute path",
    )
    arg_parser.add_argument(
        "--manual_testcase", type=str, help="Manual Testcase, *.csv"
    )

    # Test Execution
    arg_parser.add_argument(
        "--test_report", type=str, help="Test results in the *.csv format"
    )
    arg_parser.add_argument(
        "--test_plan", type=int, help="Test Plan ID from JAMA"
    )
    arg_parser.add_argument(
        "--release", type=str, help="Result Name 10.1.0-RC2"
    )

    JamaRunner(arg_parser.parse_args())()
