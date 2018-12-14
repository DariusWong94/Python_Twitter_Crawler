import pandas as pd
import pymongo
import datetime
import random
import json
from bson import ObjectId
from bson import json_util

# # Setting up mongo
# MONGO_HOST = 'mongodb://localhost/tweepyDB'
# client = pymongo.MongoClient(MONGO_HOST)

# # Use tweepyDB if it doesnt exist create a new one
# db = client.tweepyDB
# tweepyDatabase = db.twitter_search1

# Setting up mongo
MONGO_HOST = 'mongodb://localhost/redditDB'
client = pymongo.MongoClient(MONGO_HOST)

# Use redditDB if it doesnt exist create a new one
db = client.redditDB
redditDatabase = db.reddit_search


# Start time 
startTime = datetime.datetime.now()
# limitTime
limitTime = datetime.datetime.now()


# Getting and setting start time of stream
for data in redditDatabase.find({"api_type": "Stream"}).limit(1):
    startTime = data["created_utc"]
    limitTime = startTime + datetime.timedelta(minutes=5)
    #print startTime

currentList = []
count = 0
file = open("Reddit_data.json", 'a')
file.write("[")
for data in redditDatabase.find():
    dataTime = data["created_utc"]
    if dataTime >= startTime and dataTime <= limitTime:
        if(count == 0 ):
                 file.write(json.dumps(data,default=json_util.default))
                 count = count + 1
        else:                        
                file.write("," + json.dumps(data,default=json_util.default))

file.write("]")
