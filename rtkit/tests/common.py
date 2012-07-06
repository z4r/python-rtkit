from multiprocessing import Process
import unittest2 as unittest
import time


class TestCaseWithFlask(unittest.TestCase):
    application = NotImplemented

    @classmethod
    def setUpClass(cls):
        cls.server = Process(target=cls.application.run)
        cls.server.start()
        time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        cls.server.terminate()
        cls.server.join()
