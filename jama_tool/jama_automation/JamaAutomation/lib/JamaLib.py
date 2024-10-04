# Copyright Aeva 2022

"""
Reused from https://github.com/amkolhar/JamaAutomation
Jama Library
"""

import json
import os

import data.constants as const
from JamaAutomation.lib import logger
from JamaAutomation.py_jama_rest_client.client import JamaClient
from JamaAutomation.py_jama_rest_client.core import Core
from ruamel.yaml import YAML

yaml = YAML()


def text_to_rich_text(text):
    rich_text = "<p>" + text.replace("\n", "<br />\n") + "</p>"

    return rich_text


class JamaLib:
    def __init__(self):
        jama_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        # Config File Keys
        config_path = os.path.join(jama_dir, "data/user_config.yaml")
        with open(config_path, "r") as config_file:
            self.config = yaml.load(config_file)

        self.basic_auth_client = JamaClient(
            self.config[const.COMPANY_JAMA_URL],
            credentials=(
                self.config[const.USER][const.USERNAME],
                self.config[const.USER][const.PASSWORD],
            ),
            oauth=True,
        )
        self.core_auth_client = Core(
            self.config[const.COMPANY_JAMA_URL],
            user_credentials=(
                self.config[const.USER][const.USERNAME],
                self.config[const.USER][const.PASSWORD],
            ),
            oauth=True,
        )
        self.project_id = self.config[const.PROJECT]["id"]
        self.assigned_to = self.config[const.USER][const.ASSIGNED_TO]
        self.testcase_ids = {}
        self.testcase_lib = dict()
        self.requirement_lib = dict()
        self.testsuite_location = self.config[const.PROJECT][
            const.TESTSUITE_LOC_ID
        ]
        self.requirement_location = self.config[const.PROJECT][
            const.REQUIREMENT_LOC_ID
        ]
        self.logger = logger.jamalogger
        self.logger.info(self.project_id)

    def create_folder(self, folder_details):
        """
        folder_details = {"parent_location": "int",
                          "child_item_id" : "int",
                          "fields": {"name":"folder name", any other key:value needed for folder}}
        :param folder_details:
        :return:
        """
        folder_api_id = self.basic_auth_client.post_item(
            project=self.project_id,
            item_type_id=const.FOLDER_ITEM_JAMA_ID,
            child_item_type_id=folder_details["child_item_id"],
            location={"item": folder_details[const.PARENT_LOCATION]},
            fields=folder_details[const.FIELDS],
        )
        self.logger.info(
            "Folder %s is created" % folder_details[const.FIELDS][const.NAME]
        )

        return folder_api_id

    # Requirements Functions

    def get_jama_requirements_details(self):
        requirement_dir_details = (
            self.basic_auth_client.get_item_children_query(
                self.requirement_location, const.FOLDER_ITEM_JAMA_ID
            )
        )

        for feature_dir in requirement_dir_details:
            feature_dict = {}
            feature_details = self.basic_auth_client.get_item_children_query(
                feature_dir["id"], const.FOLDER_ITEM_JAMA_ID
            )
            for feature in feature_details:
                requirement_dict = {}
                requirement_details = (
                    self.basic_auth_client.get_item_children_query(
                        feature["id"], const.TESTCASE_ITEM_JAMA_ID
                    )
                )

                for requirement in requirement_details:
                    requirement_dict[
                        requirement["fields"]["name"]
                    ] = requirement["id"]

                feature_dict[feature["fields"]["name"]] = requirement_dict
                feature_dict[feature["fields"]["name"]] = feature["id"]

            self.requirement_lib[feature_dir["fields"]["name"]] = feature_dict
            self.requirement_lib[feature_dir["fields"]["name"]][
                "id"
            ] = feature_dir["id"]

        # update this location to the NAS location / or don't there is no need to store this file.
        with open(const.REQUIREMENT_LIB_FILE, "w") as req_file:
            json.dump(self.requirement_lib, req_file, indent=4)

    def create_requirements(self, requirement_details):
        """
        requirement_details : {"parent_location": "int",
                               "fields": dictionary of key:values for requirements}
        param requirement_details:
        :return:
        """
        try:
            requirement_id = self.basic_auth_client.post_item(
                project=self.project_id,
                item_type_id=const.SOFTWARE_REQ_ITEM_JAMA_ID,
                child_item_type_id=0,
                location={"item": requirement_details[const.PARENT_LOCATION]},
                fields=requirement_details[const.FIELDS],
            )
            self.logger.info(
                "Success : %s is created"
                % requirement_details[const.FIELDS][const.NAME]
            )
            self.logger.info("JAMA RESPONSE : %s" % requirement_id)

            return requirement_id

        except Exception as e:
            self.logger.error(e)
            self.logger.error(
                f"Error in creating the requirement : %s"
                % requirement_details[const.FIELDS][const.NAME]
            )
            self.logger.debug(e, exc_info=True)
            return None

    def update_requirements(self, requirement_details):
        """
        requirement_details : {"parent_location": "int",
                               "fields": dictionary of key:values for requirements}
        param requirement_details:
        :return:
        """
        try:
            jama_response = self.basic_auth_client.put_item(
                project=self.project_id,
                item_id=requirement_details["req_id"],
                item_type_id=const.SOFTWARE_REQ_ITEM_JAMA_ID,
                child_item_type_id=0,
                location={"item": requirement_details[const.PARENT_LOCATION]},
                fields=requirement_details[const.FIELDS],
            )
            self.logger.info(
                "Success : %s is updated"
                % requirement_details[const.FIELDS][const.NAME]
            )
            self.logger.info("JAMA RESPONSE : %s" % jama_response)

        except Exception as e:
            self.logger.error(e)
            self.logger.error(
                "Error in updating the testcase : %s"
                % requirement_details[const.FIELDS][const.NAME]
            )
            self.logger.debug(e, exc_info=True)

    # Testcase Functions

    def get_jama_testcase_details(self):
        test_dir_details = self.basic_auth_client.get_item_children_query(
            self.testsuite_location, const.FOLDER_ITEM_JAMA_ID
        )

        for test_dir in test_dir_details:
            test_suite_dict = {}
            test_suite_details = self.basic_auth_client.get_item_children_query(
                test_dir["id"], const.FOLDER_ITEM_JAMA_ID
            )
            for test_suite in test_suite_details:
                testcase_dict = {}
                test_case_details = (
                    self.basic_auth_client.get_item_children_query(
                        test_suite["id"], const.TESTCASE_ITEM_JAMA_ID
                    )
                )

                for test_case in test_case_details:
                    testcase_dict[test_case["fields"]["name"]] = test_case["id"]

                test_suite_dict[test_suite["fields"]["name"]] = testcase_dict
                test_suite_dict[test_suite["fields"]["name"]][
                    "id"
                ] = test_suite["id"]

            self.testcase_lib[test_dir["fields"]["name"]] = test_suite_dict
            self.testcase_lib[test_dir["fields"]["name"]]["id"] = test_dir["id"]

        # update this location to the NAS location / or don't there is no need to store this file.
        with open(const.TESTCASE_LIB_FILE, "w") as lib_file:
            json.dump(self.testcase_lib, lib_file, indent=4)

    def create_test_case(self, testcase_details):
        """
        testcase_details = {"parent_location": "int",
                            "fields": dictionary of key:values for test_case}
        :param testcase_details:
        :return:
        """
        try:
            testcase_id = self.basic_auth_client.post_item(
                project=self.project_id,
                item_type_id=const.TESTCASE_ITEM_JAMA_ID,
                child_item_type_id=0,
                location={"item": testcase_details[const.PARENT_LOCATION]},
                fields=testcase_details[const.FIELDS],
            )
            self.logger.info(
                "Success : %s is created"
                % testcase_details[const.FIELDS][const.NAME]
            )
            self.logger.info("JAMA RESPONSE : %s" % testcase_id)

            return testcase_id

        except Exception as e:
            self.logger.error(e)
            self.logger.error(
                f"Error in creating the testcase : %s"
                % testcase_details[const.FIELDS][const.NAME]
            )
            self.logger.debug(e, exc_info=True)
            return None

    def update_test_case(self, testcase_details):
        """
        testcase_details = {"fields": dictionary of key:value for test_case,
                            "testcase_id": "int"}
        :param testcase_details:
        :return:
        """
        try:
            # parent id
            parent_id = self.basic_auth_client.get_parent_id(
                testcase_details["testcase_id"]
            )
            # item type id
            item_type = self.basic_auth_client.get_item_type_id(
                testcase_details["testcase_id"]
            )
            # update fields using item type
            testcase_details[const.FIELDS][
                const.PASSFAIL_CRITERIA % item_type
            ] = testcase_details[const.CRITERIA]
            testcase_details[const.FIELDS][
                const.SOURCE_CODE % item_type
            ] = testcase_details[const.SOURCE_CODE_URL]

            jama_response = self.basic_auth_client.put_item(
                project=self.project_id,
                item_id=testcase_details["testcase_id"],
                item_type_id=item_type,
                child_item_type_id=0,
                location={"item": parent_id},
                fields=testcase_details[const.FIELDS],
            )
            self.logger.info(
                "Success : %s is updated"
                % testcase_details[const.FIELDS][const.NAME]
            )
            self.logger.info("JAMA RESPONSE : %s" % jama_response)

        except Exception as e:
            self.logger.error(e)
            self.logger.error(
                "Error in updating the testcase : %s"
                % testcase_details[const.FIELDS][const.NAME]
            )
            self.logger.debug(e, exc_info=True)

    def update_manual_test_case(self, testcase_details):
        """
        testcase_details = {"fields": dictionary of key:value for test_case,
                            "testcase_id": "int"}
        :param testcase_details:
        :return:
        """
        try:
            parent_id = self.basic_auth_client.get_parent_id(
                testcase_details["testcase_id"]
            )

            item_type = self.basic_auth_client.get_item_type_id(
                testcase_details["testcase_id"]
            )

            testcase_details[const.FIELDS][
                const.OBJECT_TYPE % item_type
            ] = const.TEST_OBJECT_TYPE

            jama_response = self.basic_auth_client.put_item(
                project=self.project_id,
                item_id=testcase_details["testcase_id"],
                item_type_id=item_type,
                child_item_type_id=0,
                location={"item": parent_id},
                fields=testcase_details[const.FIELDS],
            )
            self.logger.info(
                "Success : %s is updated"
                % testcase_details[const.FIELDS][const.NAME]
            )
            self.logger.info("JAMA RESPONSE : %s" % jama_response)
        except Exception as e:
            self.logger.error(e)
            self.logger.error(
                "Error in updating the testcase : %s"
                % testcase_details[const.FIELDS][const.NAME]
            )
            self.logger.debug(e, exc_info=True)

    def create_test_cycle(self, test_cycle_details, start_date, end_date):
        """
        test_cycle_details = {"testplan_id": "int",
                              "name": "testcycle_name",
                              "test_group": "int"
                                }
        :param end_date:
        :param start_date:
        :param test_cycle_details:
        :return:
        """

        try:
            response = self.basic_auth_client.post_testplans_testcycles(
                testplan_id=test_cycle_details["testplan_id"],
                testcycle_name=test_cycle_details["name"],
                start_date=start_date,
                end_date=end_date,
                testgroups_to_include=test_cycle_details["test_group"],
            )

            self.logger.info(f"Testcycle {response} is created")

        except Exception as e:
            logger.jamalogger.warning("Error in creating Test Cycle")
            logger.jamalogger.error(e)
            raise Exception(
                "There is error in creating Testcycle. Please check plan id"
            )

        return response

    def update_test_run(self, testrun_details):
        """

        :param testrun_details: {"testrun_id": "int",
                                  "fields": dictionary of key:value for test_run
                                    }
        :return:
        """
        test_run_id = testrun_details["testrun_id"]
        data = {"fields": testrun_details["fields"]}
        try:
            self.basic_auth_client.put_test_run(test_run_id, json.dumps(data))

        except Exception as e:
            self.logger.warning(
                "Error in updating the Test run result for %s" % test_run_id
            )
            self.logger.error(e)
            self.logger.debug(e, exc_info=True)

    def get_test_group_id(self, test_plan_id):
        response = self.basic_auth_client.get_test_groups(test_plan_id)

        test_group_dict = {}

        for i in response:
            test_group_dict[i["name"]] = i["id"]

        return test_group_dict

    def get_test_cycle_details(self, test_plan_id):
        """
        get test cycle details for given test plan id
        param requirement_id : int(test_plan_id)
        return : test_cycle_list
        """
        response = self.basic_auth_client.get_test_cycles(test_plan_id)

        test_cycle_list = list()

        for i in response:
            test_cycle_dict = {}
            test_cycle_dict["id"] = i["id"]
            test_cycle_dict["name"] = i["fields"]["name"]
            test_cycle_list.append(test_cycle_dict)

        return test_cycle_list

    def create_test_group(self, test_plan_id, test_group_name):
        testgroup_dict = self.get_test_group_id(test_plan_id)

        if test_group_name not in testgroup_dict.keys():
            self.basic_auth_client.post_test_group(
                test_plan_id, test_group_name
            )

        test_group_ids = self.get_test_group_id(test_plan_id)
        test_group_id = test_group_ids[test_group_name]

        if test_group_id is not None:
            self.logger.info(
                f"Testgroup {test_group_id} is created under testplan {test_plan_id}"
            )

        return test_group_id

    def update_testgroup(self, testplan_id, testgroup_id, testcase_id_list):
        res = f"testplans/{testplan_id}/testgroups/{testgroup_id}/testcases"

        for i in testcase_id_list:
            data = {"testCase": i}
            response = self.core_auth_client.post(resource=res, json=data)
            status = response.json()["meta"]["status"]

            if status == "Created":
                self.logger.info(
                    f"Testcase {i} is added to testplan {testplan_id} "
                    f"under testgroup {testgroup_id}"
                )

            elif status == "Conflict":
                self.logger.info(response.json()["meta"]["message"])

    def get_testrun_id(self, test_cycle_id):
        response = self.basic_auth_client.get_testruns(
            test_cycle_id=test_cycle_id
        )

        test_run_testcase_dict = dict()
        for testrun in response:
            test_run_testcase_dict[testrun["fields"]["name"]] = testrun["id"]

        return test_run_testcase_dict

    def get_testcase_testrun_id(self, test_cycle_id):
        """
        get test run id for given test cycle
        param requirement_id : int(test_cycle_id)
        return : testcase_testrun_dict
        """

        response = self.basic_auth_client.get_testruns(
            test_cycle_id=test_cycle_id
        )

        testcase_testrun_dict = dict()
        for testrun in response:
            testcase_testrun_dict[testrun["fields"]["testCase"]] = testrun["id"]

        logger.jamalogger.info("Testrun id created")

        return testcase_testrun_dict

    # Relationship Functions
    def create_testcase_requirement_relationship(
        self, requirement_id, testcase_id
    ):
        """
        param requirement_id : int(requirement id)
        param testcase_id : int(test case id)
        return :
        """

        try:
            for req in requirement_id:
                self.basic_auth_client.post_relationship(
                    int(req), int(testcase_id), const.VERIFIED_BY
                )
                logger.jamalogger.info(
                    "Mapped %s : %s" % (requirement_id, testcase_id)
                )

        except Exception as e:
            self.logger.error(e)
            self.logger.debug(str(e), exc_info=True)

    def create_unittest_detaildesign_relationship(
        self, requirement_id, testcase_id
    ):
        """
        add relationship between unit-test id and detail-desing id
        param requirement_id : int(requirement id)
        param testcase_id : int(test case id)
        return :
        """

        try:
            self.basic_auth_client.post_relationship(
                int(requirement_id), int(testcase_id), const.VERIFIED_BY
            )
            logger.jamalogger.info(
                "Mapped %s : %s" % (requirement_id, testcase_id)
            )

        except Exception as e:
            self.logger.error(e)
            self.logger.debug(str(e), exc_info=True)

    def create_detaildesign_architectural_relationship(
        self, requirement_id, testcase_id
    ):
        """
        add relationship between detail-desing id and architectural id
        param requirement_id : int(requirement id)
        param testcase_id : int(test case id)
        return :
        """

        try:
            self.basic_auth_client.post_relationship(
                int(requirement_id), int(testcase_id), const.VERIFIED_BY
            )
            logger.jamalogger.info(
                "Mapped %s : %s" % (requirement_id, testcase_id)
            )

        except Exception as e:
            self.logger.error(e)
            self.logger.debug(str(e), exc_info=True)

    def update_detaildesign(self, requirement_details):
        """
        requirement_details : {"fields": dictionary of key:values for requirements}
        param requirement_details:
        :return:
        """
        try:
            parent_id = self.basic_auth_client.get_parent_id(
                requirement_details["req_id"]
            )
            jama_response = self.basic_auth_client.put_item(
                project=self.project_id,
                item_id=requirement_details["req_id"],
                item_type_id=const.DETAIL_DESIGN_ITEM_JAM_ID,
                child_item_type_id=0,
                location={"item": parent_id},
                fields=requirement_details[const.FIELDS],
            )
            self.logger.info(
                "Success : %s is updated"
                % requirement_details[const.FIELDS][const.NAME]
            )
            self.logger.info("JAMA RESPONSE : %s" % jama_response)
        except Exception as e:
            self.logger.error(e)
            self.logger.error(
                "Error in updating the testcase : %s"
                % requirement_details[const.FIELDS][const.NAME]
            )
            self.logger.debug(e, exc_info=True)

    def update_unit_test_case(self, testcase_details):
        """
        testcase_details = {"fields": dictionary of key:value for test_case}
        :return:
        """
        try:
            parent_id = self.basic_auth_client.get_parent_id(
                testcase_details["testcase_id"]
            )
            jama_response = self.basic_auth_client.put_item(
                project=self.project_id,
                item_id=testcase_details["testcase_id"],
                item_type_id=const.UNIT_TESTCASE_ITEM_JAMA_ID,
                child_item_type_id=0,
                location={"item": parent_id},
                fields=testcase_details[const.FIELDS],
            )
            self.logger.info(
                "Success : %s is updated"
                % testcase_details[const.FIELDS][const.NAME]
            )
            self.logger.info("JAMA RESPONSE : %s" % jama_response)

        except Exception as e:
            self.logger.error(e)
            self.logger.error(
                "Error in updating the testcase : %s"
                % testcase_details[const.FIELDS][const.NAME]
            )
            self.logger.debug(e, exc_info=True)

    def find_files(self, dir, suffix):
        """
        find all files with matched suffix in directory
        param: dir, suffix
        return: list of matched files
        """

        filenames = os.listdir(dir)

        return [filename for filename in filenames if filename.endswith(suffix)]

    def get_items_upstream_relationship(self, item_id):
        """
        get the upstream relationship id
        param item_id : int(test case id)
        return : relationship_id
        """
        relationship_id = (
            self.basic_auth_client.get_items_upstream_relationships(item_id)
        )
        return relationship_id

    def delete_relationship(self, rel_id):
        """
        delete relationship between test and requirement for given relationship id
        param rel_id : int(relationship id)
        """
        return self.basic_auth_client.delete_relationships(rel_id)

    def get_latest_test_steps_in_test_run(self, run_id):
        """
        This method will update a test run with latest test steps from test case
        param rel_id : int(run id)
        """
        try:
            self.basic_auth_client.updated_test_case(run_id)
        except Exception as e:
            pass

    def get_test_detail(self, item_id):
        """
        This method will read and return all details for given id 
        param rel_id : int(relationship id)
        return : details in dict format
        """
        return self.basic_auth_client.get_test_details(item_id)

if __name__ == "__main__":
    # Once the config file is set, this script when ran should run error free
    jama_obj = JamaLib()
