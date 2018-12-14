import tweepy
import twitter_credentials
import pymongo
import json
import datetime
import time
import threading

# Setting up mongo
MONGO_HOST = 'mongodb://localhost/tweepyDB'
client = pymongo.MongoClient(MONGO_HOST)

# Use tweepyDB if it doesnt exist create a new one
db = client.tweepyDB
tweepyDatabase = db.twitter_search1

# Top trend list
TopTrends = []

# Set up Twitter authentication
auth = tweepy.OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


# Method to store data to database
def Insert_To_DB(datajson, apitype , trendCategory ):
    # Load all of the extracted Tweet data into the variable "tweet" that will be stored into the database
    tweet = {'API_type' : apitype , 'trend_category' : trendCategory }
    tweet.update(datajson)
    tweepyDatabase.insert(tweet)

# Check if ascii
def is_ascii(s):
    return all(ord(c) < 128 for c in s)

# Method to get top trends using singapore WOEID 
def GetTopTrends():
    trendsData = api.trends_place(id="23424948")
    for trend in trendsData[0]["trends"]:
        noHashTrend = trend["name"].replace("#" , "")
        if(is_ascii(noHashTrend) == True):
            TopTrends.append(noHashTrend)
        else:
            pass
    return TopTrends

# Main memthod
if __name__ == '__main__':
     GetTopTrends()

# Twitter Stream listener
class StdListener(tweepy.StreamListener):
    """
    This is a basic listener that just prints received tweets to stdout.
    """
    def on_data(self, data):
        try:
            datajson = json.loads(data)
            text = ""
            try:
                text = datajson["extended_tweet"]["full_text"].encode(errors="ignore").decode("utf-8")
            except Exception as e:
                text = datajson["text"].encode(errors="ignore").decode("utf-8")
            apitype = "Stream"
            if any(word in text for word in TopTrends):
                matched = [i for i in TopTrends if i in text]
                trendCategory = matched[0]
            else:
                trendCategory = "others"
            if datajson["place"]["country"] == "Singapore":      
                Insert_To_DB(datajson, apitype , trendCategory)
            ##print(data)
        except BaseException as e:
            print("Error on_data %s" % str(e))
            
    def on_error(self, status):
        if status == 420:
            print("error", status)
            time.sleep(15 * 60)  
            return True
        
# Thread 1: Stream API
def Stream_Tweets(api):
    locationBoundingBox = [103.603813,1.221886,104.039147,1.478619]
    stream = tweepy.Stream(api.auth, StdListener())
    stream.filter(locations=locationBoundingBox)

# Thread 2: Rest API
def Rest_API(api):
    time.sleep(60 * 60)
    print("--------------------------Rest Api--------------------------")
    for trend in TopTrends:
        for data in tweepy.Cursor(api.search,q=trend,geocode="1.352083,103.819839,25km", resultype="recent").items():
            apitype = "Rest"
            trendCategory  = trend
            DateRetrieved = str(datetime.datetime.now())
            Insert_To_DB(data._json,apitype , trendCategory)

#Thread 3: Print analytics
def Print_Analytics(): 
    while True:
        print("--------------------------Analytics--------------------------")
        print("Total collection data: " + str(tweepyDatabase.count()))
        print("Stream API data:" + str(tweepyDatabase.find({"API_type" : "Stream"}).count()))
        print("Rest API data: " + str(tweepyDatabase.find({"API_type" : "Rest"}).count()))
        print("Geo-Tagged data: " + str(tweepyDatabase.find({"geo" :{"$ne" : None}}).count()))
        print("Location code with 'Singapore' count: " + str(tweepyDatabase.find({"geo" :{"$ne" : None}, "place.country_code" : "SG"}).count()))
        print("Duplicate data: " + str((tweepyDatabase.count() - len(tweepyDatabase.distinct("id")))))
        print("Twitter Quote data: " + str(tweepyDatabase.find({"is_quote_status" : True}).count()))
        print("Twitter Retweet data: " + str(tweepyDatabase.find({"retweeted_status" : {"$ne" : None}}).count()))
        print TopTrends
        time.sleep(30)

#Multi-Threading
t1 = threading.Thread(target=Stream_Tweets, args=(api,))
t2 = threading.Thread(target=Rest_API, args=(api,))
t3 = threading.Thread(target=Print_Analytics, args=())

t1.start()
t2.start()
t3.start()

t1.join()
t2.join()
t3.join()