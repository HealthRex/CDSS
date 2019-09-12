"""
Look through directory tree for unit test cases to run.
Comparable to command-line functionality:

python -m unittest discover -v -s <directoryName> -p "Test*.py"
"""

import unittest
import logging

import os

# if __name__ == "__main__":
# Set logging level.
log = logging.getLogger("CDSS")
log.setLevel(logging.CRITICAL)

# Load test suite.
# TODO(sbala): Prevent test suite from running twice.
# For some reason, the entire test suite runs on loader.discover().
# Already ruled out hypotheses that this is due to invoking python interpreter
# in individual test files or calling test suite in main() functions.
loader = unittest.TestLoader()
suite = loader.discover('.', pattern="Test*.py")

# Run test suite.
testRunner = unittest.runner.TextTestRunner(verbosity=1)
testRunner.run(suite)
