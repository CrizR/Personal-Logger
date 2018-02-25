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
            "type": "Cognitive",
            "rating": argv.c,
            "description": argv.cd
        },
            {
                "type": "Emotional",
                "rating": argv.e,
                "description": argv.ed
            }
            , {
                "type": "Physical",
                "rating": argv.p,
                "description": argv.pd
            }

        ]

        for data_type in arg_types:
            if data_type["rating"]:
                if 10 > int(data_type["rating"]) > 0:
                    data[data_type["type"]] = {
                        "rating": data_type["rating"],
                        "description": data_type["description"],
                        "sentiment": self.get_sentiment(data_type["description"])
                    }
                else:
                    logging.error("Invalid Rating, must be 1-10")
                    exit(1)
        today = datetime.datetime.now().strftime("%Y-%m-%d %H")
        insert_data = {today: {"data": data, "weather": Weather.get_weather()}}
        logging.info("Updating Progress")
        pprog = self.db["PersonalProgress"]
        pprog.insert(insert_data)

    def graph_data(self):
        """
        Graphs personal progress data
        :return:
        """
        logging.info("Printing Data")
        pprog = self.db["PersonalProgress"]
        cursor = pprog.find({})
        data = {
            "emotional": [],
            "physical": [],
            "cognitive": []
        }
        for doc in cursor:
            i = 0
            date = list(doc.keys())[1]
            for key in list(doc[date].keys()):
                rating = int(doc[date][key]["rating"])
                data[key].append([i, rating])
            i += 1
        for key in data.keys():
            data[key].reverse()
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
            ff = open(os.getcwd() + "/old_data.txt", "w+")
            logging.info("Writing to file: " + os.getcwd() + "/old_data.txt")
            for doc in cursor:
                date = list(doc.keys())[1]
                info = {date: json.dumps(doc[date])}
                ff.writelines(str(info) + "\n")
            ff.close()
        else:
            for doc in cursor:
                date = list(doc.keys())[1]
                info = {date: json.dumps(doc[date])}
                print(info)

    def log(self, msg):
        """
        Log msg to db
        :param msg:
        :return:
        """
        logging.info("Logging Message")
        ml = self.db["MonkLogs"]
        today = datetime.datetime.now().strftime("%Y-%m-%d %H")
        ml.insert({today: {"log": msg,
                           "sentiment": self.get_sentiment(msg),
                           "weather": Weather.get_weather()}})

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
            ff = open("monk_logs.txt", "w+")
            logging.info("Writing to file: " + os.getcwd() + "/monk_logs.txt")
            for msg in cursor:
                date = list(msg.keys())[1]
                msg = {date: json.dumps(msg[date])}
                ff.writelines(str(msg) + "\n")
            ff.close()
        else:
            for msg in cursor:
                date = list(msg.keys())[1]
                msg = {date: json.dumps(msg[date])}
                print(msg)

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
