import logging
import sys
import subprocess
import os

from src.controller.controller import MonkController

HOST = 'localhost'
PORT = 27017

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(message)s',
                        datefmt="%Y-%m-%d %H:%M:%S")
    if len(sys.argv) > 1:
        MonkController().run(HOST, PORT)
    else:
        print("\n\n____________Welcome to Monk____________")
        print("| A simple, personalized, logging tool |")
        print("|                                      |")
        print("|       use --help to learn more       |")
        print("|______________________________________|\n\n")





