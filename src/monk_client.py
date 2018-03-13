import datetime
import json
import logging
import os

import matplotlib.pyplot as plt
import pymongo
from textblob import TextBlob

from src.weather_client import Weather


class MonkClient(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = pymongo.MongoClient(host, port)
        self.db = self.client["MonkMode"]

    def update_progress(self, argv):
        """
        Updates personal progress data in db
        :param argv:
        :return:
        """
        data = {}
        arg_types = [{
            "type": "cognitive",
            "rating": argv.c,
            "description": argv.cd
        },
            {
                "type": "emotional",
                "rating": argv.e,
                "description": argv.ed
            }
            , {
                "type": "physical",
                "rating": argv.p,
                "description": argv.pd
            }

        ]

        for data_type in arg_types:
            if data_type["rating"]:
                if 100 >= int(data_type["rating"]) > 0:
                    data[data_type["type"]] = {
                        "rating": data_type["rating"],
                        "description": data_type["description"],
                        "sentiment": self.get_sentiment(data_type["description"])
                    }
                else:
                    logging.error("Invalid Rating, must be 1-10")
                    exit(1)
        today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        insert_data = {today: {"data": data, "weather": Weather.get_weather()}}
        logging.info("Updating Progress")
        pprog = self.db["PersonalProgress"]
        pprog.insert(insert_data)

    def graph_data(self):
        """
        Graphs personal progress data
        :return:
        """
        logging.info("Graphing Data")
        pprog = self.db["PersonalProgress"]
        cursor = pprog.find({})
        data = {
            "emotional": [],
            "physical": [],
            "cognitive": []
        }
        for doc in cursor:
            date = list(doc.keys())[1]
            for key in list(doc[date]['data'].keys()):
                rating = int(doc[date]["data"][key]["rating"])
                data[key].append(rating)
        for key in data.keys():
            plt.ylabel('Level')
            plt.xlabel('Number of Logs - Ordered By Date')
            plt.plot(data[key])
        plt.legend(['Emotional', 'Physical', 'Cognitive'], loc='upper left')
        plt.show()

    def print_data(self, to_file=True):
        """
        Prints out personal progress data to console or file
        :param to_file:
        :return:
        """
        logging.info("Printing PData")
        pprog = self.db["PersonalProgress"]
        cursor = pprog.find({})
        if to_file:
            ff = open(os.getcwd() + "/progress_data.txt", "w+")
            logging.info("Writing to file: " + os.getcwd() + "/progress_data.txt")
            for doc in cursor:
                date = list(doc.keys())[1]
                info = {date: doc[date]}
                ff.writelines(json.dumps(info) + "\n")
            ff.close()
        else:
            for doc in cursor:
                date = list(doc.keys())[1]
                info = {date: doc[date]}
                print(json.dumps(info))

    def print_logs(self, to_file=True):
        """
        Prints out the logs to console or file
        :param to_file:
        :return:
        """
        logging.info("Printing Log Data")
        ml = self.db["MonkLogs"]
        cursor = ml.find({})
        if to_file:
            ff = open("log_data.txt", "w+")
            logging.info("Writing to file: " + os.getcwd() + "/log_data.txt")
            for log in cursor:
                date = list(log.keys())[1]
                log = {date: log[date]}
                ff.writelines(json.dumps(log) + "\n")
            ff.close()
        else:
            for log in cursor:
                date = list(log.keys())[1]
                log = {date: log[date]}
                print(json.dumps(log))

    def log(self, msg):
        """
        Log msg to db
        :param msg:
        :return:
        """
        logging.info("Logging Message")
        ml = self.db["MonkLogs"]
        today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        ml.insert({today: {"log": msg,
                           "sentiment": self.get_sentiment(msg),
                           "weather": Weather.get_weather()}})

    def import_data(self, file, import_type: str):
        """
        Imports data from the given file
        :param file:
        :param import_type:
        :return:
        """
        if import_type == "log":
            collection = self.db["PersonalProgress"]
        elif import_type == "data":
            collection = self.db["MonkLogs"]
        else:
            collection = ""
            logging.error("Invalid Type")
            exit(1)
        try:
            fl = open(file)
            data = fl.readlines()
            for line in data:
                logging.info("Inserting", line)
                collection.insert_one(json.loads(line))
        except FileNotFoundError:
            logging.error("File Not Found")
            exit(1)

    def drop_database(self, name):
        """
        Drops the database
        :param name:
        :return:
        """
        logging.info("Dropping Database")
        self.client.drop_database(name)

    def drop_collection(self, name):
        """
        Removes the collection
        :param name:
        :return:
        """
        logging.info("Dropping Collection")
        self.db.drop_collection(name)


    @staticmethod
    def get_sentiment(desc):
        """
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        :param desc:
        :return:
        """
        # create TextBlob object of passed tweet text
        analysis = TextBlob(desc)
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'
