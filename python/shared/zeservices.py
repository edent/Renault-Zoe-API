#!/usr/bin/env python

# Third party library; "pip install requests" if getting import errors.
import requests

# We use JSON to parse tokens and our token file storage.
import json

# We read JWT tokens which are base64 encoded.
import base64

# We check the token expiry time.
import time

class ZEServices:

 # API Gateway.
 servicesHost = 'https://www.services.renault-ze.com'

 # This prevents the requests module from creating its own user-agent.
 stealthyHeaders = {'User-Agent': None, 'DNT':'1'}

 def __init__(self, user, password):
  # Generate the ZE Services token.
  self.accessToken = self.getAccessToken(user, password)

 def getAccessToken(self, user, password):
  try:
   # File contains refresh_token followed by the JWT token.
   with open('credentials_token.json', 'r') as tokenStorage:
    tokenData = json.load(tokenStorage)

   # We could be using python_jwt but even the official ZE Services ("decodeToken") does it this crude way, so why overcomplicate things?
   splitToken = tokenData['token'].split('.')

   # Check it looks semi-valid.
   if len(splitToken) != 3: raise ValueError('Not a well formed JWT token')

   # Get the JSON payload of the JWT token.
   jsonPayload = base64.b64decode(splitToken[1])

   # Parse it as JSON.
   token = json.loads(jsonPayload)

   # Is the token still valid?
   if (time.gmtime() < time.gmtime(token['exp'])):
    # Just return the token as-is.
    return tokenData['token']
   # No, it expired.
   else:
     url = ZEServices.servicesHost + '/api/user/token/refresh'

     # We just send the file as we are not adding anything else into it, if this changes the following 2 key-value pairs are mandatory.
     #payload = {'refresh_token': tokenData['refresh_token'], 'token': tokenData['token']}
     payload = tokenData

     response = requests.post(url, headers=ZEServices.stealthyHeaders, json=payload).json()

     # Overwrite the current token with this newly returned one.
     tokenData['token'] = response['token']

     # Save this refresh token and new JWT token so we are nicer to Renault's authentication server.
     with open('credentials_token.json', 'w') as outfile:
      json.dump(tokenData, outfile)

  # We have never cached an access token before.
  except FileNotFoundError:
   url = ZEServices.servicesHost + '/api/user/login'
   payload = {'username':user, 'password':password}
   api_json = requests.post(url, headers=ZEServices.stealthyHeaders, json=payload).json()

   # We do not want to save all the user data returned on login, so we create a smaller file of just the mandatory information.
   tokenData = {'refresh_token' : api_json['refresh_token'], 'token' : api_json['token']}

   # Save this refresh token and JWT token for future use so we are nicer to Renault's authentication server.
   with open('credentials_token.json', 'w') as outfile:
    json.dump(tokenData, outfile)

   # The script will just want the token.
   return api_json['token']

 def apiCall(self, path):
  url = ZEServices.servicesHost + path
  headers = {'Authorization': 'Bearer ' + self.accessToken, 'User-Agent': None}
  return requests.get(url, headers=headers).json()