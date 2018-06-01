#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Support Python3 in Python2.
from __future__ import print_function

# All the shared functions are in this package.
from shared.zeservices import ZEServices
from shared.myrenault import MYRenault

# This script makes heavy use of JSON parsing.
import json

# We check whether we are running on Windows or not.
import sys

# We play with encodings so it's good to check what we are set to support.
import locale

# We ignore Tweepy not being installed.
try:
 tweepy = None
 import tweepy
except ImportError:
 pass

# Constants.
kmToMiles  = 0.621371

# Load credentials.
in_file = open('credentials.json', 'r')
credentials = json.load(in_file)
in_file.close()

# Get the VIN.
vin = credentials['VIN']

# Create a ZE Services object.
zeServices = ZEServices(credentials['ZEServicesUsername'], credentials['ZEServicesPassword'])

# ZE Services vehicle status.
zeServices_json = zeServices.apiCall('/api/vehicle/' + vin + '/battery')

battery         = zeServices_json['charge_level']
remaining_range = kmToMiles * zeServices_json['remaining_range']
charging        = zeServices_json['charging']
pluggedIn       = zeServices_json['plugged']
updateTime      = zeServices_json['last_update']
if charging: remaining_time = zeServices_json['remaining_time'] if 'remaining_time' in zeServices_json else None

# (Optionally) Create a MY Renault object.
if 'MyRenaultEmail' in credentials and 'MyRenaultPassword' in credentials:
 myRenault = MYRenault(credentials['MyRenaultEmail'], credentials['MyRenaultPassword'])

 # MY Renault vehicle status.
 myRenault_json = myRenault.apiCall()

 # We allow the MY Renault section to fail gracefully (if it cannot find our VIN).
 totalMileage     = 0

 # Go looking for the specific VIN we have requested.
 for car in myRenault_json['owned']:
  if car['vin'] == vin:
   totalMileage     = car['mileage']
   if 'MyRenaultMileageOffset' in credentials: totalMileage += credentials['MyRenaultMileageOffset']
   lastMileageRefresh = car['lastMileageRefresh']
   break
else:
 # We allow the MY Renault section to fail gracefully (if we have not set it up).
 totalMileage     = 0

# Generate the status.
status  = u'\n🔋 ' + str(battery) + '%'
status += u'\n🚗 ' + str('%.0f' % round(remaining_range)) + ' miles'
status += u'\n🔌 ' + ('Plugged in' if pluggedIn else 'Unplugged')
status += u'\n⚡ ' + ('Charging ' + ('(' + str(remaining_time) + ' minutes remain)' if remaining_time is not None else '') if charging else 'Not charging')
if totalMileage > 0: status += u'\n🛣️ ' + str(totalMileage) + ' miles (since ' + lastMileageRefresh + ')'
status += '\n#RenaultZOE'

# Check the Windows console can display UTF-8 characters.
if sys.platform != 'win32' or locale.getpreferredencoding() == 'cp65001':
 # Display the UTF-8 status (with emojis).
 print(status)
else:
 # Generate an ASCII standard text status.
 altstatus  = '\nBattery: ' + str(battery) + '%'
 altstatus += '\nRange: ' + str('%.0f' % round(remaining_range)) + ' miles'
 altstatus += '\nPlugged In: ' + ('Plugged in' if pluggedIn else 'Unplugged')
 altstatus += '\nCharging: ' + ('Charging ' + ('(' + str(remaining_time) + ' minutes remain)' if remaining_time is not None else '') if charging else 'Not charging')
 if totalMileage > 0: altstatus += u'\nMileage: ' + str(totalMileage) + ' miles (since ' + lastMileageRefresh + ')'
 altstatus += '\n#RenaultZOE'
 print(altstatus)

# Check if a Twitter library is installed.
if tweepy is not None:
 # Set up Twitter
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
