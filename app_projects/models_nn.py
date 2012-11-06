from django.db import models

class Votes(models.Model):

    project = models.ForeignKey('app_projects.Project')
    user    = models.ForeignKey('app_users.UserProfile')



class Collaborations(models.Model):
    ''' Realize the n-to-n relation between UserProfile and Project '''

    userprofile = models.ForeignKey('app_users.UserProfile')
    project     = models.ForeignKey('app_projects.Project')
    date_joined = models.DateField(auto_now=True,auto_now_add=True, help_text='Please use the following format: YYYY-MM-DD')


    def wrapper(self):
        wrapper = {}
        wrapper['userprofile'] = self.userprofile.wrapper()
        wrapper['project']     = self.project.wrapper()
        wrapper['date_joined'] = self.date_joined
        return wrapper

