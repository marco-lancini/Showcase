from __init__ import *
from oauthclient import *


class FlickrClient(OauthClient):
    """
    Wrapper for Flickr APIs

    :CONSUMER_KEY: Flickr App ID
    :CONSUMER_SECRET: Flickr API Secret
    :photoset: the connected Flickr photoset, if any
    :user_auth: account of the user on Showcase
    :auth: boolean flag (if True, the operation needs to be authenticated)

    .. seealso:: :class:`app_socialnetworks.oauthclient.OauthClient`
    """
    CONSUMER_KEY      = setting('FLICKR_APP_ID')
    CONSUMER_SECRET   = setting('FLICKR_API_SECRET')
    
    def __init__(self, photoset, user_auth=False, auth=False):
        """
        Insantiate the client: if authentication is needed, proceed with Oauth; otherwise, use a simple HTTP client

        :param photoset: the connected Flickr photoset, if any
        :type photoset: string
        :param user_auth: account of the user on Showcase
        :type user_auth: `User`
        :param auth: flag (if True, the operation needs to be authenticated)
        :type auth: boolean
        """
        self.photoset  = photoset
        self.user_auth = user_auth
        self.auth      = auth

        if self.auth:
            # Authentication needed, proceed with Oauth
            super(FlickrClient, self).__init__(self.CONSUMER_KEY, self.CONSUMER_SECRET)
        else:
            # Use a simple HTTP client
            self.client = httplib2.Http()


    def request_token(self, consumer):
        """
        Retrieve the access token of the user from his connected accounts data
        """
        # Retrieve connected accounts
        connected_accounts = self.user_auth.social_auth.filter(user=self.user_auth.id).filter(provider="flickr")
        if len(connected_accounts) == 0:
            raise NotConnectedException('Not Connected to Flickr')

        # Retrieve access_token from socialauth
        access_token       = connected_accounts[0].extra_data['access_token']
        access_token       = urlparse.parse_qs(access_token)
        oauth_token        = access_token['oauth_token'][0]
        oauth_token_secret = access_token['oauth_token_secret'][0]

        return oauth_token, oauth_token_secret        



    #=========================================================================
    # READ
    #=========================================================================
    def _query_read(self, method, query, limit=5, optionals=None):
        """
        Execute a read-only query
        """
        url = "http://api.flickr.com/services/rest/?method=%s&api_key=%s&%s&per_page=%s&format=json&nojsoncallback=1" % (method, self.CONSUMER_KEY, query, limit)
        if optionals:
            url += optionals

        try:
            resp, content = self.client.request(url, "GET")
            content = json.loads(content)
            return content
        except:
            return None


    def get_photolist(self, limit):
        """
        Get a list of photos contained in the photoset

        :param limit: max number of photos to retrieve
        :type limit: int
        """
        method    = 'flickr.photosets.getPhotos'
        query     = 'photoset_id=%s' % self.photoset

        photolist = self._query_read(method, query, limit)
        try:
            return photolist['photoset']['photo']
        except:
            return None


    def get_photo(self, photo):
        """
        Get url of a specific photo

        :param photo: Flickr photo
        :type: object
        """
        pid    = photo['id']
        method = 'flickr.photos.getSizes'
        query  = 'photo_id=%s' % pid

        photo_data  = self._query_read(method, query)
        if photo_data:
            photo_sizes = photo_data['sizes']['size']
            medium      = filter(lambda x: x['label'] == 'Medium', photo_sizes)

            if len(medium) == 0:
                medium = photo_sizes

            return medium[0]
        else:
            return None


    #=========================================================================
    # WRITE
    #=========================================================================
    def _post_photo(self, upload_api_url, title, description, photo):
        """
        Post a photo to Flickr via API
        """
        photo_name = str(photo)
        photo_file = photo.read()
        files = [("photo", photo_name, photo_file)]

        params = {
            'oauth_version': "1.0",
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': int(time.time()),
            'oauth_token': self.oauth_token,
            'oauth_consumer_key': self.CONSUMER_KEY,
            'title': title,
            'description': description
        }

        # Create a fake request with your upload url and parameters
        faux_req = oauth2.Request(method='POST', url=upload_api_url, parameters=params)

        # Sign the fake request
        signature_method = oauth2.SignatureMethod_HMAC_SHA1()
        faux_req.sign_request(signature_method, self.consumer, self.token)

        #create a dict out of the fake request signed params
        params = dict(urlparse.parse_qsl(faux_req.to_postdata()))

        content_type, body = self.encode_multipart_formdata(params, files)
        headers = {'Content-Type': content_type, 'Content-Length': str(len(body))}
        r = urllib2.Request('%s' % upload_api_url, body, headers)

        response = urllib2.urlopen(r).read()
        return response


    def upload_photo(self, title, description, photo):
        """
        Upload a photo to Flickr

        :param title: title of the photo
        :type title: string
        :param description: description of the photo
        :type description: string
        :param photo: photo to upload
        :type photo: image file
        """
        upload_api_url = 'http://api.flickr.com/services/upload/'
        response       = self._post_photo(upload_api_url, title, description, photo)
        
        # Parse Flick Response
        tree = ET.fromstring(response)

        # Check response status
        status = tree.attrib
        if status['stat'] != 'ok':
            raise UploadException("Error During Upload: %s" % response)

        # Extract new photo id
        for child in tree:
            if child.tag == 'photoid':
                pid = child.text
                break

        return pid


    def add_photo_to_photoset(self, pid):
        """
        After uploading a photo to Flickr, add it to the photoset

        :param pid: pid of the newly uploaded photo
        :type pid: string
        """
        method = 'flickr.photosets.addPhoto'
        query  = 'photoset_id=%s&photo_id=%s' % (self.photoset, pid)
        url    = "http://api.flickr.com/services/rest/?method=%s&api_key=%s&%s&format=json&nojsoncallback=1" % (method, self.CONSUMER_KEY, query)

        resp, content = self.client.request(url, "POST")
        content = json.loads(content)

        if content['stat'] != 'ok':
            if content['message'] == 'Photoset not found':
                raise ClearanceException("Photoset not found")
            else:
                raise UploadException("Error During Add Photo To Photoset: %s" % content)

    