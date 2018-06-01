#!/usr/bin/env python

# Third party library; "pip install requests" if getting import errors.
import requests

class MYRenault:

 # API Gateway.
 myRenaultHost = 'https://www.renault.co.uk'

 # This prevents the requests module from creating its own user-agent (and ask to not be included in analytics).
 stealthyHeaders = {'User-Agent': None, 'DNT':'1'}

 def __init__(self, email, password):

  # We now need to be assigned a session *before* we can login.
  self.getSession()

  # Authenticate with MY Renault.
  if not self.login(email, password):
   raise ValueError('Failed to login to MyRenault')

 def getSession(self):
  url = MYRenault.myRenaultHost + '/login-registration.html'

  # There's only 2 cookie values that are important to maintain session once we are authenticated.
  cookies = requests.get(url, headers=MYRenault.stealthyHeaders).cookies

  # X-Mapping - Renault use a load balancer (vADC) to specify an assigned server, https://community.brocade.com/t5/vADC-Docs/What-s-the-X-Mapping-cookie-for-and-does-it-constitute-a/ta-p/73638
  # JSESSIONID - This links our future requests to our existing session on this server.
  self.sessionCookies = {'X-Mapping-pjobmcgf': cookies['X-Mapping-pjobmcgf'], 'JSESSIONID': cookies['JSESSIONID']}

 def login(self, email, password):
  url = MYRenault.myRenaultHost + '/login-registration/_jcr_content/freeEditorial/columns6/col1-par/signuplogin_0.html'
  payload = {'email':email, 'password':password, 'page':'log-in'}
  response = requests.post(url, headers=MYRenault.stealthyHeaders, cookies=self.sessionCookies, data=payload).json()
  return (('status_code' in response) and (response['status_code'] == 'login_success'))

 def apiCall(self):
  url = MYRenault.myRenaultHost + '/content/renault_prod/en_GB/index/my-account/jcr:content/subNavigation.ownedvehicles.json'
  return requests.get(url, headers=MYRenault.stealthyHeaders, cookies=self.sessionCookies).json()