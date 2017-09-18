
import unittest
from medinfo.common.ProcessManager import *
from Const import RUNNER_VERBOSITY

class TestProcessManager():
    def setUp(self):
        print "Setting up"

    def test_Method(self):
        print "Running test_Method"

    def test_parseArgList(self):
        pass

    def test_update(self):
        pass

    def test_pollProcesses(self):
        pass




def suite():
    suite = unittest.TestSuite()
    instance = TestProcessManager()
    suite.addTest(instance.test_Method())
    return suite

if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
