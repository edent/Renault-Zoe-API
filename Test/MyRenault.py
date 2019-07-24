#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import aiohttp
import json
import urllib

async def get_android_config(session, location):
    url = 'https://renault-wrd-prod-1-euw1-myrapp-one.s3-eu-west-1.amazonaws.com/configuration/android/config_' + location + '.json'
    print(url)
    async with session.get(url) as response:
        responsetext = await response.text()
        if responsetext == '':
            responsetext = '{}'
        jsonresponse = json.loads(responsetext)
        if 'message' in jsonresponse:
            self.tokenData = None
            raise MyRenaultServiceException(jsonresponse['message'])
        return jsonresponse

async def get_gigyasession(session, gigyarooturl, gigyaapikey, loginID, password):
    payload = {'loginID': loginID, 'password': password, 'apiKey': gigyaapikey}
    url = gigyarooturl + '/accounts.login?' + urllib.parse.urlencode(payload)
    print(url)
    async with session.get(url) as response:
        responsetext = await response.text()
        if responsetext == '':
            responsetext = '{}'
        jsonresponse = json.loads(responsetext)
        if 'message' in jsonresponse:
            self.tokenData = None
            raise MyRenaultServiceException(jsonresponse['message'])
        return jsonresponse

async def get_gigyaaccount(session, gigyarooturl, gigyaapikey, gigyacookievalue):
    payload = {'oauth_token': gigyacookievalue}
    url = gigyarooturl + '/accounts.getAccountInfo?' + urllib.parse.urlencode(payload)
    print(url)
    async with session.get(url) as response:
        responsetext = await response.text()
        if responsetext == '':
            responsetext = '{}'
        jsonresponse = json.loads(responsetext)
        if 'message' in jsonresponse:
            self.tokenData = None
            raise MyRenaultServiceException(jsonresponse['message'])
        return jsonresponse

async def get_gigyajwt(session, gigyarooturl, gigyaapikey, gigyacookievalue):
    payload = {'oauth_token': gigyacookievalue, 'fields': 'data.personId,data.gigyaDataCenter', 'expiration': 900}
    url = gigyarooturl + '/accounts.getJWT?' + urllib.parse.urlencode(payload)
    print(url)
    async with session.get(url) as response:
        responsetext = await response.text()
        if responsetext == '':
            responsetext = '{}'
        jsonresponse = json.loads(responsetext)
        if 'message' in jsonresponse:
            self.tokenData = None
            raise MyRenaultServiceException(jsonresponse['message'])
        return jsonresponse

async def get_kamereonperson(session, kamereonrooturl, kamereonapikey, gigya_jwttoken, personId):
    payload = {'country': 'FR'}
    headers = {'x-gigya-id_token': gigya_jwttoken, 'apikey': kamereonapikey}
    url = kamereonrooturl + '/commerce/v1/persons/' + personId + '?' + urllib.parse.urlencode(payload)
    print(url)
    async with session.get(url, headers=headers) as response:
        responsetext = await response.text()
        if responsetext == '':
            responsetext = '{}'
        jsonresponse = json.loads(responsetext)
        if 'message' in jsonresponse:
            self.tokenData = None
            raise MyRenaultServiceException(jsonresponse['message'])
        return jsonresponse

async def get_kamereontoken(session, kamereonrooturl, kamereonapikey, gigya_jwttoken, accountId):
    payload = {'country': 'FR'}
    headers = {'x-gigya-id_token': gigya_jwttoken, 'apikey': kamereonapikey}
    url = kamereonrooturl + '/commerce/v1/accounts/' + accountId + '/kamereon/token?' + urllib.parse.urlencode(payload)
    print(url)
    async with session.get(url, headers=headers) as response:
        responsetext = await response.text()
        if responsetext == '':
            responsetext = '{}'
        jsonresponse = json.loads(responsetext)
        if 'message' in jsonresponse:
            self.tokenData = None
            raise MyRenaultServiceException(jsonresponse['message'])
        return jsonresponse

