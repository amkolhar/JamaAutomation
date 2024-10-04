# JamaAutomation

## File Structure

- JamaAutomation
  - data
    - config.py
      - Configuration file to setup the JamaAutomation Tool
    - constants.py
      - Tool Constants
  - lib
    - JamaLib.py
      - Reused from https://github.com/amkolhar/JamaAutomation
      - Contains functions which are needed for the tool
    - logger.py
      - Logger for the tool
    - py_jama_rest_client
        - client.py
        - core.py
- lib
  - testcase_operation.py
    - bazel run JamaAutomation/lib:testcase_operation -- --automated_testcase=(directory path for testcase)
    - bazel run JamaAutomation/lib:testcase_operation -- --automated_testcase=aeva/sw_test_ci/test
  - testexecution_operation.py
    - bazel run JamaAutomation/lib:testexecution_operation -- --test_report=(.csv test report file address) --test_plan=(Testplan ID for the release from the JAMA)
- jama_runner.py
  - bazel run JamaAutomation:jama_runner -- --automated_testcase=(directory path for testcase) --test_report=(.csv test report file address) --test_plan=(Testplan ID for the release from the JAMA)