#!/usr/bin/env python

# Third party library; "pip install requests" if getting import errors.
import requests

class ZEServices:

 # API Gateway.
 servicesHost = 'https://www.services.renault-ze.com'

 # This prevents the requests module from creating its own user-agent.
 stealthyHeaders = { 'User-Agent': None }

 def __init__(self, user, password):
  # Generate the ZE Services token.
  self.accessToken = self.getAccessToken(user, password)
 
 def getAccessToken(self, user, password):
  url = ZEServices.servicesHost + '/api/user/login'
  payload = {'username':user, 'password':password}
  api_json = requests.post(url, headers=ZEServices.stealthyHeaders, json=payload).json()
  return api_json['token']

 def apiCall(self, path):
  url = ZEServices.servicesHost + path
  headers = {'Authorization': 'Bearer ' + self.accessToken, 'User-Agent': None}
  return requests.get(url, headers=headers).json()