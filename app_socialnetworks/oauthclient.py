from __init__ import *

class NotConnectedException(Exception):
    pass
    
class UploadException(Exception):    
    pass

class ClearanceException(Exception):
    pass



class OauthClient(object):
    
    def __init__(self, CONSUMER_KEY, CONSUMER_SECRET):
        # Use your API key and secret to instantiate consumer object
        consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)

        # Retrieve access_token
        oauth_token, oauth_token_secret = self.request_token(consumer)
        
        # Instantiate access token object
        token = oauth2.Token(key=oauth_token, secret=oauth_token_secret)

        # Instantiate the client
        client = oauth2.Client(consumer, token)

        # Save fields
        self.consumer = consumer
        self.token    = token
        self.client   = client

        self.oauth_token        = oauth_token
        self.oauth_token_secret = oauth_token_secret
        


    #=========================================================================
    # MEDIA IN BODY
    #=========================================================================
    def encode_multipart_formdata(self, fields, files):
        """
            Prepare a POST message to upload media content in the body of the message

            Used by Flickr
        """        
        BOUNDARY = mimetools.choose_boundary()
        CRLF = '\r\n'
        L = []
        for (key, value) in fields.items():
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(value)

        for (key, filename, value) in files:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
            L.append('Content-Type: %s' % mimetypes.guess_type(filename)[0] or 'application/octet-stream')
            L.append('')
            L.append(value)
        L.append('--' + BOUNDARY + '--')
        L.append('')

        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        return content_type, body


    #=========================================================================
    # MEDIA IN URL
    #=========================================================================
    def oauth_sig(self,method,uri,params):
        """
        Creates the valid OAuth signature
        """
        s = method + '&'+ urllib.quote(uri).replace('/','%2F')+ '&' + '%26'.join(
            [urllib.quote(k) +'%3D'+ urllib.quote(params[k]).replace('/','%2F') for k in sorted(params.keys())]
        )
        s = s.replace('%257E','~')
        return urllib.quote(base64.encodestring(hmac.new(self.CONSUMER_SECRET + "&"+self.oauth_token_secret,s,hashlib.sha1).digest()).strip())


    def oauth_gen(self,method,url,iparams,headers):
        """
        Creates the oauth parameters we're going to need to sign the body
        """
        params = dict([(x[0], urllib.quote(str(x[1])).replace('/','%2F')) for x in iparams.iteritems()]) 
        params['oauth_consumer_key'] = self.CONSUMER_KEY
        params['oauth_nonce'] = str(time.time())[::-1]
        params['oauth_signature_method'] = 'HMAC-SHA1'
        params['oauth_timestamp'] = str(int(time.time()))
        params['oauth_version'] = '1.0'
        params['oauth_token']= self.oauth_token
        params['oauth_signature'] = self.oauth_sig(method,'http://'+headers['Host'] + url, params)
        headers['Authorization' ] =  'OAuth ' + ',  '.join(['%s="%s"' %(k,v) for k,v in params.iteritems() if 'oauth' in k ])


    def _postOAuth(self,url,params={}):
        """
        Does the actual posting. Content-type is set as x-www-form-urlencoded
        Everything url-encoded and data is sent through the body of the request.
        """
        p = urlparse.urlparse(url)
        (machine,host,uri) = (p.netloc, p.netloc, p.path) 

        headers= {'Host': host, "Content-type": 'application/x-www-form-urlencoded'}
        self.oauth_gen('POST', uri, params, headers)
        conn = httplib.HTTPConnection(machine)
        conn.request('POST', uri, urllib.urlencode(params).replace('/','%2F'), headers)
        return conn.getresponse()    
