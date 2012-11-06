from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.messages.api import get_messages

from django.contrib.auth.views import login as base_login
from django.contrib.auth import logout as base_logout
from django.contrib.auth.models import User

from social_auth import __version__ as version
from social_auth.utils import setting

from app_users.models import UserProfile


#=========================================================================
# HOME
#=========================================================================
def home(request):
    """
    Render the homepage

    :Rest Types: ``GET``
    :URL: ``/``
    """
    ctx = {}
    return render_to_response('home.html', ctx, RequestContext(request))


#=========================================================================
# CUSTOM LOGIN
#=========================================================================
def login(request):
    """
    Login the user and redirect him to the homepage

    :Rest Types: ``GET``
    :URL: ``login/``
    """
    if request.user.is_active:
        return HttpResponseRedirect('/')
    else:
        return base_login(request)

def logout(request):
    """
    Logout the user and redirect him to the homepage

    :Rest Types: ``GET``
    :URL: ``logout/``    
    """
    base_logout(request)
    return HttpResponseRedirect('/')



#=========================================================================
# SOCIAL LOGIN
#=========================================================================
def login_error(request):
    """
    Return an error page for errors during login
    
    :Rest Types: ``GET``
    :URL: ``login/error/``
    """
    messages = get_messages(request)
    return render_to_response('app_auth/error.html', {'messages': messages}, RequestContext(request))


def associate(request, backend):
    """
    Associate an account to a Social Network account
    
    :param backend: the name of social network to connect
    
    :Rest Types: ``GET``
    :URL: ``associate/(?P<backend>[^/]+)/``
    """
    try:        
        return HttpResponseRedirect('/login/' + str(backend) + '/')
    except:
        return render_to_response('app_auth/error.html', {'messages': 'This %s account is already in use' % backend}, RequestContext(request))



def ask_username(request,params=None):
    """
    When creating a new user through a social login, ask the username to user
    
    :Rest Types: ``GET``
    :URL: ``ask_username/``
    """
    if request.method == 'POST' and request.POST.get('username'):
        # Check that the username is not already taken
        username = request.POST.get('username')
        cont = UserProfile.objects.filter(user__username=username).count()
        if cont > 0:
            return render_to_response('app_auth/ask_username.html', {'social_errors': 'Username already taken'}, RequestContext(request))
        
        # Continue with the pipeline
        name = setting('SOCIAL_AUTH_PARTIAL_PIPELINE_KEY', 'partial_pipeline')
        request.session['saved_username'] = request.POST['username']
        backend = request.session[name]['backend']
        return redirect('socialauth_complete', backend=backend)
    return render_to_response('app_auth/ask_username.html', {}, RequestContext(request))


def ask_email(request,params=None):
    """
    When creating a new user through a social login, ask the email to user
    
    :Rest Types: ``GET``
    :URL: ``ask_email/``
    """
    if request.method == 'POST' and request.POST.get('email'):
        name = setting('SOCIAL_AUTH_PARTIAL_PIPELINE_KEY', 'partial_pipeline')
        request.session['saved_email'] = request.POST['email']
        backend = 'facebook'
        return redirect('socialauth_complete', backend=backend)
    return render_to_response('app_auth/ask_email.html', {}, RequestContext(request))


#=========================================================================
# PASSWORD MANAGEMENT
#=========================================================================
def password_change_done(request):
    """
    Confirm a change of password

    :Rest Types: ``GET``
    :URL: ``password/change/done/``
    """
    return HttpResponseRedirect('/users/' + str(request.user) + '/settings/')
