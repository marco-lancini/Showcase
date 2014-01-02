from __init__ import *
from oauthclient import *


class TumblrClient(OauthClient):
    """
    Wrapper for Tumblr APIs

    :CONSUMER_KEY: Tumblr App ID
    :CONSUMER_SECRET: Tumblr API Secret
    :blog: the connected Tumblr blog, if any
    :user_auth: account of the user on Showcase
    :auth: boolean flag (if True, the operation needs to be authenticated)

    .. seealso:: :class:`app_socialnetworks.oauthclient.OauthClient`
    """
    CONSUMER_KEY      = setting('TUMBLR_CONSUMER_KEY')
    CONSUMER_SECRET   = setting('TUMBLR_CONSUMER_SECRET')

    request_token_url = 'http://www.tumblr.com/oauth/request_token'
    authorize_url     = 'http://www.tumblr.com/oauth/authorize'
    access_token_url  = 'http://www.tumblr.com/oauth/access_token'
    
    def __init__(self, blog, user_auth=False, auth=False):
        """
        Insantiate the client: if authentication is needed, proceed with Oauth; otherwise, use a simple HTTP client

        :param blog: the connected Tumblr blog, if any
        :type blog: string
        :param user_auth: account of the user on Showcase
        :type user_auth: `User`
        :param auth: flag (if True, the operation needs to be authenticated)
        :type auth: boolean
        """
        self.blog      = blog
        self.user_auth = user_auth
        self.auth      = auth

        if self.auth:
            # Authentication needed, proceed with Oauth
            super(TumblrClient, self).__init__(self.CONSUMER_KEY, self.CONSUMER_SECRET)
        else:
            # Use a simple HTTP client
            self.client = httplib2.Http()


    def request_token(self, consumer):
        """
        Retrieve the access token of the user from his connected accounts data
        """
        # Retrieve connected accounts
        connected_accounts = self.user_auth.social_auth.filter(user=self.user_auth.id).filter(provider="tumblr")
        if len(connected_accounts) == 0:
            raise NotConnectedException('Not Connected to Tumblr')

        # Retrieve access_token from socialauth
        access_token       = connected_accounts[0].extra_data['access_token']
        access_token       = urlparse.parse_qs(access_token)
        oauth_token        = access_token['oauth_token'][0]
        oauth_token_secret = access_token['oauth_token_secret'][0]

        return oauth_token, oauth_token_secret        




    #=========================================================================
    # READ
    #=========================================================================
    def _query(self, method, optionals=None):
        """
        Execute a read-only query
        """
        url = "http://api.tumblr.com/v2/blog/%s.tumblr.com/%s?api_key=%s" % (self.blog, method, self.CONSUMER_KEY)
        if optionals:
            url += optionals

        try:
            resp, content = self.client.request(url, "GET")
            content = json.loads(content)['response']
            return content
        except:
            return None


    def get_blog_info(self):
        """
        Get general infos about the connected blog
        """
        method = "info"
        return self._query(method)    


    def get_blog_posts(self):
        """
        Fetch last 5 blog posts
        """
        method    = "posts"
        optionals = "&limit=5"
        
        posts = self._query(method, optionals)
        if posts:
            posts = posts['posts']
            for p in posts:
                temp  = datetime.strptime(p['date'], "%Y-%m-%d %H:%M:%S GMT")
                p['date'] = temp.strftime("%d %B %Y")

            return posts
        else:
            return None




    #=========================================================================
    # WRITE
    #=========================================================================
    def _post_blog(self, params, media=None):
        """
        Execute a write query
        """
        url = 'http://api.tumblr.com/v2/blog/%s.tumblr.com/post' % self.blog

        if media:
            content = self._postOAuth(url, params)
            content = content.read()
        else:
            body = urllib.urlencode(params)
            resp, content = self.client.request(url, "POST", body=body)

        # Check response
        content  = json.loads(content)
        response = content['meta']['msg']

        if response:
            if response != 'Created':
                if response == 'Not Authorized':
                    raise ClearanceException("Not an owned blog")
                else:
                    raise UploadException("Error During Upload: %s" % response)
        else:
            raise UploadException("Error During Upload: %s" % response)


    def add_text(self, title, body):    
        """
        Add a blog of type: *text*

        :param title: title of the blog post
        :type title: string
        :param body: content of the blog post
        :type body: string
        """
        params = {'type': 'text', 'title': title, 'body': body}
        return self._post_blog(params)


    def add_link(self, title, url):
        """
        Add a blog of type: *link*

        :param title: title of the blog post
        :type title: string
        :param url: url of the link to publish
        :type url: string
        """
        params = {'type': 'link', 'title': title, 'url': url}
        return self._post_blog(params)


    def add_quote(self, quote):  
        """ 
        Add a blog of type: *quote*

        :param quote: quote to publish
        :type quote: string
        """  
        params = {'type': 'quote', 'quote': quote}
        return self._post_blog(params)


    def add_chat(self, title, conversation):
        """
        Add a blog of type: *chat*

        :param title: title of the blog post
        :type title: string
        :param conversation: conversation to publish
        :type conversation: string
        """
        params = {'type': 'chat', 'title': title, 'conversation': conversation}
        return self._post_blog(params)


    def add_photo(self, source, photo):
        """
        Add a blog of type: *photo*

        :param source: url of the photo to publish, if any
        :type source: string
        :param photo: photo to upload, if any
        :type photo: image file
        """
        if source:
            params = {'type': 'photo', 'source': source}
            return self._post_blog(params)

        elif photo:
            params = {'type': 'photo', 'data[0]': photo.read()}
            return self._post_blog(params, media=True)


    def add_audio(self, source):
        """
        Add a blog of type: *audio*

        :param source: url of the audio file to publish
        :type source: string
        """
        if source:
            params = {'type': 'audio', 'external_url': source}
            return self._post_blog(params)


    # def add_video(self, video):
    #     params     = {'type': 'video', 'data[0]': video.read()}
    #     return self._post_blog(params, media=True)
