from django.db import models
from django.db.models.signals import post_save
from django.forms.models import model_to_dict
from settings import BASE_URL

from social_auth.models import Association
from django.contrib.auth.models import User
from app_projects.models_nn import Votes, Collaborations
from app_users.countries import *
from app_users.models_nn import CreativeFields
from app_socialnetworks.linkedin import LinkedInClient
from app_socialnetworks.gravatar import GravatarClient
from app_socialnetworks.oauthclient import NotConnectedException


#=========================================================================
# EMPLOYMENT
#=========================================================================
class Employment(models.Model):
    """
    Model for `Employment` objects, that contains informations about the current employment history of the user

    :headline: short description
    :industry: industry of specialization
    :company: actual employer
    :title: position in the company
    """
    headline = models.CharField(max_length=100, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    company  = models.CharField("Company", max_length=100, blank=True, null=True)
    title    = models.CharField("Title", max_length=100, blank=True, null=True)
    
    def wrapper(self):
        """
        Return a wrapper for an `Employment` object, ie a dictionary containing all the data
        """
        wrapper = model_to_dict(self)
        del wrapper['id']

        return wrapper



#=========================================================================
# USERPROFILE
#=========================================================================
class UserProfile(models.Model):
    """
    Model for a `UserProfile`, one of the main resources

    :user: :class:`django.contrib.auth.models.User`
    :first_name: first name
    :last_name: last name 
    :sex: sex (m,f)
    :birthday: birthday
    :website: personal website
    :phone: telephone number
    :country: nationality
    :address: address
    :availability: availability (Full-Time, Part-Time, Consulting, Freelance, Internship)
    :fee: boolean that state if the user is available to work for free
    :bio: short biography
    :employment: :class:`app_users.models.Employment`
    """
    # Bound to an auth.models.User
    user = models.OneToOneField(User)

    # Other fields
    first_name    = models.CharField(max_length=100, blank=True)
    last_name     = models.CharField(max_length=100, blank=True)
    sex           = models.CharField(choices=GENDER, max_length=2, blank=True)
    birthday      = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True, 
                                     help_text='Please use the following format: YYYY-MM-DD')
    website       = models.URLField("Website", blank=True)
    phone         = models.CharField(max_length=20, blank=True)
    country       = CountryField()
    address       = models.TextField(blank=True)
    availability  = models.CharField(choices=AVAILABILITY, max_length=2, blank=True)
    fee           = models.NullBooleanField(help_text="Are you avaiable to work for free?")
    bio           = models.TextField(max_length=200, blank=True, help_text='Max. 200 characters')
    
    # PROFILE PIC
    #profile_pic = models.FileField(storage=mfs, upload_to='profile_pics/', blank=True)

    # Employment
    employment = models.ForeignKey(Employment, null=True)
    

    #=========================================================================
    # HELPERS
    #=========================================================================    
    def __unicode__(self):
        """
        Unicode representation of the user, as its username
        """
        return self.user.username

    @property
    def full_name(self):
        """
        Return the full name of the user (first_name + last_name)
        """
        if (self.first_name == None and self.last_name == None) or (self.first_name == "" and self.last_name == ""):
            return None
        return '%s %s' % (self.first_name, self.last_name)
    
    def create_user_profile(sender, instance, created, **kwargs):
        """
        Create an `UserProfile` instance when creating a `User`
        """
        if created:
            UserProfile.objects.create(user=instance)
    post_save.connect(create_user_profile, sender=User)


    #=========================================================================
    # ACCOUNTS
    #=========================================================================
    def get_user_auth_wrapper(self):
        """
        Return a wrapper for the :class:`django.contrib.auth.models.User` connected to the `UserProfile`, 
        avoiding that sensitive informations can be exposed to clients
        """
        user_auth = {'username':self.user.username, 'email': self.user.email, 'last_login': self.user.last_login, 'date_joined': self.user.date_joined}
        return user_auth


    def get_connected_accounts(self):
        """
        Return a dictionary containing 2 lists

            - one list of connected accounts (provider, url)
            - one list of only names of the actually connected accounts
        """
        connected_accounts_set = self.user.social_auth.filter(user=self.user.id)
        connected_accounts     = []
        connected_names        = []

        for ca in connected_accounts_set:
            if ca.provider == 'twitter':
                ca_url = "https://twitter.com/account/redirect_by_id?id=%s" % ca.extra_data['id']
                connected_accounts.append({'provider':ca.provider, 'url':ca_url})

            elif ca.provider == 'facebook':
                ca_url = "https://facebook.com/profile.php?id=%s" % ca.extra_data['id']
                connected_accounts.append({'provider':ca.provider, 'url':ca_url})

            elif ca.provider == 'linkedin':
                l = LinkedInClient(self.user)
                ca_url = "http://www.linkedin.com/x/profile/%s/%s" % (l.get_consumer_key(), ca.extra_data['id'])
                connected_accounts.append({'provider':ca.provider, 'url':ca_url})

            elif ca.provider == 'flickr':
                ca_url = "http://www.flickr.com/people/%s" % ca.extra_data['id']
                connected_accounts.append({'provider':ca.provider, 'url':ca_url})

            elif ca.provider == 'tumblr':
                ca_url = "http://%s.tumblr.com" % ca.uid
                connected_accounts.append({'provider':ca.provider, 'url':ca_url})

            else:
                pass
            
            connected_names.append(ca.provider)

        return {'list': connected_accounts, 'names': connected_names}


    def delete_connected_accounts(self):
        """
        Delete all the connected accounts
        """
        connected_accounts_set = self.user.social_auth.filter(user=self.user.id)
        if connected_accounts_set.count() == 0:
            return

        for ca in connected_accounts_set:
            associations_set = Association.objects.filter(id=ca.id)
            for ass in associations_set:
                ass.delete()
                
            ca.delete()


    #=========================================================================
    # PROJECTS
    #=========================================================================
    def get_projects_own(self):
        """
        Return all the projects onwned by the user
        """
        return self.projects_own.all()

    def get_projects_own_wrapper(self):
        """
        Return the wrappers of all the projects onwned by the user
        """
        projects_own = self.get_projects_own()
        return [x.wrapper() for x in projects_own]

    def get_projects_collaborate(self):
        """
        Return all the projects in which the user collaborate
        """
        projects_collaborate_set = Collaborations.objects.filter(userprofile=self)
        projects_collaborate     = [x.project for x in projects_collaborate_set]
        return projects_collaborate

    def get_projects_collaborate_wrapper(self):
        """
        Return the wrappers of all the projects in which the user collaborate
        """
        projects_collaborate = self.get_projects_collaborate()
        return [x.wrapper() for x in projects_collaborate]

    def get_projects_voted(self):
        """
        Return all the projects voted by the user
        """
        votes = Votes.objects.filter(user=self)
        return [x.project for x in votes]

    def get_projects_voted_wrapper(self):
        """
        Return the wrappers of all the projects voted by the user
        """
        votes = Votes.objects.filter(user=self)
        return [x.wrapper() for x in votes]


    #=========================================================================
    # CONNECTED DATA
    #=========================================================================
    def get_profile_pic(self):
        """
        Return the URL of the Gravatar profile picture
        """
        g = GravatarClient(self.user.email)
        return g.get_gravatar_url()


    def delete_connected_data(self):
        """
        Delete **all** connected data

            - connected accounts
            - creative fields
            - employment data
        """
        # Disconnect all connected accounts
        self.delete_connected_accounts()

        # Delete Creative Fields
        self.delete_creative_fields()

        # Delete Employment
        self.delete_employment()

        # Delete AuthUser
        self.user.delete()


    #=========================================================================
    # LINKEDIN
    #=========================================================================
    def get_linkedin_employment(self):
        """
        Fetch employment data from LinkedIn
        """
        if 'linkedin' not in self.get_connected_accounts()['names']:
            raise NotConnectedException("Not Connected to LinkedIn")

        li = LinkedInClient(self.user)
        employment_data = li.get_employment_data()

        new_employment = Employment(headline=employment_data['headline'],
                                    industry=employment_data['industry'],
                                    company=employment_data['company'],
                                    title=employment_data['title'])
        new_employment.save()
        self.employment = new_employment
        self.save()

    def get_linkedin_skills(self):
        """
        Fetch skills from LinkedIn
        """
        if 'linkedin' not in self.get_connected_accounts()['names']:
            return None
        
        li = LinkedInClient(self.user)
        linkedin = li.skills()

        return linkedin


    #=========================================================================
    # EMPLOYMENT
    #=========================================================================
    def get_employment(self):
        """
        Return employment data
        """
        return self.employment

    def get_employment_wrapper(self):        
        """
        Return wrapper of employment data
        """
        if self.employment:
            return self.employment.wrapper()
        else:
            return None

    def delete_employment(self):
        """
        Delete the connected employment data
        """
        if self.employment:
            self.employment.delete()


    #=========================================================================
    # CREATIVE FIELDS
    #=========================================================================
    def get_creative_fields(self):
        """
        Return the list of all the creative fields of the user
        """
        fields_set      = CreativeFields.objects.filter(userprofile=self)
        creative_fields = [{'id': x.creative_field, 'name': x.get_creative_field()} for x in fields_set]
        return creative_fields


    def delete_creative_field(self, field_id):
        """
        Delete the specified creative field
        """
        fields_set = CreativeFields.objects.filter(userprofile=self).filter(creative_field=field_id)
        map(lambda x: x.delete(), fields_set)


    def delete_creative_fields(self):
        """
        Delete all the creative fields
        """
        fields_set = CreativeFields.objects.filter(userprofile=self)
        map(lambda x: x.delete(), fields_set)


    #=========================================================================
    # WRAPPER
    #=========================================================================
    def _get_display(self, key, list):
        d = dict(list)
        if key in d:
            return d[key]
        return None

    def _country_verbose(self):
        ''' Return the string associated to a country ''' 
        return self._get_display(self.country, COUNTRIES)    

    def _sex_verbose(self):
        ''' Return the string associated to the sex ''' 
        return self._get_display(self.sex, GENDER)

    def _availability_verbose(self):
        ''' Return the string associated to the availability ''' 
        return self._get_display(self.availability, AVAILABILITY)

    def wrapper(self):
        """
        Return a wrapper for a `UserProfile` object, i.e. a dictionary containing all the data
        """
        wrapper = model_to_dict(self)
        wrapper['full_name']    = self.full_name
        wrapper['country']      = self._country_verbose()
        wrapper['sex']          = self._sex_verbose()
        wrapper['availability'] = self._availability_verbose()
        del wrapper['user']
        del wrapper['id']

        # UserAuth
        user_auth = self.get_user_auth_wrapper()
        wrapper.update(user_auth)

        # Profile Pic - Gravatar
        wrapper['profile_pic'] = self.get_profile_pic()

        # Connected Accounts
        connected_accounts = self.get_connected_accounts()
        wrapper['connected_accounts'] = connected_accounts

        # Employment
        wrapper['employment'] = self.get_employment_wrapper()

        # Creative Fields
        wrapper['creative_fields'] = self.get_creative_fields()
        
        return wrapper
