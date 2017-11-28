"""Look through directory tree for unit test cases to run.
Comparable to command-line functionality:

python -m unittest discover -v -s <directoryName> -p "Test*.py"

"""

import unittest
import logging

# Set logging level.
log = logging.getLogger("CDSS")

# TODO(sbala): Fix TestDataManager.test_compositeRelated
# TODO(sbala): Fix TestSTRIDEOrderMedConversion.test_dataConversion_denormalized

# Load test suite.
loader = unittest.TestLoader()
suite = loader.discover('.', pattern="Test*.py")
log.setLevel(logging.ERROR)

# Run test suite.
testRunner = unittest.runner.TextTestRunner(verbosity=1)
testRunner.run(suite)
