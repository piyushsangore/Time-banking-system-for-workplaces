import pymongo
import config

client = pymongo.MongoClient(config.Config.MONGO_URI)

db = client['timebank']

users_collection = db['users']
tasks_collection = db['tasks']
