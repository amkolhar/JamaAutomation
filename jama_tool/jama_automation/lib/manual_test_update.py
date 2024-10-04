

"""
Script to create the testcase details for manual testcases to Jama
(from .csv file)

Example usage:
python manual_test_update.py --file_path  path_of_manual_test.csv
"""
import argparse
import json
import os

import numpy as np
import pandas as pd
from data import constants
from JamaAutomation.lib.JamaLib import JamaLib


class Testcase(JamaLib):
    def __init__(self):
        super().__init__()
        self.testcase_data = dict()

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
                f"{final_directory}/{constants.QUALIFICATION_TEST_LIB_FILE}"
            )
            with open(json_file, "w") as testcase_lib_file:
                json.dump(self.testcase_data, testcase_lib_file, indent=4)
        except Exception as e:
            self.logger.error(e)

    def create_manual_testsuite_details(self, testcase_csv):
        """
        Creates a nested dictionary with {testsuite : {testcase : {testcase_detail}}
        for manual tests
        :param testcase_csv: absolute path to the csv file for manual testcases
        :return: nested dictionary
        """
        test_dataframe = pd.read_csv(testcase_csv, header=0)
        test_dataframe = test_dataframe.replace(np.NaN, "-")
        name = test_dataframe.loc[0]["Testcase Name"]
        testcase_id = test_dataframe.loc[0]["test_JAMA_id"]
        description = test_dataframe.loc[0]["Description"]
        sw_req_id = test_dataframe.loc[0]["requirement_JAMA_id"]
        steps = []
        testcase_details = []
        testsuite_details = dict()
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
                old_name = name
            name = new_name
            individual_step = {
                "action": row["Step Action"],
                "expectedResult": row["Expected Results"],
                "notes": row["Notes"],
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
        self.create_json_file()
        return self.testcase_data

    def upload_testcase_to_jama(self):
        """
        Function to upload test cases - create / update to JAMA
        """
        for testcase_detail in self.testcase_data:
            if testcase_detail[constants.NAME] != "-":
                if (testcase_detail[constants.TESTCASE_ID] != "-") and ("MISSING" not in str(testcase_detail[constants.TESTCASE_ID])) :

                    data = self.get_test_detail(testcase_detail[constants.TESTCASE_ID])
                    field_keys = data[constants.FIELDS].keys()
                    item_type = data[constants.ITEM_TYPE]

                    testcase_details = {
                        constants.TESTCASE_ID: int(testcase_detail[constants.TESTCASE_ID]),
                        constants.FIELDS: {
                            # constants.OBJECT_TYPE: constants.TEST_OBJECT_TYPE,
                            constants.NAME: testcase_detail[constants.NAME],
                            constants.DESCRIPTION: testcase_detail[
                                constants.DESCRIPTION
                            ],
                            constants.TESTCASESTEPS: testcase_detail[constants.TESTCASESTEPS],
                        },
                    }
                    testcase_all_details = dict(testcase_details)

                    testcase_all_details[constants.FIELDS][constants.TESTCASESTEPS] = testcase_detail[constants.TESTCASESTEPS]
                    if item_type == 144:
                        testcase_all_details[constants.FIELDS][constants.SYSQT_VERIFICATION_METHOD %item_type] = [constants.VERIFICATION_METHOD["TEST"]]
                    else:
                        testcase_all_details[constants.FIELDS][constants.VERIFY_METHOD %item_type] = [constants.VERIFICATION_METHOD["TEST"]]

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

                    self.update_manual_test_case(testcase_all_details)

                    # Create link between Software requirment and qualification test
                    if testcase_detail[constants.SW_REQ_ID] != "-":
                        requirement_ids = str(
                            testcase_detail[constants.SW_REQ_ID]
                        ).split("\n")
                        for req_id in requirement_ids:
                            req_id = req_id.split(".")[0]
                            self.create_testcase_requirement_relationship(
                                requirement_id=[req_id],
                                testcase_id=int(testcase_detail[constants.TESTCASE_ID]),
                            )
                    else:
                        self.logger.warning(
                            constants.WARNING
                            + "Function {} doesn't have SW_req_ID, linking won't be done between SRA and SQT in JAMA".format(
                                testcase_detail[constants.NAME]
                            )
                            + constants.ENDC
                        )
                else:
                    self.logger.warning(
                        constants.WARNING
                        + "Test case {} has no testcase_id, details are not updated to JAMA".format(
                            testcase_detail[constants.NAME]
                        )
                        + constants.ENDC
                    )
            else:
                self.logger.warning(
                    constants.WARNING
                    + "Testcase Name cell is empty, details are not updated to JAMA"
                    + constants.ENDC
                )


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description="Upload the test results from the nightly "
        "to the JAMA Project"
    )
    arg_parser.add_argument(
        "--file_path",
        type=str,
        help="Qualification Testcases absolute file path, *.csv",
        required=True,
    )
    args = arg_parser.parse_args()

    test_tag_obj = Testcase()
    test_tag_obj.create_manual_testsuite_details(args.file_path)
    test_tag_obj.upload_testcase_to_jama()
