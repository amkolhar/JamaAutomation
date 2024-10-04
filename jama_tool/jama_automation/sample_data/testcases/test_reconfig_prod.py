
""" Test suite for production mode tests
# bazel test //aeva/sw_tests_ci/tests/ar2:test_reconfig_prod --test_tag_filters=ci
# add --test_output=all to see logs for non-failed tests in console
"""

import sys
import unittest

import aeva.py_sensor.lib.constants as const
from aeva.py_sensor.lib import aeries_constants as ae_const
from aeva.sw_tests_ci.lib.ar2.reconfig_test_case import AR2ReconfigTestCase


class TestAR2ReconfigProdMode(AR2ReconfigTestCase):
    """
    Test suite for production mode reconfig tests

    This test suite switches unit to PROD mode with sync option for B1
    then resets the unit back to DEV after executing tests.
    Tests for A2 will be skipped if unit found in DEV mode
    due to limitations on mode switch for A2 units.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.is_prod = cls.is_unit_in_prod_mode()
        if not cls.is_prod:
            cls.logger.info("Switching unit to PROD mode...")
            # move directly to tearDownClass if mode switch fails
            try:
                cls.sensor.set_operation_mode("-CS", "PROD")
                cls.sensor.api_py.restart_sensor()
                cls.is_prod = cls.is_unit_in_prod_mode()
                cls.sensor.reset_api_connection()
            except Exception as err:
                cls.logger.error(
                    "Error switching mode, restoring backups..."
                    "\nError details:\n%s.",
                    err,
                )
        if cls.sensor_sku == ae_const.AR2_NARROW_FOV_FORCED_AIR_SINK:
            cls.sensor.reconfig_change_value_with_retries(
                ae_const.SYSCONFIG_NODE,
                ae_const.SYSCONFIG_RANGE_MODES,
                ae_const.SYSCONFIG_RANGE_MODE_NORMAL_RANGE,
            )
            cls.sensor.reconfig_perform_action(
                ae_const.SYSCONFIG_NODE, const.RECONFIG_SAVE_NODE, retries=3
            )

    @classmethod
    def tearDownClass(cls):
        """Switch mode back to DEV and restart apps"""
        # only switch if unit was in non-prod mode before test
        if not cls.is_prod:
            cls.logger.info("Switching unit back to DEV mode...")
            cls.sensor.set_operation_mode("-C", "DEV")
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.skip_test_for_non_prod()

    # Test exposed in production mode reconfig / telemetry options
    # @test_type: Functional
    # @component: Platform
    # @requirement_id: 148413
    def test_verify_reconfig_options_prod(self):
        """
        Description:
        Verify only production reconfig is available
        and there are no missing nodes / options in reconfig"""
        self.verify_reconfig_options_prod()

    # @test_type: Functional
    # @component: Platform
    # @requirement_id: 148414
    def test_verify_telemetry_options_prod(self):
        """
        Description:
        Verify only production telemetry is available"""
        self.verify_telemetry_options()

    # @test_type: Functional
    # @component: Platform
    # @requirement_id: 148411
    def test_range_mode_switch_prod(self):
        """
        Description:
        Verify that user can change range pattern
        1. Iterate through the available range modes.
        2. Verify that the user can change the mode and check the updated mode on the telemetry
        3. Verify that there are no error codes seen in heakth node for each mode
        """
        self.check_range_mode_switch()


if __name__ == "__main__":
    (
        parsed_args,
        remaining_args,
    ) = TestAR2ReconfigProdMode.create_parser_and_parse_args()
    unittest.main(argv=(sys.argv[:1] + remaining_args))
