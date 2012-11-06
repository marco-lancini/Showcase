from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from app_users.models import UserProfile

#=========================================================================
# INTERCEPT CONNECTION WITH ALREADY CONNECTED ACCOUNTS
#=========================================================================
# from django.core.urlresolvers import reverse
# from social_auth.backends.exceptions import AuthAlreadyAssociated
# from social_auth.middleware import SocialAuthExceptionMiddleware


# class ExampleSocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
#     def get_message(self, request, exception):
#         if isinstance(exception, AuthAlreadyAssociated):
#             return "Somebody is already using that account!"
#         return "We got some splainin' to do!"

#     def get_redirect_uri(self, request, exception):
#         return reverse('done')



#=========================================================================
# ASK USERNAME
#=========================================================================
def redirect_to_ask_username(*args, **kwargs):
    """
    If there isn't a user in session, then redirect to :func:`views.ask_username`
    """
    if not kwargs['request'].session.get('saved_username') and kwargs.get('user') is None:
        return HttpResponseRedirect('/ask_username/')
	

def username(request, *args, **kwargs):
    """
    Retrieve the username chosen by the user
    """
    if kwargs.get('user'):
        username = kwargs['user'].username
    else:
        username = request.session.get('saved_username')
    return {'username': username}


#=========================================================================
# ASK EMAIL
#=========================================================================
def redirect_to_ask_email(*args, **kwargs):
    """
    If there isn't a saved email in session, check if the active user has an email.
    If not, then redirect him to :func:`views.ask_email`
    """
    if not kwargs['request'].session.get('saved_email'):
        try:
            u = User.objects.get(username__iexact=kwargs['user'].username)
            if u.email and u.email != "":
                return
        except:
            pass
        return HttpResponseRedirect('/ask_email/')


def email(request, *args, **kwargs):
    """
    Retrieve the email chosen by the user and update the corresponding :func:`auth.User`
    """
    if 'saved_email' in request.session:
        u = User.objects.get(username__iexact=kwargs['user'].username)
        u.email = request.session.get('saved_email')
        u.save()



#=========================================================================
# UPDATE NAME
#=========================================================================
def update_name(*args, **kwargs):
    """
    At the end of the pipeline, check if the connected account has defined a name.
    If yes, copy it into the corresponding :class:`app_users.models.UserProfile`
    """
    if kwargs.get('user'):
        temp = kwargs['user']
        
        u = UserProfile.objects.get(user__username__iexact=temp.username)

        u.first_name = temp.first_name
        u.last_name = temp.last_name
        u.save()
