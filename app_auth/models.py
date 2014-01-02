from django.db import models
from social_auth.signals import pre_update
from social_auth.backends.facebook import FacebookBackend


class CustomUserManager(models.Manager):
    """
    Manager for the :class:`CustomUser`
    """
    def create_user(self, username, email):
        """
        Retrieve the username and create the user

        :param username: the username chosen by the user
        :type username: str
        :param email: email of the user (unused)
        :type email: str 
        """
        return self.model._default_manager.create(username=username)


class CustomUser(models.Model):
    """
    Temporary resource used only during the process of social authentication

    :username: username chosen by the user
    :email: email chosen by the user
    :last_login: last time the user was logged
    """
    username   = models.CharField(max_length=128)
    email      = models.EmailField()
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    def is_authenticated(self):
        """
        Check if the user is authenticated

        :returns: True if the user is authenticated
        """
        return True

    def __unicode__(self):
        """
        String representation of the user
        
        :returns: the username chosen
        """
        return self.username


def facebook_extra_values(sender, user, response, details, **kwargs):
	return False

pre_update.connect(facebook_extra_values, sender=FacebookBackend)