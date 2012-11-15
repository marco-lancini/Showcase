from __init__ import *
from oauthclient import *

class GravatarClient(OauthClient):
    """
    Wrapper for Gravatar APIs

    :email: email of the user

    .. seealso:: :class:`app_socialnetworks.oauthclient.OauthClient`
    """
    
    def __init__(self, email):
        self.email = email


    def get_gravatar_url(self):
        """
        Retrieve the gravatar associated to the user email
        """
        email   = self.email
        size    = 200
        default = "mm"  # mistery man

        # Construct the url
        gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
        gravatar_url += urllib.urlencode({'d':default, 's':str(size)})

        return gravatar_url
