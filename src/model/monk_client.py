import datetime
import json
import logging
import os
from collections import Counter

import matplotlib.pyplot as plt
import pymongo
from textblob import TextBlob

from src.components.weather_client import Weather
from src.components.calorie_client import CalorieClient


class MonkClient(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = pymongo.MongoClient(host, port)
        self.calorie_client = CalorieClient(host, port)
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

    def graph_data(self, timeframe):
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
        comp = self.get_timeframe(timeframe)
        for doc in cursor:
            date = list(doc.keys())[1]
            try:
                datecomp = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M")
            except:
                datecomp = datetime.datetime.today()
            if datecomp > datetime.datetime.combine(comp, datetime.time.min):
                for key in data.keys():
                    rating = int(doc[date]["data"][key]["rating"])
                    data[key].append(rating)
        plt.ylabel('Level')
        plt.xlabel('Number of Logs - Ordered By Date')
        for key in data.keys():
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

    def print_foods(self, to_file=True):
        """
               Prints out the food logs to console or file
               :param to_file:
               :return:
               """
        logging.info("Printing Food Data")
        ml = self.db["FoodLogs"]
        cursor = ml.find({})
        if to_file:
            ff = open("food_data.txt", "w+")
            logging.info("Writing to file: " + os.getcwd() + "/food_data.txt")
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

    def log_meal(self, mealtime, foods_input: [], date=None):
        logging.info("Logging Meal")
        fl = self.db["FoodLogs"]
        if not date:
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            today_time = datetime.datetime.now()
            start = today + " 00:00"
        else:
            today_time = datetime.datetime.strptime(date + " 00:00", "%Y-%m-%d %H:%M")
            start = date + " 00:00"
        cursor = fl.find({})
        found = False
        if cursor.count() > 0:
            for data in cursor:
                if data is not None:
                    id = data["_id"]
                    date = list(data.keys())[1]
                    if datetime.datetime.strptime(date, "%Y-%m-%d %H:%M") \
                            > datetime.datetime.strptime(start, "%Y-%m-%d %H:%M") \
                            < today_time:
                        if data[date]["meal"] == mealtime:
                            found = True
                            foods = data[date]["foods"]
                            for food in foods_input:
                                if food not in foods:
                                    logging.info("Adding " + food + " to existing entry.")
                                    foods.append(food)
                            calories = self.calorie_client.aggregate_calories(foods)
                            result = fl.update_one({"_id": id}, {"$set": {date + ".foods": foods}})
                            logging.debug("Matched Count" + str(result.matched_count))
                            logging.debug("Modified Count" + str(result.modified_count))
                            result = fl.update_one({"_id": id}, {"$set": {date + ".calories": calories}})
                            logging.debug("Matched Count" + str(result.matched_count))
                            logging.debug("Modified Count" + str(result.modified_count))
        if not found:
            calories = self.calorie_client.aggregate_calories(foods_input)
            fl.insert({today_time.strftime("%Y-%m-%d %H:%M"): {"meal": mealtime, "foods": foods_input, "calories": calories}})

    def import_data(self, file, import_type):
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
        elif import_type == "food":
            collection = self.db["FoodLogs"]
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

    @staticmethod
    def get_timeframe(timeframe):
        now = datetime.date.today()
        if timeframe == "all":
            comp = now - datetime.timedelta(days=365 * 10)
        elif timeframe == "year":
            comp = now - datetime.timedelta(days=365)
        elif timeframe == "month":
            comp = now - datetime.timedelta(days=28)
        elif timeframe == "week":
            comp = now - datetime.timedelta(days=7)
        else:
            comp = now - datetime.timedelta(days=365 * 10)
        return comp

    def stats(self, timeframe=None, print=True):
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
        top_weathers = {
            "positive": '',
            "negative": '',
            "neutral": ''
        }
        weathers = Counter()
        most_common_weather_types = {
            "positive": Counter({}),
            "negative": Counter({}),
            "neutral": Counter({})
        }
        trio = {
            "cognitive": 0,
            "physical": 0,
            "emotional": 0
        }
        comp = self.get_timeframe(timeframe)
        number_of_logs = 0
        number_of_progress = 0

        number_of_logs = self.log_stats(comp, number_of_logs, sentiments, weather, weather_mood)
        number_of_progress = self.progress_stats(comp, number_of_progress, sentiments, trio, weather, weather_mood)
        food_stats = self.food_stats(comp)

        for mood in weather_mood.keys():
            most_common_weather_types[mood] = Counter(weather_mood[mood])
            weathers += Counter(weather_mood[mood])
        highest_percent = 0
        for mood in top_weathers.keys():
            for weather_type in most_common_weather_types[mood].keys():
                if most_common_weather_types[mood][weather_type] / weathers[weather_type] > highest_percent:
                    if weathers[weather_type] > 1:
                        highest_percent = most_common_weather_types[mood][weather_type] / weathers[weather_type]
                        top_weathers[mood] = weather_type
            highest_percent = 0

        emotion_percent = {
            "positive": round(sentiments["positive"] / (sentiments["positive"] +
                                                        sentiments["negative"] + sentiments["neutral"]) * 100, 2),
            "neutral": round(sentiments["neutral"] / (sentiments["positive"] +
                                                      sentiments["negative"] + sentiments["neutral"]) * 100, 2),
            "negative": round(sentiments["negative"] / (sentiments["positive"] +
                                                        sentiments["negative"] + sentiments["neutral"]) * 100, 2)
        }
        if print:
            logging.info("\n------------------------------------------------")
            logging.info("General Stats:\t\t\t\t\t")
            logging.info("------------------------------------------------")
            logging.info("Number of Logs:\t\t\t\t|" + str(number_of_logs) + str("\t|"))
            logging.info("Number of Progress Logs:\t\t|" + str(number_of_progress) + str("\t|"))
            logging.info("Number of Food Logs:\t\t\t|" + str(food_stats["number_of_food_logs"]) + str("\t|"))
            logging.info("------------------------------------------------")
            logging.info("Weather Stats:\t\t\t\t\t")
            logging.info("------------------------------------------------")
            for mood in emotion_percent.keys():
                logging.info("Percent " + mood.capitalize() + " \t\t\t|" + str(emotion_percent[mood]) + " %" + str("|"))
            logging.info("Most Common Weather:\t\t\t|" + str(weathers.most_common(1)[0][0]) + str("\t|"))
            for mood in top_weathers.keys():
                logging.info("Most " + mood.capitalize() + " Weather:\t\t\t|" + top_weathers[mood] + str("\t|"))
            logging.info("------------------------------------------------")
            logging.info("Progress Stats:\t\t\t\t\t")
            logging.info("------------------------------------------------")
            logging.info("Average Cognitive Rating:\t\t|" + str(round((trio["cognitive"] / number_of_progress), 2)) + str("\t|"))
            logging.info("Average Physical Rating:\t\t|" + str(round((trio["physical"] / number_of_progress), 2)) + str("\t|"))
            logging.info("Average Emotional Rating:\t\t|" + str(round((trio["emotional"] / number_of_progress), 2)) + str("\t|"))
            logging.info("------------------------------------------------")
            logging.info("Food Stats:\t\t\t\t\t")
            logging.info("------------------------------------------------")
            logging.info("Average Calories Per Day\t\t|" + str(food_stats["avg_calories_per_day"]) + str("\t|"))
            logging.info("Pounds Per Week\t\t\t\t|" + str(food_stats["lbs_per_week"]) + str("\t|"))
            logging.info("------------------------------------------------")
            logging.info("\n")

        return {
            "logs": number_of_logs,
            "personal_logs": number_of_progress,
            "food_logs": food_stats["number_of_food_logs"],
            "positive_percent": emotion_percent["positive"],
            "negative_percent": emotion_percent["negative"],
            "neutral_percent": emotion_percent["neutral"],
            "positive_weather": top_weathers["positive"],
            "negative_weather": top_weathers["negative"],
            "neutral_weather": top_weathers["neutral"],
            "avg_cognitive": str(round((trio["cognitive"] / number_of_progress), 2)),
            "avg_physical": str(round((trio["physical"] / number_of_progress), 2)),
            "avg_emotion": str(round((trio["emotional"] / number_of_progress), 2)),
            "avg_calories": food_stats["avg_calories_per_day"],
            "lbs_per_week": food_stats["lbs_per_week"]
        }

    def food_stats(self, comp):
        collection = self.db["FoodLogs"]
        cursor = collection.find({})

        current_day = datetime.datetime.combine(comp, datetime.time.min)
        total_calories = 0
        num_of_days = 0
        burn_rate = 2000
        days = {}
        while current_day < datetime.datetime.now():
            days[current_day.date()] = 0
            current_day += datetime.timedelta(days=1)
        for meal in cursor:
            date = list(meal.keys())[1]
            try:
                datecomp = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M")
            except:
                datecomp = datetime.datetime.today()
            if datecomp > datetime.datetime.combine(comp, datetime.time.min) and datetime.date(datecomp.year, datecomp.month, datecomp.day) in days:
                total_calories += meal[date]["calories"]
                num_of_days += 1/3
        return {
            "number_of_food_logs": int(num_of_days * 3),
            "avg_calories_per_day": int(total_calories / num_of_days),
            "lbs_per_week": round((((total_calories / num_of_days) - burn_rate) * 7) / 3500, 2)
        }

    def progress_stats(self, comp, number_of_progress, sentiments, trio, weather, weather_mood):
        """
        Get progress stats
        :param comp:
        :param number_of_progress:
        :param sentiments:
        :param trio:
        :param weather:
        :param weather_mood:
        :return:
        """
        collection = self.db["PersonalProgress"]
        cursor = collection.find({})
        for data in cursor:
            date = list(data.keys())[1]
            try:
                datecomp = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M")
            except:
                datecomp = datetime.datetime.today()
            if datecomp > datetime.datetime.combine(comp, datetime.time.min):
                number_of_progress += 1
                pdata = data[date]["data"]
                for type in pdata.keys():
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
        return number_of_progress

    def log_stats(self, comp, number_of_logs, sentiments, weather, weather_mood):
        """
        Get log stats
        :param comp:
        :param number_of_logs:
        :param sentiments:
        :param weather:
        :param weather_mood:
        :return:
        """
        collection = self.db["MonkLogs"]
        cursor = collection.find({})
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
        return number_of_logs
