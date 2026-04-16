from loguru import logger

class LoguruLogger():
    def __init__(self):
        pass

    def info(self, msg:str):
        logger.info(msg)
    
    def debug(self, msg:str):
        logger.debug(msg)

    def exception(self, msg:str):
        logger.exception(msg)