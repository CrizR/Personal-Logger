
import pymongo
import logging


class CalorieClient(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = pymongo.MongoClient(host, port)
        self.db = self.client["FoodToCalories"]

    def get_calories(self, food):
        collection = self.db["Converter"]
        existing_food = collection.find_one({"name": food})
        if existing_food is not None:
            return existing_food["calories"]
        else:
            calories = int(input("Enter number of calories in [" + food + "] : "))
            collection.insert_one({"name": food, "calories": calories})
            return calories

    def aggregate_calories(self, foods):
        logging.info("Getting Calories")
        calories = 0
        for food in foods:
            c = self.get_calories(food)
            calories += c
        return calories


