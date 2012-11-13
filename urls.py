from django.conf.urls.defaults import *


# Search for "dbindexes.py" in all installed apps
import dbindexer
dbindexer.autodiscover()




    



urlpatterns = patterns('',
    ('^_ah/warmup$', 'djangoappengine.views.warmup'),

    # Auth & Homepage
    url(r'', include('app_auth.urls')),

    # Collaborations
    url(r'', include('app_collaborations.urls')),

    # Hints
    url(r'', include('app_hints.urls')),

    # Projects
    url(r'', include('app_projects.urls')),

    # Users
    url(r'', include('app_users.urls')),

    # Serve static content
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'static'}),



    # Docs
    (r'^docs/', 'django.views.generic.simple.direct_to_template', {'template': 'docs/_build/html/index.html'}),
)






#     #=========================================================================

     


# Serve MEDIA
# http://www.muhuk.com/2009/05/25/serving-static-media-in-django-development-server.html
# import settings
# from django.views.static import serve
# _media_url = settings.MEDIA_URL
# _media_url = _media_url[1:]
# urlpatterns += patterns('',
#     (r'^%s(?P<path>.*)$' % _media_url, serve, {'document_root': settings.MEDIA_ROOT}))
# del(_media_url, serve)
