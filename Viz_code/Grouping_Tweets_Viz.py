import matplotlib
matplotlib.use('Agg')
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pymongo
import datetime
import random

# Setting up mongo
MONGO_HOST = 'mongodb://localhost/tweepyDB'
client = pymongo.MongoClient(MONGO_HOST)

# Use tweepyDB if it doesnt exist create a new one
db = client.tweepyDB
tweepyDatabase = db.twitter_search1


# Start time 
startTime = datetime.datetime.now()
# limitTime
limitTime = datetime.datetime.now()

def getBucketList(currentList):
    buketArr= []
    CountI = 0
    # Used to count data in a certain range, 9 represents 0-10 mins range
    bucketTime = 9
    # Points to the next 10 mins
    buketPoint =  datetime.datetime.now()   
    # Range limit
    bucketLimit = datetime.datetime.now()
    for date in currentList:
        # # set Initial buket point and buket limit
        if CountI == 0:
            buketPoint = date + datetime.timedelta(minutes=10)
            bucketLimit = date + datetime.timedelta(minutes=60)
            buketArr.append(bucketTime)
        # # Within 10mins range, simple append the buket time
        elif CountI != 0 and date <= buketPoint:
            buketArr.append(bucketTime)
        # # After 10mins range, increment buketPoint and buketTime
        elif CountI != 0 and date >= buketPoint:
            buketPoint = buketPoint + datetime.timedelta(minutes=10)
            bucketTime = bucketTime + 10
            buketArr.append(bucketTime)
        # # break if date collected passes one hour mark    
        elif CountI != 0 and date >= bucketLimit: 
            break
        CountI = CountI + 1 
        # print date
    return buketArr


# Getting and setting start time of stream
for data in tweepyDatabase.find({"API_type": "Stream"}).limit(1):
    startTime = datetime.datetime.strptime(data["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
    limitTime = startTime + datetime.timedelta(minutes=60)
    #print startTime

trendsList={}
trendCount = 0
# Get all trends append into list
for trend in tweepyDatabase.find().distinct("trend_category"):
    currentList = []
    for data in tweepyDatabase.find({"trend_category": trend}):
        dataTime = datetime.datetime.strptime(data["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
        if dataTime >= startTime and dataTime <= limitTime:
            currentList.append(dataTime)
            trendCount = trendCount + 1
            #print dataTime
        else: 
            pass
    if len(currentList) == 0:
        pass
    else:    
        # Append into list of trends used
        trendsList[trend] = len(currentList)

geoTrendsList={}
geoTrendCount = 0
# Get all trends append into list
for trend in tweepyDatabase.find().distinct("trend_category"):
    currentList = []
    for data in tweepyDatabase.find({"trend_category": trend , "geo" :{"$ne" : None} }):
        dataTime = datetime.datetime.strptime(data["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
        if dataTime >= startTime and dataTime <= limitTime:
            currentList.append(dataTime)
            geoTrendCount = geoTrendCount + 1
            #print dataTime
        else: 
            pass      
    if len(currentList) == 0:
        pass
    else:    
        
        # Append into list of trends used
        geoTrendsList[trend] = len(currentList)


# Input buket array into API to plot histogram

labels, values = zip(*trendsList.items())
labels = np.array(labels)
values = np.array(values)
values = values.tolist()

labels1, values1 = zip(*geoTrendsList.items())
labels1 = np.array(labels1)
values1 = np.array(values1)
values1 = values1.tolist()

d = {
    'All Tweets: ' + str(trendCount) : pd.Series(values, index = labels),
    'Geo-Tag Tweets: ' + str(geoTrendCount) : pd.Series(values1 , index = labels1)
}

df = pd.DataFrame(d)
df.plot(kind="bar")

plt.legend(loc="center left",bbox_to_anchor=(1, 0.5) )
plt.title(r'Histogram of Grouped Tweets')
plt.ylabel('Tweet Count(s)')
plt.xlabel('Time (mins)')
plt.grid(axis='y', alpha=0.75)

plt.savefig('./Graphs/Grouping_All_Histogram.png',bbox_inches='tight')