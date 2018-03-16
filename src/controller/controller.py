import argparse
import logging

from src.model.monk_client import MonkClient


class MonkController(object):

    def run(self, host, port):
        argv = self.parse_args()
        mc = MonkClient(host, port)
        if argv.c or argv.e or argv.ed:
            mc.update_progress(argv)

        if argv.graph:
            mc.graph_data(argv.graph)

        if argv.reset:
            if argv.reset == "logs":
                mc.print_logs()
                mc.drop_collection("MonkLogs")
            elif argv.reset == "data":
                mc.print_data()
                mc.drop_collection("PersonalProgress")
            elif argv.reset == "all":
                mc.drop_database("MonkMode")
            else:
                logging.error("Must provide valid reset arg [logs, data, or all]")
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

        if argv.fdel:
            mc.drop_database("MonkMode")

        if argv.ilogs:
            file = argv.ilogs
            mc.import_data(file, "log")

        if argv.idata:
            file = argv.idata
            mc.import_data(file, "data")

        if argv.stats:
            mc.stats(argv.stats)

        if argv.ping:
            logging.info("Pong!")

    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser()
        parser.add_argument("-c", help="Cognitive Rating")
        parser.add_argument("-cd", help="Cognitive Description")
        parser.add_argument("-e", help="Emotional Rating")
        parser.add_argument("-ed", help="Emotional Description")
        parser.add_argument("-p", help="Physical Rating")
        parser.add_argument("-pd", help="Physical Description")
        parser.add_argument("-reset", help="Resets specified data and puts old data in .txt file")
        parser.add_argument("-graph", help="Graph Data")
        parser.add_argument("-log", help="Logs a message")
        parser.add_argument("-lprint", help="Print Logs")
        parser.add_argument("-dprint", help="Print Progress Data")
        parser.add_argument("-fdel", action='store_true', help="No Data Saved Anywhere")
        parser.add_argument("-ilogs", help="Import Logs")
        parser.add_argument("-idata", help="Import Data")
        parser.add_argument("-stats", help="Stats")
        parser.add_argument("-ping", action='store_true', help="Test to see if it's working")
        return parser.parse_args()
