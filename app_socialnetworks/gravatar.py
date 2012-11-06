from __init__ import *
from oauthclient import *

from django.conf import settings

class GravatarClient(OauthClient):

    CONSUMER_KEY      = setting('FLICKR_APP_ID')
    CONSUMER_SECRET   = setting('FLICKR_API_SECRET')
    
    def __init__(self, email):
        self.email = email


    def get_gravatar_url(self):
        # Set your variables
        email   = self.email
        size    = 200
        default = "mm"  # mistery man

        # Construct the url
        gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
        gravatar_url += urllib.urlencode({'d':default, 's':str(size)})

        return gravatar_url
