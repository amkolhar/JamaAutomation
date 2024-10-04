

"""
Script to read the details of unittest cases from unit-test file 
and update the details into Jama

To update unit test in JAMA run python file jama_tool/jama_automation/lib/unit_test_update.py
it takes two command line arguments 
    a. --input_file : Provide which .txt file to be executed
        by default script will execute all .txt files present in lpc-sw/jama_tool/inputs 
    b. --git_branch : provide git branch name to update link in JAMA for unit test.
"""

import argparse
import json
import os
import subprocess

import pandas as pd
from data import constants
from JamaAutomation.lib.JamaLib import JamaLib, text_to_rich_text

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)


class Testcase(JamaLib):
    def __init__(self):
        super().__init__()
        self.testcase_data = []

    def read_function_details(self, path):
        """
        Read function details from cpp file and creates a nested dictionary
            with Name, Description, detail_design_id, unit_test_id
        param path: absolute path of unit-test file
        return: list with unit-test details
        """
        try:
            # open the file to read details
            with open(path, "r") as fd:
                file_data = fd.read()
                test_info = file_data.split("\\brief")[1:]
            fd.close()

            # read each function details
            for details in test_info:
                read_comment = []
                read_function = []
                testcase_details = {}
                func_data = details.strip().split("\n")
                flag = False
                for desc in func_data:
                    if "///" in desc and flag == False:
                        if (constants.SDD_ID in desc) or (
                            constants.SUV_ID in desc
                        ):
                            flag == True
                        else:
                            read_comment.append(desc)
                    elif desc.strip() == "" or "///" in desc:
                        pass
                    elif ";" in desc or "{" in desc:
                        read_function.append(desc)
                        break
                    else:
                        read_function.append(desc)

                # read description
                description = "Brief " + read_function[0]
                description = text_to_rich_text(description)
                for line in read_comment:
                    param_return = line.strip().split("///")
                    param_return = " ".join(param_return)
                    description = description + " " + param_return
                    description = text_to_rich_text(description)
                    description = description.replace("\\param", "Param:")
                    description = description.replace("\\return", "Return:")

                # read detail_design_id
                if constants.SDD_ID in details:
                    sdd_info = details.split(constants.SDD_ID)[1].split("\n")[0]
                    if "MISSING" in sdd_info:
                        detail_design_id = None
                    else:
                        detail_design_id = int(sdd_info)
                else:
                    detail_design_id = None

                # read arch_doc_id
                if constants.SUV_ID in details:
                    suv_info = details.split("SUV_ID")[1].split("\n")[0]
                    if "MISSING" in suv_info:
                        unit_test_id = None
                    else:
                        unit_test_id = int(suv_info)
                else:
                    unit_test_id = None

                # find function defination using regex
                # val = re.findall(r'(\(.+?\))',func)

                # read function name
                # func_with_param = read_function[1].split('(')[0]

                # read function name with complete line
                func_with_param = read_function[1]
                if ")" not in func_with_param:
                    func_with_param = (
                        func_with_param + " " + read_function[2].strip()
                    )

                suite_test_names = (
                    func_with_param[
                        func_with_param.find("(")
                        + 1 : func_with_param.find(")")
                    ]
                    .replace(",", ".")
                    .replace(" ", "")
                )

                # create url to bitbucket master branch souce code
                function_name = read_function[1].replace("{", "")
                if function_name in file_data:
                    phrase_index = file_data.index(function_name)
                    l_num = (
                        file_data[:phrase_index].count("\n") + 1
                    )  # Nth line has n-1 '\n's before
                    url = self.create_ulr(path, l_num)
                else:
                    url = None

                # add details to dictionary
                testcase_details[constants.NAME] = suite_test_names
                testcase_details[
                    constants.DESCRIPTION
                ] = description  # .replace(",", "")
                testcase_details[constants.DETAIL_DESIGN_ID] = detail_design_id
                testcase_details[constants.UNIT_TEST_ID] = unit_test_id
                testcase_details[constants.SOURCE_CODE_URL] = url

                # append dictionaty to list
                if unit_test_id is not None:
                    self.testcase_data.append(testcase_details)
                else:
                    self.logger.warning(
                        constants.WARNING
                        + "Function {} doesn't have SUV_ID in description, details won't be updated to JAMA".format(
                            func_with_param
                        )
                        + constants.ENDC
                    )
        except KeyError:
            self.logger.error(testcase_details)

    def create_json_file(self):
        """
        create json file for unit-test details
        """
        # create dir under tmp dir for store json file
        root_dir = r"/tmp"
        final_directory = os.path.join(root_dir, r"Jama_Automation")
        if not os.path.exists(final_directory):
            os.makedirs(final_directory)

        json_file = f"{final_directory}/{constants.UNIT_TEST_LIB_FILE}"

        with open(json_file, "w") as testcase_lib_file:
            json.dump(self.testcase_data, testcase_lib_file, indent=4)

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

    def update_unit_test(self):
        """
        Function for update unit-test details to JAMA
        """
        for testcase_detail in self.testcase_data:
            testcase_details = {
                constants.FIELDS: {
                    constants.NAME: testcase_detail[constants.NAME],
                    constants.DESCRIPTION: testcase_detail[
                        constants.DESCRIPTION
                    ],
                    constants.UNIT_TEST_SOUCE_CODE: testcase_detail[
                        constants.SOURCE_CODE_URL
                    ],
                },
                constants.TESTCASE_ID: testcase_detail[constants.UNIT_TEST_ID],
            }

            # update unit-test details
            self.update_unit_test_case(testcase_details)

            # Create link between Detail-design id and unit-test id
            if testcase_detail[constants.DETAIL_DESIGN_ID] is not None:
                self.create_unittest_detaildesign_relationship(
                    testcase_detail[constants.DETAIL_DESIGN_ID],
                    testcase_detail[constants.UNIT_TEST_ID],
                )
            else:
                self.logger.warning(
                    constants.WARNING
                    + "Function {} doesn't have SDD_ID in description, linking won't be done between SUV and SDD in JAMA".format(
                        testcase_detail[constants.NAME]
                    )
                    + constants.ENDC
                )

    def read_input_file(self, input_file):
        """
        Read the file paths from the file passed by command line
        param input_file: absolute file path
        return: list with detail-design file paths
        """
        try:
            unit_test = []
            with open(input_file, "r") as filedata:
                lines = filedata.readlines()

            for line in range(len(lines)):
                if "@unit-test-file-paths-start" in lines[line]:
                    for data in range(line + 1, len(lines)):
                        linedata = lines[data].strip().replace('"', "")
                        if ("@unit-test-file-paths-end" in lines[data]) or (
                            "@detail-design-file-paths-start" in lines[data]
                        ):
                            break
                        elif linedata and linedata[0] != "#":
                            unit_test.append(linedata)

            if not unit_test:
                self.logger.warning(
                    f"{input_file} does not have unit-test paths, please check the paths in input file"
                )

            return unit_test

        except KeyError:
            self.logger.error(KeyError)

    def update_unittest_details(self, input_file):
        """
        Creates a list with details of unit test
        param paths: absolute file pathsfor unit-test
        """
        # get all txt files
        if os.path.isdir(input_file):
            file_name_list = self.find_files(input_file, ".txt")

            for file_name in file_name_list:
                # read all paths from input file
                complete_file_path = f"{input_file}/{file_name}"

                file_paths = self.read_input_file(complete_file_path)

                for file_path in file_paths:
                    complete_path = f"{root_repo}/{file_path}"

                    self.logger.info(f"File under execution : {file_path}")

                    self.read_function_details(complete_path)

                    # Update detail desing data
                    self.update_unit_test()
        else:
            # read all paths from input file
            complete_file_path = f"{path_to_inputs}/{input_file}"

            self.logger.info(f"File under execution : {file_path}")

            file_paths = self.read_input_file(complete_file_path)

            for path in file_paths:
                complete_path = f"{root_repo}/{path}"

                self.read_function_details(complete_path)

                # update unit test details
                self.update_unit_test()

        # create json file for test details
        self.create_json_file()


if __name__ == "__main__":
    root_repo = (
        subprocess.Popen(
            ["git", "rev-parse", "--show-toplevel"], stdout=subprocess.PIPE
        )
        .communicate()[0]
        .rstrip()
        .decode("utf-8")
    )

    path_to_inputs = f"{root_repo}/jama_tool/inputs"

    arg_parser = argparse.ArgumentParser(
        description="Update the unit test cases to the JAMA Project"
    )

    arg_parser.add_argument(
        "--input_file",
        type=str,
        help="Path to the file which conatins unit test file paths, absolute path",
        default=f"{root_repo}/jama_tool/inputs",
    )

    arg_parser.add_argument(
        "--git_branch",
        type=str,
        help="Git branch name, eg, master",
    )

    args = arg_parser.parse_args()

    test_tag_obj = Testcase()

    if (args.input_file is not None) and (args.git_branch is not None):
        test_tag_obj.update_unittest_details(args.input_file)

    else:
        arg_parser.error(
            "Check command line arguments and pass valid input file path and branch name"
        )
