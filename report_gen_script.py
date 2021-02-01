from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
import time
import os
from datetime import datetime

twitter_list_of_json = []
tweets_this_minute = 0
num_tweets_per_min = []
user_report_filename = "user_report.json"
link_report_filename = "link_report.json"
content_report_filename = "content_report.json"
keys_file_name = "keys.json"

# keys from twitter for stream and listener authentication
access_token = None
access_token_secret = None
consumer_key = None
consumer_secret = None


def write_to_file(complete_file_path, json):
    file = open(complete_file_path, "a")               # append mode
    file.write(str(json) + "\n")
    file.close()


def get_current_time_in_mins():
    return datetime.now().strftime("%Y-%m-%dT%H:%M")


def get_filename(file_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, file_name)


class StdOutListener(StreamListener):

    def __init__(self, time_limit=60):
        self.start_time = time.time()
        self.limit = time_limit

    def on_data(self, data):         # on_data method of a stream listener receives all messages and calls
        global twitter_list_of_json
        global tweets_this_minute
        if time.time() - self.start_time < self.limit:
            data_dict = json.loads(data)  # here we convert JSON string into Json object
            twitter_list_of_json.append(data_dict)
            tweets_this_minute += 1
        else:
            return False

    def on_error(self, status):
        print(status)


'''
fetches data from twitter and 
returns list of jsonObjects
using stream and listener from tweepy  for 1 minute
'''


def get_twitter_data(tracklist):
    global tweets_this_minute
    global twitter_list_of_json


    listener = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, listener)

    tweets_this_minute = 0
    stream.filter(track=tracklist)
    num_tweets_per_min.append(tweets_this_minute)

    if len(num_tweets_per_min) >= 6:
        tweets_sixth_min_from_now = num_tweets_per_min.pop(0)
        twitter_list_of_json = twitter_list_of_json[tweets_sixth_min_from_now:]
        print "deleted 6th minute of data from now "

    return twitter_list_of_json


def get_user_report(twitter_list_of_json):

    user_report_list = []
    for i in twitter_list_of_json:
        user_report_list.append(i["user"])
    screen_name_dic = {}

    for i in user_report_list:
        screen_name = i['screen_name']
        if screen_name in screen_name_dic:
            screen_name_dic[screen_name] += 1
        else:
            screen_name_dic[screen_name] = 1
    return screen_name_dic


def get_links_report(twitter_list_of_json):

    links_report_list = []
    for i in twitter_list_of_json:
        links_report_list.append(i['entities']['urls'])

    final_user_profile_list = []
    for list_of_usr_dict in links_report_list:
        for usr_dict in list_of_usr_dict:
            final_user_profile_list.append(usr_dict)                           #[{u'url': u'https://t.co/MtKmx01DfO', u'indices': [42, 65], u'expanded_url': u'https://youtu.be/T-9LeTp2VOI'..}]

    urls_dict = {}
    for i in final_user_profile_list:
        url = i['expanded_url']
        if url in urls_dict:
            urls_dict[url] += 1
        else:
            urls_dict[url] = 1
    return urls_dict


def get_content_report(twitter_list_of_json):
    text_list = []
    exclude = ['is', 'in', 'not', 'too', 'to', 'I', 'has', 'for', 'if', 'by', 'a', 'your', 'on', 'with', 'will',
               'it', 'and', 'am', 'are', 'we', 'look', 'the', 'like', 'she', 'he', 'her', 'have', 'his', 'of',
               'from', 'you', 'this', 'A', 'who', 'How', 'be', 'that']

    for i in twitter_list_of_json:
        text_list.append(i['text'])

    list_of_words = []

    for text in text_list:
        tweet_text_words = text.split()
        for word in tweet_text_words:
            if word not in exclude:
                list_of_words.append(word)

    # print "list_of_words", list_of_words
    # [u'@shanti0207:', u'Modi', u'govt', u'trying', u'Gujarat', u'Model']

    dic_of_words = {}
    for i in list_of_words:
        if i in dic_of_words:
            dic_of_words[i] += 1
        else:
            dic_of_words[i] = 1

    # print "dic_of_words", dic_of_words
    # #{u'Canada': 125, u'all': 730, u'kuttye.esse': 87, u'Sidhu': 59, u'government.': 17, u'paale': 85}

    words_sorted_by_occurence = []
    for k in sorted(dic_of_words, key=dic_of_words.get, reverse=True):
        words_sorted_by_occurence.append(k)

    return len(words_sorted_by_occurence), words_sorted_by_occurence[:10]           #[u'RT', u'Modi', u'\u0915\u0947', u'#ModiPlanningFarmerGenocide', u'be', u'that', u'farmers', u'all', u'PM']


def generate_user_report(user_report_data):
    user_report_json = json.dumps(user_report_data)
    json_output = json.loads("{}")
    json_output["timestamp"] = get_current_time_in_mins()
    json_output["user_tweet_counts"] = user_report_json

    #print "json generated: " + str(json_output)
    write_to_file(get_filename(user_report_filename), json_output)
    print "written the generate_link_report data in : " + user_report_filename + " for time: " + get_current_time_in_mins()


def generate_link_report(link_report_data):
    link_report_json = json.dumps(link_report_data)
    json_output = json.loads("{}")
    json_output["timestamp"] = get_current_time_in_mins()
    json_output["user_link_counts"] = link_report_json

    # print "json generated: " + str(json_output)
    write_to_file(get_filename(link_report_filename), json_output)
    print "written the generate_link_report data in : " + link_report_filename + " for time: " + get_current_time_in_mins()


def generate_content_report(content_report_data):
    content_report_json = json.dumps(content_report_data)
    json_output = json.loads("{}")
    json_output["timestamp"] = get_current_time_in_mins()
    json_output["user_content_counts"] = content_report_json

    write_to_file(get_filename(content_report_filename), json_output)
    print "written the content_report data in : " + content_report_filename + " for time: " + get_current_time_in_mins()

def initializeKeys():
    global access_token
    global access_token_secret
    global consumer_key
    global consumer_secret

    filename = get_filename(keys_file_name)
    file_object = open(filename)
    key_dict = json.load(file_object)

    access_token = key_dict["ACCESS_TOKEN"]
    consumer_key = key_dict["CONSUMER_KEY"]
    consumer_secret = key_dict["CONSUMER_SECRET"]
    access_token_secret = key_dict["ACCESS_TOKEN_SECRET"]

    if access_token == None or consumer_key == None or access_token_secret == None or consumer_secret == None:
        raise Exception("we have an issue with authentication keys not found")


if __name__ == '__main__':
    print "initaling keys"
    initializeKeys()

    print "Script to generate reports starts... "

    print "Enter the keywords for which you want to stream twitter: "
    tracklist = raw_input().split()
    print tracklist

    while True:

        print "Fetching data from twitter: ..."
        twitter_data_list = get_twitter_data(tracklist)
        print "Fetched " + str(len(twitter_data_list)) + ": records from twitter in list of json objects."

        print "Getting user report data from twitter json data: "
        user_report_data = get_user_report(twitter_data_list)
        print "Total users in user report data: " + str(len(user_report_data))
        generate_user_report(user_report_data)


        print "Getting links report data from twitter json data"
        links_report_data = get_links_report(twitter_data_list)
        print "Total links in links report data: " + str(len(links_report_data))
        generate_link_report(links_report_data)

        print "Getting content report data from twitter json data: "
        total_words, content_report_data = get_content_report(twitter_data_list)
        print "Total words in content report data:" + str(total_words) + ", also fetched top 10 words."
        generate_content_report(content_report_data)



