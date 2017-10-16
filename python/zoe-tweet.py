#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Support Python3 in Python2.
from __future__ import print_function

# This script makes heavy use of JSON parsing.
import json

# We check whether we are running on Windows or not.
import sys

# We play with encodings so it's good to check what we are set to support.
import locale

# Third party library; "pip install requests" if getting import errors.
import requests

# We ignore Tweepy not being installed.
try:
 tweepy = None
 import tweepy
except ImportError:
 pass

# API Gateway.
servicesHost = 'https://www.services.renault-ze.com'
myRenaultHost = 'https://www.renault.co.uk'

# Constants.
kmToMiles  = 0.621371
stealthyHeaders = { 'User-Agent': None }

def getZEAccessToken(user,password):
 url = servicesHost + '/api/user/login'
 payload = {'username':user, 'password':password}
 api_json = requests.post(url, headers=stealthyHeaders, json=payload).json()
 return api_json['token']

def apiCallZEServices(path):
 url = servicesHost + path
 headers = {'Authorization': 'Bearer ' + zeServicesAccessToken, 'User-Agent': None}
 api_json = requests.get(url, headers=headers).json()
 return api_json

def getMyReanultAccessToken(email,password):
 url = myRenaultHost + '/login-registration/_jcr_content/freeEditorial/columns6/col1-par/signuplogin_0.html'
 payload = {'email':email, 'password':password, 'page':'log-in'}
 request = requests.post(url, headers=stealthyHeaders, data=payload)
 return request.cookies

def apiCallMyRenault(mapping,sessionId):
 url = myRenaultHost + '/content/renault_prod/en_GB/index/my-account/jcr:content/subNavigation.ownedvehicles.json'
 cookies = dict([('gig_hasGmid', 'ver2'), ('X-Mapping-pjobmcgf', mapping), ('JSESSIONID', sessionId)])
 api_json = requests.get(url, headers=stealthyHeaders, cookies=cookies).json()
 return api_json

# Load credentials.
in_file = open('credentials.json', 'r')
credentials = json.load(in_file)
in_file.close()

# Generate the ZE Services token.
zeServicesAccessToken = getZEAccessToken(credentials['ZEServicesUsername'], credentials['ZEServicesPassword'])

# Get the VIN.
vin = credentials['VIN']

# ZE Services vehicle status.
status_json = apiCallZEServices('/api/vehicle/' + vin + '/battery')

# Debug
#print(status_json)

# Generate the MY Renault token.
myRenaultAccessToken = getMyReanultAccessToken(credentials['MyRenaultEmail'], credentials['MyRenaultPassword'])

# MY Renault vehicle status.
myRenault_json = apiCallMyRenault(myRenaultAccessToken['X-Mapping-pjobmcgf'], myRenaultAccessToken['JSESSIONID'])

# Debug
#print(myRenault_json)

battery          = status_json['charge_level']
remaining_range  = kmToMiles * status_json['remaining_range']
chargingStatus   = status_json['charging']
pluggedStatus    = status_json['plugged']
updateTime       = status_json['last_update']

if (chargingStatus):
 chargingText = u'Charging'
else:
 chargingText = u'Not charging'

if (pluggedStatus):
 pluggedText  = u'Plugged in'
else:
 pluggedText  = u'Unplugged'

# We allow the My Renault section to fail gracefully.
totalMileage     = 0

# Go looking for the specific VIN we have requested.
for car in myRenault_json['owned']:
 if car['vin'] == vin:
  totalMileage     = car['mileage']
  lastMileageRefresh = car['lastMileageRefresh']
  break

# Generate the status.
status  = u'\n🔋 ' + str(battery) + '%'
status += u'\n🚗 ' + str('%.0f' % round(remaining_range)) + ' miles'
status += u'\n🔌 ' + pluggedText
status += u'\n⚡ ' + chargingText
if totalMileage > 0: status += u'\n🛣️ ' + str(totalMileage) + ' miles (since ' + lastMileageRefresh + ')'
status += u'\n#RenaultZOE'

# Check the Windows console can display UTF-8 characters.
if sys.platform != 'win32' or locale.getpreferredencoding() == 'cp65001':
 print(status)
else:
 altstatus  = u'\nBattery: ' + str(battery) + '%'
 altstatus += u'\nRange: ' + str('%.0f' % round(remaining_range)) + ' miles'
 altstatus += u'\nPlugged In: ' + pluggedText
 altstatus += u'\nCharging: ' + chargingText
 if totalMileage > 0: altstatus += u'\nMileage: ' + str(totalMileage) + ' miles (since ' + lastMileageRefresh + ')'
 altstatus += u'\n#RenaultZOE'
 print(altstatus)

# Check if a Twitter library is installed.
if tweepy is not None:
 # Set Up Twitter
 twitter_access_token        = credentials['twitter_access_token']
 twitter_access_token_secret = credentials['twitter_access_token_secret']
 twitter_consumer_key        = credentials['twitter_consumer_key']
 twitter_consumer_secret     = credentials['twitter_consumer_secret']

 auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
 auth.set_access_token(twitter_access_token, twitter_access_token_secret)
 twitter = tweepy.API(auth)
 twitter.update_status(status)
else:
 print('\nTweepy not installed; unable to tweet this.')
