import argparse
import logging

from src.model.monk_client import MonkClient


class MonkController(object):

    def run(self, host, port):
        argv = self.parse_args()
        mc = MonkClient(host, port)
        if argv.c or argv.e or argv.ed:
            mc.update_progress(argv)

        if argv.dinner:
            mc.log_meal("dinner", argv.dinner.split(","))

        if argv.lunch:
            mc.log_meal("lunch", argv.lunch.split(","))

        if argv.breakfast:
            mc.log_meal("breakfast", argv.breakfast.split(","))

        if argv.graph:
            mc.graph_data(argv.graph)

        if argv.reset:
            if argv.reset == "logs":
                mc.print_logs()
                mc.drop_collection("MonkLogs")
            elif argv.reset == "data":
                mc.print_data()
                mc.drop_collection("PersonalProgress")
            elif argv.reset == "food":
                mc.print_foods()
                mc.drop_collection("FoodLogs")
            elif argv.reset == "all":
                mc.drop_database("MonkMode")
            else:
                logging.error("Must provide valid reset arg [logs, data, food, all]")
                exit(1)

        if argv.log:
            mc.log(argv.log)

        if argv.lprint:
            if argv.lprint == "console":
                mc.print_logs(False)
            elif argv.lprint == "file":
                mc.print_logs(True)
            elif argv.lprint == "confile":
                mc.print_logs(False)
                mc.print_logs(True)
            else:
                logging.error("Must provide valid print arg [console, file, or confile]")
                exit(1)

        if argv.dprint:
            if argv.dprint == "console":
                mc.print_data(False)
            elif argv.dprint == "file":
                mc.print_data(True)
            elif argv.dprint == "confile":
                mc.print_data(False)
                mc.print_data(True)
            else:
                logging.error("Must provide valid print arg [console, file, or confile]")
                exit(1)

        if argv.fprint:
            if argv.fprint == "console":
                mc.print_foods(False)
            elif argv.fprint == "file":
                mc.print_foods(True)
            elif argv.fprint == "confile":
                mc.print_foods(False)
                mc.print_foods(True)
            else:
                logging.error("Must provide valid print arg [console, file, or confile]")
                exit(1)

        if argv.fdel:
            mc.drop_database("MonkMode")

        if argv.ilogs:
            file = argv.ilogs
            mc.import_data(file, "log")

        if argv.idata:
            file = argv.idata
            mc.import_data(file, "data")

        if argv.ifood:
            file = argv.ifood
            mc.import_data(file, "food")

        if argv.stats:
            mc.stats(argv.stats)

        if argv.ping:
            logging.info("Pong!")

    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser(
            description="******************************************************************************"
                        "Welcome to Monk, a personal logging tool used to"
                        " track your progress in a variety of different ways.")
        parser.add_argument("-c", dest='cognitive-rating', type=int, help="Use to log your current cognitive rating")
        parser.add_argument("-cd", dest='cognitive-description', help="Use to describe why you think you deserve the "
                                                                      "rating you've assigned or elaborate")
        parser.add_argument("-e", dest='emotional-rating', type=int, help="Use to log your current emotional rating")
        parser.add_argument("-ed", dest='emotional-description', help="Use to describe why you think you deserve the "
                                                                      "rating you've assigned or elaborate")
        parser.add_argument("-p", dest='physical-rating', type=int, help="Use to log your current physical rating")
        parser.add_argument("-pd", dest='physical-description', help="Use to describe why you think you deserve the "
                                                                     "rating you've assigned or elaborate")
        parser.add_argument("-dinner", dest='foods',
                            help="Use to log your dinner, it will automatically add calories if you've"
                                 "inputted the given foods before. Foods should be comma delimited, no spaces.")
        parser.add_argument("-lunch", dest='foods',
                            help="Use to log your lunch, it will automatically add calories if you've"
                                 "inputted the given foods before. Foods should be comma delimited, no spaces.")
        parser.add_argument("-breakfast", dest='foods',
                            help="Use to log your breakfast, it will automatically add calories if you've"
                                 "inputted the given foods before. Foods should be comma delimited, no spaces.")
        parser.add_argument("-reset", choices=['food', 'log', 'data'],
                            help="Resets specified data and puts old data in .txt file")
        parser.add_argument("-graph", choices=['all', 'year', 'month', 'week'], help="Use to graph your personal data")
        parser.add_argument("-log", dest="Message", help="Use to log a basic message")
        parser.add_argument("-lprint", choices=['console', 'file', 'confile'],
                            help="Use to print out your basic messages")
        parser.add_argument("-dprint", choices=['console', 'file', 'confile'],
                            help="Use to print out your personal progress logs")
        parser.add_argument("-fprint", choices=['console', 'file', 'confile'], help="Use to print out your food logs")
        parser.add_argument("-fdel", action='store_true', help="Use to delete all of the data, "
                                                               "does not save anything to file")
        parser.add_argument("-ilogs", dest='filepath',
                            help="Use to import personal logs, argument should be a filepath")
        parser.add_argument("-idata", dest='filepath',
                            help="Use to import progress logs, argument should be a filepath")
        parser.add_argument("-ifood", dest='filepath', help="Use to import food logs, argument should be a filepath")
        parser.add_argument("-stats", choices=['all', 'year', 'month', 'week'], help="Use to display stats, "
                                                                                     "argument should be a timeframe")
        parser.add_argument("-ping", action='store_true', help="Use as a test to see if everything is working")
        return parser.parse_args()
