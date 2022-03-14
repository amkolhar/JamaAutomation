# Copyright Atharv Kolhar (amkolhar)

"""
Jama Library
"""

import json

import JamaAutomation.data.constants as const
from JamaAutomation.data import config
from JamaAutomation.lib import logger
from JamaAutomation.py_jama_rest_client.client import JamaClient
from JamaAutomation.py_jama_rest_client.core import Core


def text_to_rich_text(text):
    rich_text = "<p>%s</p>\n\n" % text

    return rich_text


class JamaLib:
    def __init__(self):
        self.basic_auth_client = JamaClient(config.CONFIG[const.COMPANY_JAMA_URL],
                                            credentials=(config.CONFIG[const.USERNAME],
                                                         config.CONFIG[const.PASSWORD]),
                                            oauth=True)
        self.core_auth_client = Core(config.CONFIG[const.COMPANY_JAMA_URL],
                                     user_credentials=(config.CONFIG[const.USERNAME],
                                                       config.CONFIG[const.PASSWORD]),
                                     oauth=True)
        self.project = config.CONFIG[const.PROJECT]
        self.assigned_to = config.CONFIG[const.ASSIGNED_TO]
        self.testcase_ids = {}
        self.testsuite_location = config.TESTSUITE_LOCATION
        self.logger = logger.jamalogger

    def create_folder(self, folder_details):
        """
        folder_details = {"parent_location": "int",
                          "child_item_id" : "int",
                          "fields": {"name":"folder name", any other key:value needed for folder}}
        :param folder_details:
        :return:
        """
        folder_api_id = self.basic_auth_client.post_item(project=self.project,
                                                         item_type_id=config.ITEM_IDS[const.FOLDER_ITEM_ID],
                                                         child_item_type_id=folder_details["child_item_id"],
                                                         location={"item": folder_details[const.PARENT_LOCATION]},
                                                         fields=folder_details[const.FIELDS])
        self.logger.info("Folder %s is created" % folder_details[const.FIELDS][const.NAME])

        return folder_api_id

    def create_test_case(self, testcase_details):
        """
        testcase_details = {"parent_location": "int",
                            "fields": dictionary of key:values for test_case}
        :param testcase_details:
        :return:
        """
        try:
            testcase_id = self.basic_auth_client.post_item(project=self.project,
                                                           item_type_id=config.ITEM_IDS[const.TESTCASE_ITEM_ID],
                                                           child_item_type_id=0,
                                                           location={
                                                               "item": testcase_details[const.PARENT_LOCATION]},
                                                           fields=testcase_details[const.FIELDS])
            self.logger.info("Success : %s is created" % testcase_details[const.FIELDS][const.NAME])
            self.logger.info("JAMA RESPONSE : %s" % testcase_id)

            return testcase_id

        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"Error in creating the testcase : %s" % testcase_details[const.FIELDS][const.NAME])
            self.logger.debug(e, exc_info=True)
            return None

    def update_test_case(self, testcase_details):
        """
        testcase_details = {"parent_location": "int",
                            "fields": dictionary of key:value for test_case,
                            "testcase_id": "int"}
        :param testcase_details:
        :return:
        """
        try:
            jama_response = self.basic_auth_client.put_item(project=self.project,
                                                            item_id=testcase_details[const.TESTCASE_ID],
                                                            item_type_id=config.ITEM_IDS[const.TESTCASE_ITEM_ID],
                                                            child_item_type_id=0,
                                                            location={
                                                                "item": testcase_details[const.PARENT_LOCATION]},
                                                            fields=testcase_details[const.FIELDS])
            self.logger.info("Success : %s is updated" % testcase_details[const.FIELDS][const.NAME])
            self.logger.info("JAMA RESPONSE : %s" % jama_response)

        except Exception as e:
            self.logger.error(e)
            self.logger.error("Error in updating the testcase : %s" % testcase_details[const.FIELDS][const.NAME])
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
            response = self.basic_auth_client.post_testplans_testcycles(testplan_id=test_cycle_details["testplan_id"],
                                                                        testcycle_name=test_cycle_details["name"],
                                                                        start_date=start_date,
                                                                        end_date=end_date,
                                                                        testgroups_to_include=
                                                                        test_cycle_details["test_group"])

            self.logger.info(f"Testcycle id: {response}")

        except Exception as e:
            logger.jamalogger.warning("Error in creating Test Cycle")
            logger.jamalogger.error(e)
            raise Exception("There is error in creating Testcycle. Please check plan id")

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
            self.logger.warning("Error in updating the Test run result for %s" % test_run_id)
            self.logger.error(e)
            self.logger.debug(e, exc_info=True)

    def get_test_group_id(self, test_plan_id):
        response = self.basic_auth_client.get_test_groups(test_plan_id)

        test_group_dict = {}

        for i in response:
            test_group_dict[i["name"]] = i["id"]

        return test_group_dict

    def create_test_group(self, test_plan_id, test_group_name):

        testgroup_dict = self.get_test_group_id(test_plan_id)

        if test_group_name not in testgroup_dict.keys():
            self.basic_auth_client.post_test_group(test_plan_id, test_group_name)

    def update_testgroup(self, testplan_id, testgroup_id, testcase_id_list):
        res = f'testplans/{testplan_id}/testgroups/{testgroup_id}/testcases'

        for i in testcase_id_list:
            data = {"testCase": i}
            response = self.core_auth_client.post(resource=res, json=data)
            status = response.json()["meta"]["status"]

            if status == "Created":
                self.logger.info(f"Testcase {i} is added to testplan {testplan_id} "
                                 f"under testgroup {testgroup_id}")

            elif status == "Conflict":
                self.logger.info(response.json()["meta"]["message"])

    def get_testrun_id(self, test_cycle_id):

        response = self.basic_auth_client.get_testruns(test_cycle_id=test_cycle_id)

        test_run_testcase_dict = dict()
        for testrun in response:
            test_run_testcase_dict[testrun["fields"]["name"]] = testrun["id"]

        return test_run_testcase_dict

    def create_testcase_requirement_relationship(self, requirement_id, testcase_id):

        try:
            self.basic_auth_client.post_relationship(int(requirement_id), int(testcase_id), config.VERIFIED_BY)
            logger.jamalogger.info("Mapped %s : %s" % (requirement_id, testcase_id))

        except Exception as e:
            self.logger.error(e)
            self.logger.debug(str(e), exc_info=True)


if __name__ == '__main__':
    # Once the config file is set, this script when ran should run error free
    jama_obj = JamaLib()
