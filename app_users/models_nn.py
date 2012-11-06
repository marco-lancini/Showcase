from django.db import models
from app_collaborations.options import CREATIVE_FIELDS


class CreativeFields(models.Model):
    ''' Realize the n-to-n relation between UserProfile and CreativeFields '''

    userprofile    = models.ForeignKey('app_users.UserProfile')
    creative_field = models.CharField(max_length=3, choices=CREATIVE_FIELDS, blank=False)


    def _get_display(self, key, list):
        d = dict(list)
        if key in d:
            return d[key]
        return None

    def get_creative_field(self):
        return self._get_display(self.creative_field, CREATIVE_FIELDS)    


    def wrapper(self):
        wrapper = {}
        wrapper['userprofile']    = self.userprofile.wrapper()
        wrapper['creative_field'] = self.get_creative_field()
        return wrapper