async def get_batterystatus(session, kamereonrooturl, kamereonapikey, gigya_jwttoken, kamereonaccesstoken, vin):
    headers = {'x-gigya-id_token': gigya_jwttoken, 'apikey': kamereonapikey, 'x-kamereon-authorization' : 'Bearer ' + kamereonaccesstoken}
    url = kamereonrooturl + '/commerce/v1/accounts/kmr/remote-services/car-adapter/v1/cars/' + vin + '/battery-status'
    print(url)
    async with session.get(url, headers=headers) as response:
        responsetext = await response.text()
        if responsetext == '':
            responsetext = '{}'
        jsonresponse = json.loads(responsetext)
        if 'message' in jsonresponse:
            self.tokenData = None
            raise MyRenaultServiceException(jsonresponse['message'])
        return jsonresponse

async def main():
    async with aiohttp.ClientSession(
            ) as session:
        await mainwithsession(session)

async def mainwithsession(session):
    # Load credentials.
    in_file = open('credentials.json', 'r')
    credentials = json.load(in_file)
    in_file.close()

    #android_config = await get_android_config(session, credentials['RenaultServiceLocation'])
    #with open('android_config.json', 'w') as outfile:
    #    json.dump(android_config, outfile)
    in_file = open('android_config.json', 'r')
    android_config = json.load(in_file)
    in_file.close()
    print('android_config')
    
    gigyarooturl = android_config['servers']['gigyaProd']['target']
    gigyaapikey = android_config['servers']['gigyaProd']['apikey']

    kamereonrooturl = android_config['servers']['wiredProd']['target']
    kamereonapikey = android_config['servers']['wiredProd']['apikey']
    
    gigya_session = await get_gigyasession(session, gigyarooturl, gigyaapikey, credentials['RenaultServicesUsername'], credentials['RenaultServicesPassword'])
    with open('gigya_session.json', 'w') as outfile:
        json.dump(gigya_session, outfile)
    #in_file = open('gigya_session.json', 'r')
    #gigya_session = json.load(in_file)
    #in_file.close()
    print('gigya_session')
    
    gigyacookievalue = gigya_session['sessionInfo']['cookieValue']

    #gigya_account = await get_gigyaaccount(session, gigyarooturl, gigyaapikey, gigyacookievalue)
    #with open('gigya_account.json', 'w') as outfile:
    #    json.dump(gigya_account, outfile)
    in_file = open('gigya_account.json', 'r')
    gigya_account = json.load(in_file)
    in_file.close()
    print('gigya_account')

    gigya_jwt = await get_gigyajwt(session, gigyarooturl, gigyaapikey, gigyacookievalue)
    with open('gigya_jwt.json', 'w') as outfile:
        json.dump(gigya_jwt, outfile)
    #in_file = open('gigya_jwt.json', 'r')
    #gigya_jwt = json.load(in_file)
    #in_file.close()
    print('gigya_jwt')
    
    gigya_jwttoken= gigya_jwt['id_token']
    
    kamereonpersonid = gigya_account['data']['personId']
    
    #kamereon_person = await get_kamereonperson(session, kamereonrooturl, kamereonapikey, gigya_jwttoken, kamereonpersonid)
    #with open('kamereon_person.json', 'w') as outfile:
    #    json.dump(kamereon_person, outfile)
    in_file = open('kamereon_person.json', 'r')
    kamereon_person = json.load(in_file)
    in_file.close()
    print('kamereon_person')

    kamereonaccountid = kamereon_person['accounts'][0]['accountId']

    kamereon_token = await get_kamereontoken(session, kamereonrooturl, kamereonapikey, gigya_jwttoken, kamereonaccountid)
    with open('kamereon_token.json', 'w') as outfile:
        json.dump(kamereon_token, outfile)
    print('kamereon_token')
    
    kamereonaccesstoken = kamereon_token['accessToken']

    kamereon_battery = await get_batterystatus(session, kamereonrooturl, kamereonapikey, gigya_jwttoken, kamereonaccesstoken, credentials['VIN'])
    print(kamereon_battery)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
