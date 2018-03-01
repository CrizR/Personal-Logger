import pymongo, json

HOST = 'localhost'
PORT = 27017
client = pymongo.MongoClient(HOST, PORT)
db = client["MonkMode"]
collection = db["PersonalProgress"]

cursor = collection.find({})

fl = open("old_data.txt")

data = fl.readlines()

for line in data:
    print(line)
    collection.insert_one(json.loads(line))

