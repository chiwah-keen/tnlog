from log import TNLog
log = TNLog()
log.init(logname="test", logpath="./", log_level="DEBUG")

class Test():
    def __init__(self):
        log.info('Test ....')

    def logTest():
        log

if __name__ == '__main__':
    t = Test()
