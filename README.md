# twitter_report_generation


Language: Python 2.7.18

Setup:
* pip install tweepy
* go to directory where code is checked out and add a file keys.json with below json in it:
{
    "ACCESS_TOKEN": "twitter_access_token",
    "ACCESS_TOKEN_SECRET": "twitter_access_token_secret",
    "CONSUMER_KEY": "twitter_consumer_key",
    "CONSUMER_SECRET": "twitter_consumer_secret"
}

* run python report_gen_script.py  (it will prompt you to enter the input keyword)
* It will start generating reports and appending it in user_report.json, link_report.json and content_report.json
 for 5 minutes along with timestamp.



Have used the Streaming API(tweepy library) to download data that is being produced on real time by twitter.

#### Steps for getting twitter credentials: 
Streaming API to get Tweets that contain certain words or hashtags and it also returned objects by the API.

1. Go to https://apps.twitter.com/ and log in with your Twitter credentials.
2. Click “create an app” (first you might have to apply for a twitter development account)
3. Fill in the form to create the application.
4. Go to “Keys and Tokens” tab to collect your tokens.
5. Create an Access token and access token secret.

And these "Access token and access token secret" had used in application that aims to collect data from any Twitter API.
Here, I have used Python Library called Tweepy to connect to the Twitter API and download the data.

I have used StreamListener module from tweepy.streaming 

