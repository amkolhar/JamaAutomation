

"""
Script to read requirement id and testcase id from csv file and maps them in jama

Example usage:
python requirement_testcase_map.py --file_path path_of_requirement_testcase_map.csv
"""

import argparse

import pandas as pd
from JamaAutomation.lib.JamaLib import JamaLib


class MapRequirements(JamaLib):
    def __init__(self, test_report):
        super().__init__()

        self.test_report = test_report

    def read_csv(self):
        """
        Read requirement and testcase jama id from csv file and create data frame
        return: pandas dataframe which holds requirement and testcase jama id
        """
        try:
            # read requirement and test-case jama ids from csv file
            test_dataframe = pd.read_csv(self.test_report, sep=",")

            return test_dataframe

        except Exception as e:
            self.logger.error(e)
            self.logger.debug(e, exc_info=True)

    def map_req_test(self):
        req_list = self.read_csv()

        # map between requirement and tesst case ids
        for index, row in req_list.iterrows():
            requirement_id = (row["requirement_JAMA_id"],)
            testcase_id = row["test_JAMA_id"]

            self.create_testcase_requirement_relationship(
                requirement_id, testcase_id
            )


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description="Upload the test results to JAMA Project"
    )

    arg_parser.add_argument(
        "--test_report",
        type=str,
        help="Test results in the *.csv format",
        required=True,
    )

    args = arg_parser.parse_args()

    test_exec_obj = MapRequirements(args.test_report)

    test_exec_obj.map_req_test()
