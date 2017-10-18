#!/usr/bin/env python

# Third party library; "pip install requests" if getting import errors.
import requests

class MYRenault:

 # API Gateway.
 myRenaultHost = 'https://www.renault.co.uk'

 # This prevents the requests module from creating its own user-agent.
 stealthyHeaders = { 'User-Agent': None }

 def __init__(self, email, password):
  # Generate the MY Renault token.
  accessToken = self.getAccessToken(email, password)

  # There's only 2 cookie values that are important to confirm we are authenticated.

  # Renault use a load balancer (vADC) : https://community.brocade.com/t5/vADC-Docs/What-s-the-X-Mapping-cookie-for-and-does-it-constitute-a/ta-p/73638
  self.mapping = accessToken['X-Mapping-pjobmcgf']

  # This links our future requests to our existing login.
  self.sessionId = accessToken['JSESSIONID']

 def getAccessToken(self, email, password):
  url = MYRenault.myRenaultHost + '/login-registration/_jcr_content/freeEditorial/columns6/col1-par/signuplogin_0.html'
  payload = {'email':email, 'password':password, 'page':'log-in'}
  return requests.post(url, headers=MYRenault.stealthyHeaders, data=payload).cookies

 def apiCall(self):
  url = MYRenault.myRenaultHost + '/content/renault_prod/en_GB/index/my-account/jcr:content/subNavigation.ownedvehicles.json'
  cookies = dict([('gig_hasGmid', 'ver2'), ('X-Mapping-pjobmcgf', self.mapping), ('JSESSIONID', self.sessionId)])
  return requests.get(url, headers=MYRenault.stealthyHeaders, cookies=cookies).json()