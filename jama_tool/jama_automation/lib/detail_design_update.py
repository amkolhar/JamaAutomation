

"""
Script to read the details from detail-design file 
and update the details into Jama

To update detail design in JAMA run python file lpc-sw/jama_tool/jama_automation/lib/detail_design_update.py
    it takes two command line arguments 
    a. --input_file : Provide which .txt file to be executed
        by default script will execute all .txt files present in lpc-sw/jama_tool/inputs 
    b. --git_branch : provide git branch name to update link in JAMA for detail design.
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
        self.deaildesign_details = []

    def read_function_details(self, path):
        """
        Read the function details from file and creates a dictionary
            with Name, Description, detail_design_id, arch_doc_id
        param path: absolute path of the detail-design file
        return: list with detail-design details
        """
        try:
            # open the file to read details
            with open(path, "r") as fd:
                file_data = fd.read()
                detail_design_info = file_data.split("\\brief")[1:]
            fd.close()

            # read each function details
            for details in detail_design_info:
                read_comments = []
                read_function = []
                deaildesign_info = {}
                func_data = details.strip().split("\n")
                flag = False
                for desc in func_data:
                    if "///" in desc and flag == False:
                        if (constants.SDD_ID in desc) or (
                            constants.SAD_ID in desc
                        ):
                            flag = True
                        else:
                            read_comments.append(desc)
                    elif desc.strip() == "" or "///" in desc:
                        pass
                    elif ";" in desc or "{" in desc:
                        read_function.append(desc)
                        break
                    else:
                        read_function.append(desc)

                # read description
                description = "Brief: " + read_function[0]
                description = text_to_rich_text(description)
                for line in read_comments:
                    description1 = line.strip().split("///")
                    description1 = " ".join(description1)
                    description = description + " " + description1
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
                if constants.SAD_ID in details:
                    sad_info = details.split(constants.SAD_ID)[1].split("\n")[0]
                    if "MISSING" in sad_info:
                        arch_doc_id = None
                    else:
                        arch_doc_id = sad_info
                else:
                    arch_doc_id = None

                # find function defination using regex
                # val = re.findall(r'(\(.+?\))',func)

                # read only function name
                # func_name = read_function[1].split('(')[0].split()[1]

                # read function name with complete line
                func_with_param = (
                    read_function[1].replace(";", "").replace("{", "")
                )
                if ")" not in func_with_param:
                    func_with_param = (
                        func_with_param
                        + " "
                        + read_function[2]
                        .strip()
                        .replace(";", "")
                        .replace("{", "")
                    )

                # create url to bitbucket master branch souce code
                function_name = read_function[1].replace(";", "")
                if function_name in file_data:
                    phrase_index = file_data.index(function_name)
                    l_num = (
                        file_data[:phrase_index].count("\n") + 1
                    )  # Nth line has n-1 '\n's before
                    url = self.create_ulr(path, l_num)
                else:
                    url = None

                # add details to dictionary
                deaildesign_info[constants.NAME] = func_with_param
                deaildesign_info[constants.DESCRIPTION] = description
                deaildesign_info[constants.DETAIL_DESIGN_ID] = detail_design_id
                deaildesign_info[constants.ARCH_DOC_ID] = arch_doc_id
                deaildesign_info[constants.SOURCE_CODE_URL] = url

                # append dictionaty to list
                if detail_design_id is not None:
                    self.deaildesign_details.append(deaildesign_info)
                else:
                    self.logger.warning(
                        constants.WARNING
                        + "Function {} doesn't have SDD_ID in description, details won't be updated to JAMA".format(
                            func_with_param
                        )
                        + constants.ENDC
                    )

        except KeyError:
            self.logger.error(deaildesign_info)

    def create_json_file(self):
        """
        create json file for unit-test details
        """
        # create dir under tmp dir for store json file
        root_dir = r"/tmp"
        final_directory = os.path.join(root_dir, r"Jama_Automation")
        if not os.path.exists(final_directory):
            os.makedirs(final_directory)

        json_file = f"{final_directory}/{constants.DETAIL_DESIGN_LIB_FILE}"

        with open(json_file, "w") as testcase_lib_file:
            json.dump(self.deaildesign_details, testcase_lib_file, indent=4)

    def create_ulr(self, file_name, line_num):
        """
        Function to create url to bitbucket master brnach for given file and line number
        param file_name: Path of the dettail-design
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

    def update_detail_design(self):
        """
        Function to update detail-design details in JAMA
        """
        for detail_design in self.deaildesign_details:
            testcase_details = {
                constants.REQ_ID: detail_design[constants.DETAIL_DESIGN_ID],
                constants.FIELDS: {
                    constants.NAME: detail_design[constants.NAME],
                    constants.DESCRIPTION: detail_design[constants.DESCRIPTION],
                    constants.DD_SOURCE_CODE: detail_design[
                        constants.SOURCE_CODE_URL
                    ],
                    constants.DD_ITEM_TYPE: constants.DETAIL_DESIGN_ITEM_TYPE_JAMA_ID,
                    constants.DD_OBJECT_TYPE: constants.DETAIL_DESIGN_OBJECT_TYPE_JAMA_ID,
                    constants.DD_VERIFICATION_METHOD: [
                        constants.DETAIL_DESIGN_VERIFICATION_METHOD_JAMA_ID
                    ],
                },
            }

            # update dedail-design details
            self.update_detaildesign(testcase_details)

            # Create link between Architectural-Design id and Detail-design id
            if detail_design[constants.ARCH_DOC_ID] is not None:
                arch_doc_ids = detail_design[constants.ARCH_DOC_ID].split(",")
                for id in arch_doc_ids:
                    self.create_detaildesign_architectural_relationship(
                        id, detail_design[constants.DETAIL_DESIGN_ID]
                    )
            else:
                self.logger.warning(
                    constants.WARNING
                    + "Function {} doesn't have SAD_ID in description, linking won't be done between SAD and SDD in JAMA".format(
                        detail_design[constants.NAME]
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
            detail_design = []
            with open(input_file, "r") as filedata:
                lines = filedata.readlines()

            for line in range(len(lines)):
                if "@detail-design-file-paths-start" in lines[line]:
                    for data in range(line + 1, len(lines)):
                        linedata = lines[data].strip().replace('"', "")
                        if ("@detail-design-file-paths-end" in lines[data]) or (
                            "@unit-test-file-paths-start" in lines[data]
                        ):
                            break
                        elif linedata and linedata[0] != "#":
                            detail_design.append(linedata)

            if not detail_design:
                self.logger.warning(
                    f"{input_file} does not have detail-design paths, please check the paths in input file"
                )

            return detail_design

        except KeyError:
            self.logger.error(KeyError)

    def update_detaildesign_details(self, input_file):
        """
        Creates a list with details of detail design
        param paths: absolute file paths for detail-design
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

                    # Update detail design data
                    self.update_detail_design()
        else:
            # read all paths from input file
            complete_file_path = f"{path_to_inputs}/{input_file}"

            file_paths = self.read_input_file(complete_file_path)

            for file_path in file_paths:
                complete_path = f"{root_repo}/{file_path}"

                self.logger.info(f"File under execution : {file_path}")

                self.read_function_details(complete_path)

                # Update detail design data
                self.update_detail_design()

        # create json file with detail-design details
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
        description="Update the test results to the JAMA Project"
    )

    arg_parser.add_argument(
        "--input_file",
        type=str,
        help="Path to the file which contains detail design file paths, absolute path",
        default=path_to_inputs,
    )
    arg_parser.add_argument(
        "--git_branch",
        type=str,
        help="Git branch name, eg, master",
    )

    args = arg_parser.parse_args()

    test_tag_obj = Testcase()

    if (args.input_file is not None) and (args.git_branch is not None):
        test_tag_obj.update_detaildesign_details(args.input_file)

    else:
        arg_parser.error(
            "Check command line arguments and pass valid input file path and git brnach"
        )
