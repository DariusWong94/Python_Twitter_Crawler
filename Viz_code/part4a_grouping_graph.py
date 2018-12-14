import matplotlib
matplotlib.use('Agg')
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pymongo
from datetime import datetime, timedelta
import pytz
import time
import random

# Setting up mongo
MONGO_HOST = 'mongodb://localhost/tweepyDB'
client = pymongo.MongoClient(MONGO_HOST)

# Use tweepyDB if it doesnt exist create a new one
db = client.tweepyDB
dbdata = db.twitter_search1

##################- - -     MongoDB     - - -###################################################################################################
#----------------------------------------------------------------------------------------------------------------------------------------------#
TOPIC = []
#----------------------------------------------------------------------------------------------------------------------------------------------#
def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

startTimeOf1stTweet = datetime.now()
limit =  datetime.now()
for x in dbdata.find({"API_type":"Stream"}, {"_id" : 0 , "created_at": 1}).limit(1):
    startTimeOf1stTweet =datetime.strptime(x['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
    limit = startTimeOf1stTweet + timedelta(minutes=60)

for x in dbdata.find({"trend_category":{"$ne" : None}}, {"trend_category" : 1,"_id" : 0 , "created_at": 1}):
    if x['trend_category'] in TOPIC:
        continue
    elif isEnglish(x['trend_category']) != True:
        continue
    else:
        TOPIC.append(x['trend_category'])

# pTopic = ' | '.join(TOPIC)
# print(pTopic)
#----------------------------------------------------------------------------------------------------------------------------------------------#

def groupData():
    dateList = []
    NumRecord = 0

def convertStringToTime(dateData):
    datelist_ = []
    for d in dateData:
        d = d[:19]
        datelist_.append(datetime.strptime(d, '%Y-%m-%d %H:%M:%S'))
    return datelist_    

def getBucketList(dateList_):
    bucketList= []
    counter = 0
    bucketTime = 9
    buketPoint =  datetime.now()
    for dateevery10 in dateList_:
        if counter == 0:
            buketPoint = dateevery10 + timedelta(minutes=10)
            bucketList.append(bucketTime)
        # first 10mins    
        elif counter != 0 and dateevery10 <= buketPoint:
            bucketList.append(bucketTime)
        elif counter != 0 and dateevery10 >= buketPoint:
            buketPoint = buketPoint + timedelta(minutes=10)
            bucketTime = bucketTime + 10
            bucketList.append(bucketTime)
        # after first 10mins    
        counter = counter + 1 
    return bucketList

def plotGraph(xyz,label,colour):
    plt.hist(xyz, bins=[0,10,20,30,40,50,60], rwidth=0.9, alpha= 1,
                color=colour,label=label, histtype='bar')
    # plt.plot(xyz, "-",
    #             color=colour,label=label)
        
#----------------------------------------------------------------------------------------------------------------------------------------------#
bucketlist = []
colours = []
labels = []
for trend in TOPIC:
    dateList = []
    for x in dbdata.find({"trend_category" :trend},{"_id" : 0 , "created_at": 1, "API_type": 1}):
        date =datetime.strptime(x['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
        if date >= startTimeOf1stTweet and date <= limit:
            dateList.append(date)
    dateList = sorted(dateList)
    if len(dateList) == 0:
        pass
    else:
        x = getBucketList(dateList)
        bucketlist.append(x)
        colours.append("#%06x" % random.randint(0, 0xFFFFFF))
        labels.append(trend + " Count:[" + str(len(dateList)) + "]" )
        print(len(dateList))

plotGraph(bucketlist,labels,colours)
#----------------------------------------------------------------------------------------------------------------------------------------------#
 
plt.title(r'Histogram of amount of trends Data')
plt.ylabel('Trend Data Counts')
plt.xlabel('Time')
plt.legend(loc="center left",bbox_to_anchor=(1, 0.5))
plt.savefig('grouping_graph.png',bbox_inches='tight')
print("Graph saved to /graph/part(4ac)grouping_graph.png")    
    
    


    
