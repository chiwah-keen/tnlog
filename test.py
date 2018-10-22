from log import TNLog
import unittest
log = TNLog()
log.init(logname="test", logpath="./", log_level="DEBUG")


class Test(unittest.TestCase):

    def test_01(self):
        log.info("123")

    def test_02(self):
        log.info('wewe')

if __name__ == '__main__':
    unittest.main()
