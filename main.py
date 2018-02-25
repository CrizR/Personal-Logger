import logging
import sys

from src.controller import MonkController

HOST = 'localhost'
PORT = 27017

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(message)s',
                        datefmt="%Y-%m-%d %H:%M:%S")
    if len(sys.argv) > 1:
        MonkController().run(HOST, PORT)
    else:
        logging.error("Invalid Number of Arguments")





