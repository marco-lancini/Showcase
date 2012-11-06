from dbindexer.lookups import StandardLookup
from dbindexer.api import register_index
from app_users.models import UserProfile

register_index(UserProfile, {'user__username': StandardLookup(),})
