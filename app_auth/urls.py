from django.conf.urls.defaults import *
from django.contrib.auth import views as auth_views
from app_auth.views import *
from app_auth.views import login as custom_login, logout as custom_logout

urlpatterns = patterns('',  
    # Home
    url(r'^$', home, name="app_auth.home"), 

    # Login / logout
    url(r'^login/$',  custom_login,  name="app_auth.login"),
    url(r'^logout/$', custom_logout, name="app_auth.logout"),

    # Password Management
    url(r'^password/change/$', auth_views.password_change, 
        {'template_name': 'registration/password_change_form.html'}, name='app_auth.password_change'),
    url(r'^password/change/done/$', password_change_done, name='app_auth.password_change_done'),

    # Social Auth
    url(r'^ask_username/$', ask_username, name='app_auth.ask_username'),
    url(r'^ask_email/$', ask_email, name='app_auth.ask_email'),
    url(r'^error/$', login_error, name='app_auth.error'),
    url(r'^login/error/$', login_error, name='app_auth.error'),
    url(r'^associate/(?P<backend>[^/]+)/$', associate, name='app_auth.associate'),

    #=========================================================================
    # Registration links
    (r'^accounts/', include('registration.urls')),

    # Social login
    (r'', include('social_auth.urls')),

    # Default django login module 
    (r'', include('registration.auth_urls')),
)


# Password Reset
# url(r'^password/reset/$', password_reset, {'template_name': 'registration/password_reset_form.html'}, name='auth_password_reset'),
# url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm, {'template_name': 'registration/password_reset_confirm.html'}),
# url(r'^password/reset/complete/$', password_reset_complete, {'template_name': 'registration/password_reset_complete.html'}),
# url(r'^password/reset/done/$', password_reset_done, {'template_name': 'registration/password_reset_done.html'})
