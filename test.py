from log import TNLog
log = TNLog()
log.init(logname="test", logpath="./", log_level="DEBUG")

class Test():
    def __init__(self):
        log.info('Test ....')

    def logTest(self):
        log.info("123")

if __name__ == '__main__':
    t = Test()
    t.logTest()
