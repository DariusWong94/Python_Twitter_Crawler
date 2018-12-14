import praw
import time
import json
import pymongo
import threading
import datetime
# Setting up mongo
MONGO_HOST = 'mongodb://localhost/redditDB'
client = pymongo.MongoClient(MONGO_HOST)

# Use redditDB if it doesnt exist create a new one
db = client.redditDB
redditDatabase = db.reddit_search

reddit = praw.Reddit(client_id='bGjd-GkJD7pESg',
                     client_secret='-LSki7j7xzEwlzgmwg1vBqxatuc',
                     user_agent='Reddit Crawler')

# Getting top trends list
TrendsList = []
for result in reddit.subreddit('trendingsubreddits').hot(limit=15):
    print result.title
    TrendsList += result.title[36:].replace('/r/', '').replace(' ', '').split(",")
    print TrendsList
TrendsList_='' + '+'.join(TrendsList) +''

# Thread 1: Stream API
def streaming():
    for comment in reddit.subreddit(TrendsList_).stream.comments():
        dbComment = {
            "author" : str(comment.author),
            "body" : comment.body,
            "created_utc" : datetime.datetime.utcfromtimestamp(comment.created_utc),
            "distinguished" : comment.distinguished,
            "edited" : comment.edited,
            "id" : comment.id,
            "is_submitter" : comment.is_submitter,
            "link_id" : comment.link_id,
            "parent_id" : comment.parent_id,
            "permalink" : comment.permalink,
            "score" : comment.score,
            "stickied" : comment.stickied,
            "submission" : str(comment.submission),
            "subreddit" : str(comment.subreddit),
            "subreddit_id" : comment.subreddit_id,
            "api_type" : "Stream"
        }
        redditDatabase.insert(dbComment)

# Thread 2: Rest API
def rest():
    time.sleep(60 * 60)
    print("-------------------Start Rest-------------------")
    starttime = time.time()
    timeout = starttime + 60*60
    for submission in reddit.subreddit(TrendsList_).hot():
        if (time.time() >= timeout):
            break
        submission.comments.replace_more(limit=None)
        for comment in submission.comments.list():
            if (time.time() >= timeout):
                break
            dbComment = {
                "body" : comment.body,
                "author" : str(comment.author),
                "created_utc" : datetime.datetime.utcfromtimestamp(comment.created_utc),
                "distinguished" : comment.distinguished,
                "edited" : comment.edited,
                "id" : comment.id,
                "is_submitter" : comment.is_submitter,
                "link_id" : comment.link_id,
                "parent_id" : comment.parent_id,
                "permalink" : comment.permalink,
                "score" : comment.score,
                "stickied" : comment.stickied,
                "submission" : str(comment.submission),
                "subreddit" : str(comment.subreddit),
                "subreddit_id" : comment.subreddit_id,
                "api_type" : "Rest"
            }
            redditDatabase.insert(dbComment)
    print("Time limit reached, stopping Rest API Thread")

# Do analysis every 1 min 
def analysis():
    print("Analysis Thread Started.....")
    timeElapsed = -1
    starttime = time.time()
    timeout = starttime + 60*60*2
    while (time.time() <= timeout):
        print("-------------------Analyics------------------")
        print("Stream API count: " + str(redditDatabase.find({"api_type" : "Stream"}).count()))
        print("Rest API count: " + str(redditDatabase.find({"api_type" : "Rest"}).count()))
        print("Number of Subreddits: " + str(len(redditDatabase.distinct("subreddit_id"))))
        print("Number of Submissions: " + str(len(redditDatabase.distinct("submission_id"))))
        print("Number of comments: " + str(redditDatabase.count()))
        timeElapsed = timeElapsed + 1
        print("Time Elapsed: " + str(timeElapsed) + " Mins")
        time.sleep(60)
    print("Time limit reached, stopping Analysis Thread")

# Multi-Threading 
t1 = threading.Thread(target=streaming, args=())
t2 = threading.Thread(target=rest, args=())
t3 = threading.Thread(target=analysis, args=())

t1.start()
t2.start()
t3.start()