#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Xibo - Digital Signage - http://www.xibo.org.uk
# Copyright (C) 2009-2012 Alex Harrington
#
# This file is part of Xibo.
#
# Xibo is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version. 
#
# Xibo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Xibo.  If not, see <http://www.gnu.org/licenses/>.
#

##############
##
## This is part of the Xibo Test Suite.
## OAuth Setup
##
##############

# Imports
import urlparse
import urllib
import oauth2 as oauth
import ConfigParser
from xml.dom import minidom
import base64
import hashlib

class XiboAPI:
    def __init__(self,fileName='site.cfg',fromConfigFile=True,message=None,verbose=True):
        self.__connected__ = False
        self.__consumer__ = None
        self.__client__ = None
        self.__token__ = None
        self.__verbose__ = verbose

        if fromConfigFile:
            # TODO: Lots of possible exceptions can get thrown here.
            # Either they should be handled or code calling this needs to know it can blow up on them.
            self.config = ConfigParser.ConfigParser()
            self.config.readfp(open('defaults.cfg'))
            self.config.read([fileName])

            consumer_key = self.config.get('Main','consumer_key')
            consumer_secret = self.config.get('Main','consumer_secret')

            if self.config.get('Main','url') == "NULL":
                raise RuntimeError('No Server URL has been configured.')

            url = self.tidyUrl(self.config.get('Main','url'))

            user_token = self.config.get('Main','token')
            user_secret = self.config.get('Main','secret')

            if user_token == "NULL":
                if message != None:
                    print message
                user_token, user_secret = self.setupUserToken(url,consumer_key,consumer_secret)

                config2 = ConfigParser.RawConfigParser()
                config2.add_section('Main')
                config2.set('Main', 'token', user_token)
                config2.set('Main', 'secret', user_secret)
                config2.set('Main', 'url', url)

                with open(fileName, 'wb') as configfile:
                    config2.write(configfile)

                config2 = None

            self.connect(url,consumer_key,consumer_secret,user_token,user_secret)

    def setupUserToken(self,url,consumer_key,consumer_secret):
        # ATTRIBUTION:
        # This code is based heavily on the "Twitter Three-legged OAuth Example" from
        # http://github.com/simplegeo/python-oauth2/blob/master/README.md
        # by SimpleGEO (http://simplegeo.com/)

        # Step 1: Get a request token. This is a temporary token that is used for 
        # having the user authorize an access token and to sign the request to obtain 
        # said access token.

        consumer = oauth.Consumer(consumer_key, consumer_secret)
        client = oauth.Client(consumer)

        resp, content = client.request(self.access_urls(url)['request_token_url'], "GET")
        if resp['status'] != '200':
            raise Exception("Invalid response %s." % resp['status'])

        request_token = dict(urlparse.parse_qsl(content))

        if self.__verbose__:
            print "Request Token:"
            print "    - oauth_token        = %s" % request_token['oauth_token']
            print "    - oauth_token_secret = %s" % request_token['oauth_token_secret']
            print 

        # Step 2: Redirect to the provider. Since this is a CLI script we do not 
        # redirect. In a web application you would redirect the user to the URL
        # below.

        print "Go to the following link in your browser:"
        print "%s&oauth_token=%s" % (self.access_urls(url)['authorize_url'], request_token['oauth_token'])
        print 

        # After the user has granted access to you, the consumer, the provider will
        # redirect you to whatever URL you have told them to redirect to. You can 
        # usually define this in the oauth_callback argument as well.
        accepted = 'n'
        while accepted.lower() == 'n':
            accepted = raw_input('Have you authorized me? (y/n) ')
    
        # Step 3: Once the consumer has redirected the user back to the oauth_callback
        # URL you can request the access token the user has approved. You use the 
        # request token to sign this request. After this is done you throw away the
        # request token and use the access token returned. You should store this 
        # access token somewhere safe, like a database, for future use.
        token = oauth.Token(request_token['oauth_token'],
        request_token['oauth_token_secret'])
    
        client = oauth.Client(consumer, token)

        resp, content = client.request(self.access_urls(url)['access_token_url'], "POST")
        access_token = dict(urlparse.parse_qsl(content))

        if self.__verbose__:
            print "Access Token:"
            print "    - oauth_token        = %s" % access_token['oauth_token']
            print "    - oauth_token_secret = %s" % access_token['oauth_token_secret']
            print
            print "You may now access protected resources using the access tokens above." 
            print ""

        return (access_token['oauth_token'],access_token['oauth_token_secret'])

    def connect(self,url,consumer_key,consumer_secret,user_token,user_secret):
        self.__url__ = self.tidyUrl(url)

        self.__consumer_key__ = consumer_key
        self.__consumer_secret__ = consumer_secret
        self.__user_token__ = user_token
        self.__user_secret__ = user_secret

        self.__consumer__ = oauth.Consumer(consumer_key, consumer_secret)
        self.__token__ = oauth.Token(user_token,user_secret)
        self.__client__ = oauth.Client(self.__consumer__, self.__token__)
        self.__connected__ = True

    def tidyUrl(self,url):
        # Check the final character of the URL is a '/', and if not add it
        if url[-1] != "/":
            url = url + "/"

        return url

    def access_urls(self,url):
        # Return a dict of URLs to use to access the service:
        request_token_url = url + 'services.php?service=oauth&method=request_token'
        access_token_url = url + 'services.php?service=oauth&method=access_token'
        authorize_url = url + 'index.php?p=oauth&q=authorize'

        return ({'url': url, 'request_token_url': request_token_url, 'access_token_url': access_token_url, 'authorize_url': authorize_url})


    def callMethod(self,methodName,parameters=[],service='rest'):
        # Call the method methodName with parameters
        # Parameters should be a list of tuples as follows:
        #  [('parameterName','parameterValue'),('parameterName2','parameterValue2')]

        if not self.__connected__:
            raise XiboAPIError('Attempted to call the API before it has been initialised')

        url = self.__url__ + "services.php"

        # Setup minimal parameters as a list of tuples
        params = [('method',methodName),('service',service)]
        params.extend(parameters)

        # Sign the request with OAuth and get the response from the server
        try:
            response, content = self.__client__.request(url, method='POST', body=urllib.urlencode(dict(params)))
        except AttributeError:
            raise XiboAPIError('Could not contact the server')
        except:
            raise XiboAPIError('An unspecified error occured')
    
        # Send the content off to be checked for an error status
        if response['status'] == '200':
            status = self.parseError(content)
        else:
            status = ('ERROR',0,'Error 500 in webservice')

        return (response, status[0], status[1], status[2], content)

    def parseID(self,xml,nodeName,attribute='id'):
        # Parse out an id from XML
        # Used for example when adding a layout to get the new layout's ID
        doc = minidom.parseString(xml)

        nodes = doc.getElementsByTagName(nodeName)
        for node in nodes:
            if nodeName == 'region':
                return node.attributes[attribute].value
            else:
                return int(node.attributes[attribute].value)

        raise XiboAPIError('No node/attribute matches your request')

    def parseError(self,xml):
        # Parse out an error from XML
        doc = minidom.parseString(xml)

        nodes = doc.getElementsByTagName('rsp')
        for node in nodes:
            if str(node.attributes['status'].value) == 'error':
                for errNode in doc.getElementsByTagName('error'):
                    code = int(errNode.attributes['code'].value)
                    message = str(errNode.attributes['message'].value)
                    return ('ERROR',code,message)
            else:
                return ('OK',0,'')

        raise XiboAPIError('No node/attribute matches your request')

    def b64encode(self, data):
        # Encode and checksum the data
        data = base64.b64encode(data)
        checksum = hashlib.md5(data).hexdigest()

        return (data, checksum)

    def getConsumerKey(self):
        if not self.__connected__:
            raise XiboAPIError('Attempted to call the APU before it has been initialsed')
        return self.__consumer_key__

    def getConsumerSecret(self):
        if not self.__connected__:
            raise XiboAPIError('Attempted to call the APU before it has been initialsed')
        return self.__consumer_secret__

    def getUserToken(self):
        if not self.__connected__:
            raise XiboAPIError('Attempted to call the APU before it has been initialsed')
        return self.__user_token__

    def getUserSecret(self):
        if not self.__connected__:
            raise XiboAPIError('Attempted to call the APU before it has been initialsed')
        return self.__user_secret__

    def getUrl(self):
        if not self.__connected__:
            raise XiboAPIError('Attempted to call the APU before it has been initialsed')
        return self.__url__

class XiboAPIError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

