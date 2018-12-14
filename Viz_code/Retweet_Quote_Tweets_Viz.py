import matplotlib
matplotlib.use('Agg')
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pymongo
import datetime

# Setting up mongo
MONGO_HOST = 'mongodb://localhost/tweepyDB'
client = pymongo.MongoClient(MONGO_HOST)

# Use tweepyDB if it doesnt exist create a new one
db = client.tweepyDB
tweepyDatabase = db.twitter_search1
# Start time 
startTime = datetime.datetime.now()
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
for data in tweepyDatabase.find({"API_type": "Stream"},).limit(1):
    startTime = datetime.datetime.strptime(data["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
    limitTime = startTime + datetime.timedelta(minutes=60) 
    #print startTime

fullArr = []
quoteDataArr = []
# Geting array of all the data with Quote
for data in tweepyDatabase.find({"is_quote_status" : True}):
    dataTime = datetime.datetime.strptime(data["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
  
    if dataTime >= startTime and dataTime <= limitTime:
        quoteDataArr.append(dataTime)
        #print dataTime
quoteDataArr = sorted(quoteDataArr)
print len(quoteDataArr)
sortedBuket = getBucketList(quoteDataArr)
fullArr.append(sortedBuket)

retweetDataArr = []
# Geting array of all the data with Retweets
for data in tweepyDatabase.find({"retweeted_status" : {"$ne" : None}}):
    dataTime = datetime.datetime.strptime(data["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
    if dataTime >= startTime and dataTime <= limitTime:
        retweetDataArr.append(dataTime)
        #print dataTime
retweetDataArr = sorted(retweetDataArr)
print len(retweetDataArr)
sortedBuket = getBucketList(retweetDataArr)
fullArr.append(sortedBuket)

colorList = ["#ff0000" , "#0000ff" ]
labelList = ["Quote Tweets: " + str(len(quoteDataArr)) , "Retweet Tweets: " + str(len(retweetDataArr))]
# Input buket array into API to plot histogram
commutes = pd.Series(fullArr)
plt.hist(fullArr, bins=[0,10,20,30,40,50,60], rwidth=0.9,
                   color=colorList)

plt.legend(loc="center left",bbox_to_anchor=(1, 0.5) , labels = labelList)
plt.title(r'Histogram of Quote/Retweet Tweets')
plt.ylabel('Tweet Count(s)')
plt.xlabel('Time (mins)')
plt.grid(axis='y', alpha=0.75)

plt.savefig('./Graphs/Retweets_Quote_Histogram.png',bbox_inches='tight')