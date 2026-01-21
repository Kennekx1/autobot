import logging

class BaseBot:
    def __init__(self, name: str):
        self.name = name
        self.logger = self._setup_logger()

    def _setup_logger(self):
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def run(self):
        raise NotImplementedError("Each bot must implement its own run method.")
