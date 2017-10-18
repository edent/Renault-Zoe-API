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

# Create a MY Renault object.
myRenault = MYRenault(credentials['MyRenaultEmail'], credentials['MyRenaultPassword'])

# MY Renault vehicle status.
myRenault_json = myRenault.apiCall()

battery          = zeServices_json['charge_level']
remaining_range  = kmToMiles * zeServices_json['remaining_range']
chargingStatus   = zeServices_json['charging']
pluggedStatus    = zeServices_json['plugged']
updateTime       = zeServices_json['last_update']

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

# Check the Windows console can display UTF-8 characters.
if sys.platform != 'win32' or locale.getpreferredencoding() == 'cp65001':
 # Generate the status.
 status  = u'\n🔋 ' + str(battery) + '%'
 status += u'\n🚗 ' + str('%.0f' % round(remaining_range)) + ' miles'
 status += u'\n🔌 ' + pluggedText
 status += u'\n⚡ ' + chargingText
 if totalMileage > 0: status += u'\n🛣️ ' + str(totalMileage) + ' miles (since ' + lastMileageRefresh + ')'
else:
 status  = u'\nBattery: ' + str(battery) + '%'
 status += u'\nRange: ' + str('%.0f' % round(remaining_range)) + ' miles'
 status += u'\nPlugged In: ' + pluggedText
 status += u'\nCharging: ' + chargingText
 if totalMileage > 0: status += u'\nMileage: ' + str(totalMileage) + ' miles (since ' + lastMileageRefresh + ')'

print(status)