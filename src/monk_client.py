import datetime
import json
import logging
import os

import matplotlib.pyplot as plt
import pymongo
from textblob import TextBlob

from src.weather_client import Weather
from collections import Counter


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
        if import_type == "data":
            collection = self.db["PersonalProgress"]
        elif import_type == "log":
            collection = self.db["MonkLogs"]
        else:
            collection = ""
            logging.error("Invalid Type")
            exit(1)
        try:
            fl = open(file)
            data = fl.readlines()
            for line in data:
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

    def stats(self, timeframe=None):
        collection = self.db["MonkLogs"]
        cursor = collection.find({})
        sentiments = {
            "positive": 0,
            "negative": 0,
            "neutral": 0,
        }
        weather = {}
        weather_mood = {
            "positive": [],
            "negative": [],
            "neutral": [],
        }
        now = datetime.date.today()
        if timeframe == "all":
            logging.info(" __________")
            logging.info("| All data |")
            logging.info("|__________|\n")
            comp = now - datetime.timedelta(days=365 * 10)
        elif timeframe == "year":
            logging.info(" ________________")
            logging.info("|Last year's data|")
            logging.info("|________________|\n")
            comp = now - datetime.timedelta(days=365)
        elif timeframe == "month":
            logging.info(" _________________")
            logging.info("|Last month's data|")
            logging.info("|_________________|\n")
            comp = now - datetime.timedelta(days=28)
        elif timeframe == "week":
            logging.info(" ________________")
            logging.info("|Last week's data|")
            logging.info("|________________|\n")
            comp = now - datetime.timedelta(days=7)
        else:
            logging.info(" __________")
            logging.info("| All data |")
            logging.info("|__________|\n")
            comp = now - datetime.timedelta(days=365 * 10)

        number_of_logs = 0
        number_of_progress = 0

        for log in cursor:
            date = list(log.keys())[1]
            try:
                datecomp = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M")
            except:
                datecomp = datetime.datetime.today()
            if datecomp > datetime.datetime.combine(comp, datetime.time.min):
                number_of_logs += 1
                sentiment = log[date]["sentiment"]
                sentiments[sentiment] += 1
                if date in log and "weather" in log[date] \
                        and log[date]["weather"] is not None \
                        and "weather_type" in log[date]["weather"]:
                    weather_types = log[date]["weather"]["weather_type"]
                    for weather_type in weather_types:
                        if weather_type not in weather:
                            weather[weather_type] = 0
                        weather[weather_type] += 1
                        weather_mood[sentiment].append(weather_type)

        collection = self.db["PersonalProgress"]
        cursor = collection.find({})
        trio = {
            "cognitive": 0,
            "physical": 0,
            "emotional": 0
        }

        num = 0
        for data in cursor:
            date = list(data.keys())[1]
            try:
                datecomp = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M")
            except:
                datecomp = datetime.datetime.today()
            if datecomp > datetime.datetime.combine(comp, datetime.time.min):
                number_of_progress += 1
                num += 1
                pdata = data[date]["data"]
                for type in trio.keys():
                    trio[type] += int(pdata[type]["rating"])
                    sentiment = pdata[type]["sentiment"]
                    sentiments[sentiment] += 1
                    log = data[date]
                    if "weather" in log \
                            and log["weather"] is not None \
                            and "weather_type" in log["weather"]:
                        weather_types = log["weather"]["weather_type"]
                        for weather_type in weather_types:
                            if weather_type not in weather:
                                weather[weather_type] = 0
                            weather[weather_type] += 1
                            weather_mood[sentiment].append(weather_type)

        logging.info("Number of Logs:\t\t\t\t|" + str(number_of_logs))
        logging.info("Number of Progress Logs:\t\t|" + str(number_of_progress))
        emotion_percent = {
            "positive": round(sentiments["positive"] / (sentiments["positive"] +
                             sentiments["negative"] + sentiments["neutral"]) * 100, 2),
            "neutral": round(sentiments["neutral"] / (sentiments["positive"] +
                             sentiments["negative"] + sentiments["neutral"]) * 100, 2),
            "negative": round(sentiments["negative"] / (sentiments["positive"] +
                                sentiments["negative"] + sentiments["neutral"]) * 100, 2)
        }
        for mood in emotion_percent.keys():
            logging.info("Percent " + mood.capitalize() + " \t\t\t|" + str(emotion_percent[mood]) + "%")

        weathers = Counter()
        most_common_weather_types = {
            "positive": Counter({}),
            "negative": Counter({}),
            "neutral": Counter({})
        }
        for mood in weather_mood.keys():
            most_common_weather_types[mood] = Counter(weather_mood[mood])
            weathers += Counter(weather_mood[mood])
        logging.info("Most Common Weather:\t\t\t|" + str(weathers.most_common(1)[0][0]))
        top_weathers = {
            "positive": '',
            "negative": '',
            "neutral": ''
        }
        highest_percent = 0
        for mood in weather_mood.keys():
            for weather_type in most_common_weather_types[mood].keys():
                if most_common_weather_types[mood][weather_type] / weathers[weather_type] > highest_percent:
                    highest_percent = most_common_weather_types[mood][weather_type] / weathers[weather_type]
                    top_weathers[mood] = weather_type
            highest_percent = 0
            logging.info("Most " + mood.capitalize() + " Weather:\t\t\t|" + top_weathers[mood])

        logging.info("Average Cognitive Rating:\t\t|" + str(round((trio["cognitive"] / num), 2)))
        logging.info("Average Physical Rating:\t\t|" + str(round((trio["physical"] / num), 2)))
        logging.info("Average Emotional Rating:\t\t|" + str(round((trio["physical"] / num), 2)))
        self.graph_data()
