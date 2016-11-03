#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json, tweepy, requests

#	API Gateway
host = "https://www.services.renault-ze.com"

#	Constants
kmToMiles  = 0.621371

def apiCall(path):
	url = host + path
	headers = {"Authorization": "Bearer " + access_token}
	r = requests.get(url, headers=headers)
	api_json = r.json()

	return api_json

def getAccessToken(user,password):
	url = host + "/api/user/login"
	payload = {'username':user,'password':password}
	r = requests.post(url, json=payload)
        api_json = r.json()

        return api_json["token"]

#   Load Credentials
in_file = open("credentials.json","r")
credentials = json.load(in_file)
in_file.close()

#	Generate the token
user     = credentials["username"]
password = credentials["password"]
access_token = getAccessToken(user, password)

#	Get the VIN
vin = credentials["VIN"]

#	Vehicle Status
status_url  = "/api/vehicle/"+vin+"/battery"
status_json = apiCall(status_url)

#	Debug
#print status_json

battery          = status_json["charge_level"]
remaining_range  = kmToMiles * status_json["remaining_range"]
chargingStatus   = status_json["charging"]
pluggedStatus    = status_json["plugged"]
updateTime       = status_json["last_update"]

if (chargingStatus):
	chargingText = u"Charging"
else:
	chargingText = u"Not charging"

if (pluggedStatus):
	pluggedText  = u"Plugged in"
else:
	pluggedText  = u"Unplugged"

#	Set Up Twitter
twitter_access_token        = credentials["twitter_access_token"]
twitter_access_token_secret = credentials["twitter_access_token_secret"]
twitter_consumer_key        = credentials["twitter_consumer_key"]
twitter_consumer_secret     = credentials["twitter_consumer_secret"]

auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
auth.set_access_token(twitter_access_token, twitter_access_token_secret)
twitter = tweepy.API(auth)

#	Generate the Tweet
tweet  = u"\n🔋 " + str(battery) + "%"
tweet += u"\n🚗 " + str("%.0f" % round(remaining_range)) + " miles"
tweet += u"\n🔌 " + pluggedText
tweet += u"\n⚡ " + chargingText
tweet += u"\n⚠ Secured and Locked"
tweet += u"\n#RenaultZOE"

print tweet

twitter.update_status(tweet)
