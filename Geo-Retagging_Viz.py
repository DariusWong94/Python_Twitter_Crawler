import matplotlib
matplotlib.use('Agg')
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from pymongo import MongoClient
import datetime
from collections import Counter
import random
import numpy as np

MONGO_HOST = 'mongodb://127.0.0.1:27017/tweepyDB'
client = MongoClient(MONGO_HOST)
db = client.tweepyDB
tweepyDatabase = db.twitter_search1

# Check if ascii
def is_ascii(s):
    return all(ord(c) < 128 for c in s)

# Start time 
startTime = datetime.datetime.now()
limitTime = datetime.datetime.now()

# Getting and setting start time of stream
for data in tweepyDatabase.find({"API_type": "Stream"},).limit(1):
    startTime = datetime.datetime.strptime(data["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
    limitTime = startTime + datetime.timedelta(minutes=60) 
    #print startTime

# Get all trends
TrendList = []
for data in tweepyDatabase.find().distinct("trend_category"):
    TrendList.append(data)

# Get all data
fullDataList = []
for data in tweepyDatabase.find():
    dataTime = datetime.datetime.strptime(data["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
    if dataTime >= startTime and dataTime <= limitTime:
        fullDataList.append(data)

# Split full data
fullDataList.sort(key=lambda  x:x["_id"], reverse=True)
a = fullDataList
evenList = a[0:][::2]
oddListOriginal = a[1:][::2]

originalPlaceList = []
# Orignal Odd List
for data in oddListOriginal:
    if data["place"] is not None and is_ascii(data['place']['full_name']):
        originalPlaceList.append(data["place"]["full_name"])
    else:    
        data["place"] = {"full_name":"None"}
        originalPlaceList.append(data["place"]["full_name"])

originalPlaceCount = Counter(originalPlaceList)

oddList = a[1:][::2]

# Get places of all trends
AllPlacesList = {}
for trends in TrendList:
    trendPlaceList = []
    for data in evenList:
        if data["trend_category"] == trends:
            if data["place"] is not None:
                trendPlaceList.append(data["place"]["full_name"])    
        else:
            pass
    AllPlacesList[trends] = trendPlaceList
#print AllPlacesList

topPlacesList = {}
# Get top Place for each trend
for trend, places in AllPlacesList.items():
    a = Counter(places)
    top = 0
    topword = ""
    for k,v in a.items():
        if v < top:
            pass
        else:
            top = v
            topword = k
    if topword == "":
        topword = "Singapore"
    topPlacesList[trend] = topword

fullArr = []
placeList = []
# print topPlacesList
# update oddList geo data 
for trend , topwords in topPlacesList.items():
    for data in oddList:
        if data["trend_category"] == trend:
            if data["place"] is not None:
                data["place"]["full_name"] = topwords
                placeList.append(data["place"]["full_name"])
            else:
                data["place"] = {"full_name":"Singapore"}
                placeList.append(data["place"]["full_name"])

placeCount = Counter(placeList)

# Input buket array into API to plot histogram
labels, values = zip(*placeCount.items())
labels = np.array(labels)
values = np.array(values)
values = values.tolist()

labels1, values1 = zip(*originalPlaceCount.items())
labels1 = np.array(labels1)
values1 = np.array(values1)
values1 = values1.tolist()

d = {
    'After Retagging' : pd.Series(values, index = labels),
    'Before Retagging' : pd.Series(values1 , index = labels1)
}

df = pd.DataFrame(d)
df.plot(kind="bar")

plt.legend(loc="center left",bbox_to_anchor=(1, 0.5))
plt.title(r'Histogram of Geo-Retagged Tweets')
plt.ylabel('Tweet Count(s)')
plt.xlabel('Place Name')
plt.grid(axis='y', alpha=0.75)

plt.savefig('./Geo-Retagging_Histogram.png',bbox_inches='tight')