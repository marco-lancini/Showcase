from django.db import models

class Votes(models.Model):
    """
    Model for a `Vote`, a many-to-many relationship between 
    projects (:class:`app_projects.models.Project`) and users (:class:`app_users.models.UserProfile`)

    :project: the project of interest
    :users: the users that have voted the project
    """
    project = models.ForeignKey('app_projects.Project')
    user    = models.ForeignKey('app_users.UserProfile')



class Collaborations(models.Model):
    """
    Model for a `Collaboration`, a many-to-many relationship between 
    projects (:class:`app_projects.models.Project`) and users (:class:`app_users.models.UserProfile`)

    :project: the project of interest
    :userprofile: the users that collaborates to the project
    :date_joined: date in which the collaborator joined the project
    """
    userprofile = models.ForeignKey('app_users.UserProfile')
    project     = models.ForeignKey('app_projects.Project')
    date_joined = models.DateField(auto_now=True,auto_now_add=True, help_text='Please use the following format: YYYY-MM-DD')

    def wrapper(self):
        """
        Return a wrapper for a `Collaborations` object, i.e. a dictionary containing the wrappers of the involved objects
        """
        wrapper = {}
        wrapper['userprofile'] = self.userprofile.wrapper()
        wrapper['project']     = self.project.wrapper()
        wrapper['date_joined'] = self.date_joined
        return wrapper
