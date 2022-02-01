# Copyright Atharv Kolhar (amkolhar)

"""
Jama Library
"""

import logging
import warnings

from py_jama_rest_client.client import JamaClient

import data.constants as const
from data import config

warnings.filterwarnings("ignore")

logger = logging.getLogger("JAMALIB")
logger.setLevel(logging.INFO)

handle = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                              "%Y-%m-%d %H:%M:%S")
handle.setFormatter(formatter)
handle.setLevel(logging.INFO)
logger.addHandler(handle)

log_handle = logging.FileHandler("JamaAutomation_log.txt")
log_handle.setFormatter(formatter)
log_handle.setLevel(logging.INFO)
logger.addHandler(log_handle)


class JamaLib:
    def __init__(self):
        self.basic_auth_client = JamaClient(config.CONFIG[const.COMPANY_JAMA_URL],
                                            credentials=(config.CONFIG[const.USERNAME],
                                                         config.CONFIG[const.PASSWORD]),
                                            oauth=True)
        self.project = config.CONFIG[const.PROJECT]
        self.assigned_to = config.CONFIG[const.ASSIGNED_TO]
        self.testcase_ids = {}

    def create_test_case(self, testcase_details):
        try:
            jama_response = self.basic_auth_client.post_item(project=self.project,
                                                             item_type_id=config.ITEM_IDS[const.TESTCASE_ITEM_ID],
                                                             child_item_type_id=0,
                                                             location={
                                                                 "item": config.TESTSUITE_LOCATION[
                                                                     testcase_details[const.TESTSUITE_NAME]]},
                                                             fields=testcase_details[const.FIELDS])
            self.testcase_ids[testcase_details[const.TESTSUITE_NAME]][const.FIELDS[const.NAME]] = jama_response
            logger.info("Success : %s is created" % const.FIELDS[const.NAME])

        except Exception as e:
            logger.error(e)
            logger.error("Error in creating the testcase : %s" % const.FIELDS[const.NAME])

    def update_test_case(self, testcase_details):
        try:
            jama_response = self.basic_auth_client.put_item(project=self.project,
                                                            item_id=testcase_details[const.TESTCASE_ID],
                                                            item_type_id=config.ITEM_IDS[const.TESTCASE_ITEM_ID],
                                                            child_item_type_id=0,
                                                            location={
                                                                "item": config.TESTSUITE_LOCATION[
                                                                    testcase_details[const.TESTSUITE_NAME]]},
                                                            fields=testcase_details[const.FIELDS])
            self.testcase_ids[testcase_details[const.TESTSUITE_NAME]][const.FIELDS[const.NAME]] = jama_response
            logger.info("Success : %s is created" % const.FIELDS[const.NAME])

        except Exception as e:
            logger.error(e)
            logger.error("Error in updating the testcase : %s" % const.FIELDS[const.NAME])


if __name__ == '__main__':
    # Once the config file is set, this script when ran should run error free
    jama_obj = JamaLib()
