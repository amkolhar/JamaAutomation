

"""
Script to create test cycle into Jama

Example usage:
python test_cycle_create.py --test_plan 482273 --cycle_name test_cycle_name
"""

import argparse
import datetime

from JamaAutomation.lib.JamaLib import JamaLib


class TestCycleCreate(JamaLib):
    def __init__(self, test_plan_id, test_cycle_name):
        super().__init__()

        self.test_cycle_name = test_cycle_name
        self.test_plan_id = test_plan_id

    def get_test_group(self, test_plan_id):
        """
        get all test groups for given test plan
        param: test_plan_id
        return: test_group_id
        """

        # get test groups under given test plan
        test_groups_id = self.get_test_group_id(test_plan_id)

        group_keys = list(test_groups_id.values())

        return group_keys

    def create_cycle(self, test_plan_id, test_group_id):
        """
        Create test cycle for test groups in test plan
        param: test_plan_id, test_group_id
        return: test_cycle_id
        """

        test_cycle_details = {
            "testplan_id": test_plan_id,
            "name": self.test_cycle_name,
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

    def check_test_cycle_exist(self):
        """
        check if test cycle is already exist in Test plan
        param:
        return: Ture if present else False
        """
        test_cycles = self.get_test_cycle_details(self.test_plan_id)
        for cycle in test_cycles:
            if self.test_cycle_name in cycle["name"]:
                return True
        return False

    def test_cycle_create(self):
        """
        -Create test cycle for all groups under given test paln
        """
        try:
            # get test group id
            test_group_id = self.get_test_group(self.test_plan_id)

            # Check if given test cycle already exist
            cycle = self.check_test_cycle_exist()

            # Create test cycle if not exist
            if not cycle:
                self.create_cycle(self.test_plan_id, test_group_id)
            else:
                self.logger.warning(
                    "Test cycle you're trying to create already exists in the Test plan."
                )
                self.logger.error("Test cylce has not been created")

        except Exception as e:
            self.logger.error(e)
            self.logger.debug(e, exc_info=True)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description="Create the test cycle into JAMA Project"
    )

    arg_parser.add_argument(
        "--test_plan",
        type=str,
        required=True,
        help="Jama api Id for Test plan",
    )
    arg_parser.add_argument(
        "--cycle_name",
        type=str,
        required=True,
        help="Name of test cycle to create",
    )
    args = arg_parser.parse_args()

    test_exec_obj = TestCycleCreate(args.test_plan, args.cycle_name)

    test_exec_obj.test_cycle_create()
