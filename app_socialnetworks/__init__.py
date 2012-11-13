"""

Module that manage the interaction with a :class:`models.UserProfile` resource

"""

import time, json, urllib, urllib2, urlparse
import httplib, httplib2, oauth2
from datetime import datetime
import hmac, hashlib
import signal
import base64
from uuid import uuid4
import mimetools, mimetypes
import xml.etree.ElementTree as ET
from django.conf import settings
from django.contrib.auth.models import User

def setting(name, default=None):
    """Return setting value for given name or default value."""
    return getattr(settings, name, default)

