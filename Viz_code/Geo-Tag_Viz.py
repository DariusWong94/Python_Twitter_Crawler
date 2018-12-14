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

buketArr= []
CountI = 0
# Used to count data in a certain range, 9 represents 0-10 mins range
bucketTime = 9
# Points to the next 10 mins
buketPoint =  datetime.datetime.now()
# Range limit
bucketLimit = datetime.datetime.now()
# Start time 
startTime = datetime.datetime.now()
limitTime = datetime.datetime.now() 
# Getting and setting start time of stream
for data in tweepyDatabase.find( {"API_type": "Stream"}, {"_id" : 0 , "created_at": 1}).limit(1):
    startTime = datetime.datetime.strptime(data["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
    limitTime = startTime + datetime.timedelta(minutes=60) 
    #print startTime

# Geting array of all the geo tagged data after startTime
compareArr = []
fullData = tweepyDatabase.find( {"geo" :{"$ne" : None}})
for data in fullData:
    dataTime = datetime.datetime.strptime(data["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
    if dataTime >= startTime and dataTime <= limitTime:
        compareArr.append(dataTime)
        #print dataTime
compareArr = sorted(compareArr)
print len(compareArr)
for date in compareArr:
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


labelList = ["Geo-Taged Tweets: " + str(len(compareArr))]
# Input buket array into API to plot histogram
commutes = pd.Series(buketArr)
commutes.plot(kind = "hist", grid=True, bins=[0,10,20,30,40,50,60], rwidth=0.9,
                   color='#607c8e')

plt.legend(loc="center left",bbox_to_anchor=(1, 0.5) , labels = labelList)
plt.title(r'Histogram of Geo-tagged Tweets')
plt.ylabel('Geo-Tagged Count(s)')
plt.xlabel('Time (mins)')
plt.grid(axis='y', alpha=0.75)

plt.savefig('./Graphs/Geo-Tagged_Histogram.png' ,bbox_inches='tight')