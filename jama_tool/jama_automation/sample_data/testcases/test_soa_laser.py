
"""
Test suite for ICSM related tests

Execute test from command line:
# bazel test //aeva/sw_tests_ci/tests/ar2:test_soa_laser --test_tag_filters=ci
# add --test_output=all to see logs for non-failed tests in console
# add --test_arg=--iterations=10 to increase the iteration default=3
"""

import argparse
import sys
import unittest

import aeva.py_sensor.lib.aeries_constants as ae_const
from aeva.sw_tests_ci.lib.ar2.ar2_test_case import AR2TestCase
from aeva.sw_tests_ci.lib.base_test_case import has_subtests


class AR2TestSoaLaser(AR2TestCase):
    """Test suite for ICSM related tests"""

    point_cloud_check = False
    soa_laser_iterations = 3

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # ICSM node is not present in PROD mode
        if cls.is_icsm and not cls.is_unit_in_prod_mode():
            cls.initial_soa_tec_temperature = cls.sensor.reconfig_get_value(
                ae_const.ICSM_NODE, ae_const.RECONFIG_SOA_TEC_TEMP
            )
            cls.initial_laser_tec_temperature = cls.sensor.reconfig_get_value(
                ae_const.ICSM_NODE, ae_const.RECONFIG_LASER_TEC_TEMP
            )
            cls.initial_modulation = cls.sensor.reconfig_get_value(
                ae_const.ICSM_NODE, ae_const.ENABLE_MODULATION
            )
            cls.initial_hfov = cls.sensor.reconfig_get_value(
                ae_const.SCANNER_NODE, ae_const.SCANNER_HFOV
            )
            (
                cls._initial_laser_state,
                cls._initial_soa_state,
            ) = cls.sensor.icsm.get_soa_laser_enable_state()
            (
                cls.initial_soa_current,
                cls.initial_laser_current,
            ) = cls.sensor.icsm.get_soa_laser_current()
            cls.initial_tuning_algo_state = cls.sensor.reconfig_get_value(
                ae_const.ICSM_NODE, ae_const.ENABLE_LASER_ALGO
            )
            cls.sensor.reconfig_change_value_with_retries(
                ae_const.ICSM_NODE, ae_const.ENABLE_LASER_ALGO, False
            )
            cls.initial_enable_soa_tec = cls.sensor.reconfig_get_value(
                ae_const.ICSM_NODE, ae_const.ENABLE_SOA_TEC
            )

    def setUp(self):
        super().setUp()
        self.wait_for_all_health_errors_to_clear()
        self.sensor.reconfig_change_value_with_retries(
            ae_const.ICSM_NODE,
            ae_const.ENABLE_MODULATION,
            ae_const.BASIC_MODULATION,
        )

    def tearDown(self):
        if self.is_icsm and not self.is_unit_in_prod_mode():
            self.sensor.reconfig_change_value_with_retries(
                ae_const.ICSM_NODE,
                ae_const.ENABLE_SOA_TEC,
                self.initial_enable_soa_tec,
            )
            self.sensor.icsm.set_soa_laser_state(
                self._initial_soa_state, self._initial_laser_state
            )
            self.sensor.icsm.set_soa_laser_current(
                self.initial_soa_current, self.initial_laser_current
            )

            self.sensor.reconfig_change_value_with_retries(
                ae_const.ICSM_NODE,
                ae_const.ENABLE_MODULATION,
                self.initial_modulation,
            )
            self.sensor.reconfig_change_value_with_retries(
                ae_const.SCANNER_NODE, ae_const.SCANNER_HFOV, self.initial_hfov
            )
            self.sensor.reconfig_change_value_with_retries(
                ae_const.IFM_NODE, ae_const.ENABLE_LASER_PLL_RECOVERY, True
            )

        super().tearDown()

    @classmethod
    def tearDownClass(cls):
        cls.sensor.reconfig_change_value_with_retries(
            ae_const.ICSM_NODE,
            ae_const.ENABLE_LASER_ALGO,
            cls.initial_tuning_algo_state,
        )
        super().tearDownClass()

    def check_soa_current(self, exp_current, soa):
        self.sensor.reconfig_change_value_with_retries(
            ae_const.ICSM_NODE, ae_const.SOA_RECONFIG_CURRENT % soa, exp_current
        )

        self.check_soa_current_amp(soa)

    def check_laser_current(self, exp_current, laser):
        self.sensor.reconfig_change_value_with_retries(
            ae_const.ICSM_NODE,
            ae_const.LASER_RECONFIG_CURRENT[laser],
            exp_current,
        )

        self.check_laser_current_amp(laser)

    def check_soa_tec_temperature_status(self):
        soa_tec_temp_good = self.sensor.api_if.get_telemetry_value(
            ae_const.ICSM_NODE, ae_const.SOA_TEC_TEMP_GOOD
        )

        self.assertEqual(
            ae_const.TEC_TEMP_GOOD,
            soa_tec_temp_good,
            msg="Incorrect TEC temperature status reported.\nExpected: %s\nActual: %s"
            % (ae_const.TEC_TEMP_GOOD, soa_tec_temp_good),
        )

    def check_soa_tec_temperature(self, exp_temp):
        soa_tec_temp = self.sensor.api_if.get_telemetry_value(
            ae_const.ICSM_NODE, ae_const.TELEM_SOA_TEC_TEMP
        )

        self.assertAlmostEquals(
            exp_temp,
            soa_tec_temp,
            delta=ae_const.TEC_TEMP_THRESHOLD,
            msg="SOA TEC Temperature:\n"
            "Expected: %s\n"
            "Actual: %s" % (exp_temp, soa_tec_temp),
        )

    def check_laser_tec_temperature_status(self):
        laser_tec_temp_good = self.sensor.api_if.get_telemetry_value(
            ae_const.ICSM_NODE, ae_const.LASER_TEC_TEMP_GOOD
        )

        self.assertEqual(
            ae_const.TEC_TEMP_GOOD,
            laser_tec_temp_good,
            msg="Incorrect TEC temperature status reported.\nExpected: %s\nActual: %s"
            % (ae_const.TEC_TEMP_GOOD, laser_tec_temp_good),
        )

    def check_laser_tec_temperature(self, exp_temp):
        laser_tec_temp = self.sensor.api_if.get_telemetry_value(
            ae_const.ICSM_NODE, ae_const.TELEM_LASER_TEC_TEMP
        )

        self.assertAlmostEquals(
            exp_temp,
            laser_tec_temp,
            delta=ae_const.TEC_TEMP_THRESHOLD,
            msg="SOA TEC Temperature:\n"
            "Expected: %s\n"
            "Actual: %s" % (exp_temp, laser_tec_temp),
        )

    def check_max_laser_curr_value(self, max_laser_curr, laser_curr):
        """Validate if the laser current maximum value in the manifest is equal to 0.4 A +-0.001 delta"""
        self.assertAlmostEqual(
            max_laser_curr,
            ae_const.LASER_CURR_MAX_VALUE,
            delta=0.001,
            msg="Max Value for %s \n Expected Value: %s, Actual Value: %s"
            % (laser_curr, ae_const.LASER_CURR_MAX_VALUE, max_laser_curr),
        )

    @has_subtests
    # @jira_tag: https://aevainc.atlassian.net/browse/EVE-8830
    # @test_type: Functional
    # @component: ICSM-MCU
    # @requirement_id: 148412
    def test_soa_enable_disable(self):
        """
        Description:
        Test case to validate the SOA Enable and Disable functionality
        1. Disable all the SOAs
        2. Disable Modulation
        3. Enable each SOA
        4. Check for SOA Debug Current in telemetry
        5. Disable each SOA
        6. Check for SOA Debug Current in telemetry

        """

        self.set_soa_all_disabled()
        self.set_laser_enabled()
        self.sensor.reconfig_change_value_with_retries(
            ae_const.ICSM_NODE,
            ae_const.ENABLE_MODULATION,
            ae_const.DISABLED_MODULATION,
        )

        for iteration in range(self.soa_laser_iterations):
            for soa in range(self.sensor.icsm.SOA_NUM):
                self.sensor.reconfig_change_value_with_retries(
                    ae_const.ICSM_NODE, ae_const.SOA_ENABLE % soa, True
                )
                self.sensor.reconfig_change_value_with_retries(
                    ae_const.ICSM_NODE, ae_const.SOA_RECONFIG_CURRENT % soa, 0.5
                )
                self.sub_test_function(
                    self.soa_control,
                    "SOA_%s_control_to_%s_%s" % (soa, True, iteration),
                    False,
                    False,
                    False,
                    soa,
                    True,
                )
                self.sub_test_function(
                    self.soa_control,
                    "SOA_%s_control_to_%s_%s" % (soa, False, iteration),
                    False,
                    False,
                    False,
                    soa,
                    False,
                )

    @has_subtests
    # @jira_tag: https://aevainc.atlassian.net/browse/EVE-8830
    # @test_type: Functional
    # @component: ICSM-MCU
    # @requirement_id: 148405
    def test_laser_enable_disable(self):
        """
        Description:
        Test case to validate the Laser Enable and Disable functionality
        1. Disable both the Lasers
        2. Enable each Laser
        3. Check for Laser Current in telemetry
        5. Disable each Laser
        6. Check for Laser Current in telemetry

        """

        for iteration in range(self.soa_laser_iterations):
            # Enable both the Lasers and Check the Current
            self.check_laser_all_control(True, iteration)

            # Disable both the Lasers and Check the Current
            self.check_laser_all_control(False, iteration)

    @has_subtests
    # @jira_tag: https://aevainc.atlassian.net/browse/EVE-8830
    # @test_type: Functional
    # @component: ICSM-MCU
    # @requirement_id: 148406
    def test_soa_current_change(self):
        """
        Description:
        Test case to validate the SOA current change functionality
        1. Disable all SOAs
        2. Disable Modulation
        3. Enable one SOA and change the current in reconfig
        4. Validate the changed current in the telemetry
        5. Disable the SOA
        6. Repeat the step 3 and 4 for all the SOA
        """

        self.set_soa_all_disabled()
        self.sensor.reconfig_change_value_with_retries(
            ae_const.ICSM_NODE,
            ae_const.ENABLE_MODULATION,
            ae_const.DISABLED_MODULATION,
        )

        for soa in range(self.sensor.icsm.SOA_NUM):
            self.sensor.reconfig_change_value_with_retries(
                ae_const.ICSM_NODE, ae_const.SOA_ENABLE % soa, True
            )

            min_curr = float(
                self.sensor.manifest[ae_const.ICSM_NODE][
                    ae_const.SOA_RECONFIG_CURRENT % soa
                ]["min"]
            )
            max_curr = float(
                self.sensor.manifest[ae_const.ICSM_NODE][
                    ae_const.SOA_RECONFIG_CURRENT % soa
                ]["max"]
            )
            mean_curr = (min_curr + max_curr) / 2

            exp_currents = [min_curr, mean_curr, max_curr]

            for exp_curr in exp_currents:
                self.sub_test_function(
                    self.check_soa_current,
                    "SOA_current_%s_%s_amps" % (soa, exp_curr),
                    False,
                    False,
                    False,
                    exp_curr,
                    soa,
                )

            self.sensor.reconfig_change_value_with_retries(
                ae_const.ICSM_NODE,
                ae_const.SOA_RECONFIG_CURRENT % soa,
                self.initial_soa_current[soa],
            )
            self.sensor.reconfig_change_value_with_retries(
                ae_const.ICSM_NODE, ae_const.SOA_ENABLE % soa, False
            )

    @has_subtests
    # @jira_tag: https://aevainc.atlassian.net/browse/EVE-8830
    # @test_type: Functional
    # @component: ICSM-MCU
    # @requirement_id: 148407
    def test_laser_current_change(self):
        """
        Description:
        Test case to validate the Laser current change functionality
        1. Change the Laser current in reconfig
        2. Validate the changed current in the telemetry
        3. Repeat the step 1 and 2 for other Laser

        """
        for laser in range(len(ae_const.LASER_RECONFIG_CURRENT)):
            self.sensor.reconfig_change_value_with_retries(
                ae_const.ICSM_NODE, ae_const.LASER_ENABLE[laser], True
            )

            min_curr = float(
                self.sensor.manifest[ae_const.ICSM_NODE][
                    ae_const.LASER_RECONFIG_CURRENT[laser]
                ]["min"]
            )
            max_curr = float(
                self.sensor.manifest[ae_const.ICSM_NODE][
                    ae_const.LASER_RECONFIG_CURRENT[laser]
                ]["max"]
            )

            mean_curr = (min_curr + max_curr) / 2

            exp_currents = [min_curr, mean_curr, max_curr]
            for exp_curr in exp_currents:
                self.sub_test_function(
                    self.check_laser_current,
                    "Laser_current_%s_%s_amp" % (laser, exp_curr),
                    False,
                    False,
                    False,
                    exp_curr,
                    laser,
                )

    @classmethod
    def parse_extra_args(cls, parser: argparse.ArgumentParser):
        super(AR2TestSoaLaser, cls).parse_extra_args(parser)
        parser.add_argument(
            "--iterations",
            type=int,
            required=False,
            default=0,
            help="Number of iterations to run.",
        )


if __name__ == "__main__":
    parsed_args, remaining_args = AR2TestSoaLaser.create_parser_and_parse_args()
    if parsed_args.iterations:
        AR2TestSoaLaser.soa_laser_iterations = parsed_args.iterations
    unittest.main(argv=(sys.argv[:1] + remaining_args))
