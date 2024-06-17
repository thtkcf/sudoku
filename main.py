import logging
import logging.config

from ui import App

if __name__ == "__main__":
    logging.config.fileConfig("logging.conf")
    logging.info("Running app")
    App().start()
