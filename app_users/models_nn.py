from django.db import models
from app_collaborations.options import CREATIVE_FIELDS, get_creative_field_verbose


class CreativeFields(models.Model):
    """
    Model for a many-to-many relationship between 
    users (:class:`app_users.models.UserProfile`) and `CreativeFields`

    :userprofile: the user of interest
    :creative_field: creative field associated to the user
    """
    userprofile    = models.ForeignKey('app_users.UserProfile')
    creative_field = models.CharField(max_length=3, choices=CREATIVE_FIELDS, blank=False)

    def get_creative_field(self):
        """
        Return a string representation of the creative field
        """
        return get_creative_field_verbose(self.creative_field)

    def wrapper(self):
        """
        Return a wrapper for a `CreativeFields` object, ie a dictionary containing the wrappers of the involved objects
        """
        wrapper = {}
        wrapper['userprofile']    = self.userprofile.wrapper()
        wrapper['creative_field'] = self.get_creative_field()
        return wrapper
