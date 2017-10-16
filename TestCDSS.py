import unittest
import logging

# Set logging level.
log = logging.getLogger("CDSS")

# TODO(sbala): Complete implementation by enabling differential logging levels.
# Move logging level settings to the application logic, away from the TestCases.
# To do this, call the application name from each of the end test cases as the
# logger name. Then set the logging level in the actual __main__ function for
# the relevant test suite.
#
# Check on each individual test module...
# medinfo.cpoe
# medinfo.dataconversion

# Load test suite.
loader = unittest.TestLoader()
suite = loader.discover('./medinfo/dataconversion', pattern="Test*.py")
log.setLevel(logging.ERROR)

# Run test suite.
testRunner = unittest.runner.TextTestRunner(verbosity=2)
testRunner.run(suite)
