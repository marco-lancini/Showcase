from django.db import models
from django.forms.models import model_to_dict
from settings import BASE_URL

from app_users.models import UserProfile
from app_projects.models_nn import Votes, Collaborations
from app_collaborations.options import CATEGORIES, get_category_verbose

from app_socialnetworks.tumblr import TumblrClient
from app_socialnetworks.flickr import FlickrClient


#=========================================================================
# MATERIAL
#=========================================================================
class Material(models.Model):
    """
    Model for `Material` objects, that contains reference to external resources related to a :class:`app_projects.models.Project`

    :description: detailed description of the project
    :tumblr: name of the connected Tumblr blog, if any 
    :flickr: id of the connected Flickr photoset, if any 
    :youtube1: id of a youtube video, if any
    :youtube2: id of a youtube video, if any
    """
    description = models.TextField("Detailed Description", max_length=1000, blank=True, help_text='Max. 1000 characters')

    tumblr      = models.CharField("Tumblr Blog", max_length=50, blank=True, null=True, 
                            help_text='Link this project to a Tumblr blog. Enter only the name of the blog: xxx from xxx.tumblr.com')
    flickr      = models.CharField("Flickr Photoset", max_length=50, blank=True, null=True, 
                            help_text='Link this project to a Flickr Photoset. Enter only the id of the set: xxx from www.flickr.com/photos/user/sets/XXX')


    youtube1    = models.CharField("Youtube Video", max_length=50, blank=True, null=True, 
                            help_text='Embed a Youtube Video. Enter only the id of the video: xxx from www.youtube.com/watch?v=xxx')
    youtube2    = models.CharField("Youtube Video", max_length=50, blank=True, null=True, 
                            help_text='Embed a Youtube Video. Enter only the id of the video: xxx from www.youtube.com/watch?v=xxx')


    #=========================================================================
    # DESCRIPTION
    #=========================================================================
    def get_description(self):
        """
        Getter for the description of the project
        
        :returns:  a string containing the detailed description of the project
        """
        return self.description


    #=========================================================================
    # TUMBLR
    #=========================================================================
    def tumblr_get_posts(self):
        """
        Fetch most recent posts from the connected blog

        :returns: a list of blog posts
        """
        # Tumblr
        t = TumblrClient(self.tumblr)
        posts = t.get_blog_posts()
        return posts


    def get_client(self, username):
        """
        Getter for the `TumblrClient`

        :returns: a `TumblrClient` with authentication permission
        """
        # Retrieve user from username
        username = str(username)
        user = UserProfile.objects.get(user__username__iexact=username)
        
        # Instantiate wrapper with authentication permission
        f = TumblrClient(self.tumblr, user_auth=user.user, auth=True)

        return f


    def tumblr_add_text(self, username, title, body):
        """
        Post text to Tumblr
        """
        # Get client
        username = str(username)
        f = self.get_client(username)

        # Upload Text Post
        f.add_text(title, body)


    def tumblr_add_link(self, username, title, url):
        """
        Post link to Tumblr
        """
        username = str(username)
        f = self.get_client(username)
        f.add_link(title, url)


    def tumblr_add_quote(self, username, quote):
        """
        Post quote to Tumblr
        """
        username = str(username)
        f = self.get_client(username)
        f.add_quote(quote)

    def tumblr_add_chat(self, username, title, conversation):
        """
        Post chat to Tumblr
        """
        username = str(username)
        f = self.get_client(username)
        f.add_chat(title, conversation)


    def tumblr_add_photo(self, username, source, data):
        """
        Post photo to Tumblr
        """
        username = str(username)
        f = self.get_client(username)
        f.add_photo(source, data)

    def tumblr_add_audio(self, username, source):
        """
        Post audio to Tumblr
        """
        username = str(username)
        f = self.get_client(username)
        f.add_audio(source)

    # def tumblr_add_video(self, username, data):
    #     f = self.get_client(username)
    #     f.add_video(data)


    #=========================================================================
    # FLICKR
    #=========================================================================
    def flickr_get_photos(self):
        """
        Fetch most recent photos from the connected photoset

        :returns: a list of photos
        """
        f = FlickrClient(self.flickr)
        n = 6

        photolist = f.get_photolist(6)
        if photolist:
            photos = [f.get_photo(x) for x in photolist]
        else:
            photos = None

        return photos


    def flickr_get_url(self, owner):
        """
        Getter for the public url of the connected photoset

        :returns: the public accessible url of the connected photoset
        """
        try:
            user = owner.user.social_auth.get(user=owner.user.id).filter(provider="flickr")
            user = user[0]
            uid  = user.uid
            url = 'http://www.flickr.com/photos/%s/sets/%s/' % (uid, self.flickr)
            return url
        except:
            return "http://www.flickr.com/"


    def flickr_add_photo(self, username, title, description, photo):
        """
        Upload a photo to Flickr and add it to the connected photoset
        """
        # Retrieve user from username
        username = str(username)
        user = UserProfile.objects.get(user__username__iexact=username)
        
        # Instantiate wrapper with authentication permission
        f = FlickrClient(self.flickr, user_auth=user.user, auth=True)

        # Upload photo
        pid = f.upload_photo(title, description, photo)

        # Associate the new photo to the connected photoset
        f.add_photo_to_photoset(pid)



    #=========================================================================
    # YOUTUBE
    #=========================================================================
    def youtube_get_videos(self):
        """
        Getter for the ids of the Youtube videos
        """
        return [self.youtube1, self.youtube2]

    
    #=========================================================================
    # OTHER
    #=========================================================================
    def wrapper(self):
        """
        Return a wrapper for a `Material` object, i.e. a dictionary with elem=true if the project has that piece of material
        """
        temp = model_to_dict(self)
        del temp['id']

        wrapper = {}
        for k in temp.keys():
            wrapper[k] = True if temp[k] else False

        return wrapper




#=========================================================================
# PROJECT
#=========================================================================
class Project(models.Model):
    """
    Model for a `Project`, one of the main resources

    :owner: :class:`app_users.models.UserProfile` that own the project
    :category: the `Category` which the project belongs
    :title: title of the project
    :summary: short summary of the project
    :start_date: date in which the project was started
    :end_date: date in which the project ended, if empty still ongoing
    :website: external website of the project
    :material: :class:`app_projects.models.Material` connected to the project
    """
    owner    = models.ForeignKey(UserProfile, related_name='projects_own', on_delete=models.CASCADE)

    category   = models.CharField(max_length=3, choices=CATEGORIES, blank=False)
    title      = models.CharField(max_length=100, blank=False)
    summary    = models.TextField(max_length=500, blank=False, help_text='Max. 500 characters')
    start_date = models.DateField(auto_now=False, auto_now_add=False, blank=False, null=False, help_text='Please use the following format: YYYY-MM-DD')
    end_date   = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True, help_text='Please use the following format: YYYY-MM-DD.\nLeave empty if still in progress')
    website    = models.URLField("Website", blank=True)

    material = models.ForeignKey(Material, null=True)


    #=========================================================================
    # METHODS
    #=========================================================================
    def __unicode__(self):
        """
        Unicode representation of the project, as its title
        """
        return 'Project: ' + self.title


    #=========================================================================
    # OWNER
    #=========================================================================
    def get_owner(self):
        """
        Getter for the owner
        """
        try:
            return self.owner
        except:
            return None

    def get_owner_wrapper(self):
        """
        Getter for the wrapper of the owner
        """
        try:
            owner = self.get_owner()
            return owner.wrapper()
        except:
            return None


    #=========================================================================
    # MATERIAL
    #=========================================================================
    def get_material(self):
        """
        Return the `Material` object connected to the project
        """
        return self.material


    def get_material_wrapper(self):        
        """
        Return the wrapper of the `Material` object connected to the project
        """
        if self.material:
            return self.material.wrapper()
        else:
            return None


    def get_material_extended(self):
        """
        Return a wrapper around all the extra-informations stored in the connected `Material`

            - description
            - flickr photos (via API call)
            - tumblr posts (via API call)
            - youtube videos
        """
        material_dict = self.get_material_wrapper()
        if not material_dict:
            return None

        # Access extra info
        if material_dict['description']:
            material_dict['description'] = self.material.get_description()
        
        if material_dict['flickr']:
            del material_dict['flickr']
            material_dict['flickr_photos'] = self.material.flickr_get_photos()

            owner = self.get_owner()
            if owner:
                material_dict['flickr_url'] = self.material.flickr_get_url(owner)
            else:
                material_dict['flickr_url'] = None

        if material_dict['tumblr']:
            del material_dict['tumblr']
            material_dict['tumblr_posts'] = self.material.tumblr_get_posts()

        if material_dict['youtube1'] or material_dict['youtube2']:
            del material_dict['youtube1']
            del material_dict['youtube2']
            material_dict['youtube_videos'] = self.material.youtube_get_videos()

        return material_dict


    def delete_material(self):
        """
        Delete all the connected material
        """
        if self.material:
            self.material.delete()

    

    #=========================================================================
    # COLLABORATORS
    #=========================================================================
    def get_collaborators(self):
        """
        Fetch all the collaborators of the project
        """
        collaborators_set = Collaborations.objects.filter(project=self)
        collaborators     = [x.userprofile for x in collaborators_set]
        return collaborators

    def get_collaborators_wrapper(self):
        """
        Fetch all the collaborators of the project, and return their wrappers
        """
        collaborators = self.get_collaborators()
        return [x.wrapper() for x in collaborators]


    def delete_collaborators(self):
        """
        Delete all the collaborations relationships
        """
        collaborators_set = Collaborations.objects.filter(project=self)
        for coll in collaborators_set:
            coll.delete()


    def delete_collaborator(self, username):
        """
        Delete the collaborators with the specified username
        """
        collaborators_set = Collaborations.objects.filter(project=self)
        for coll in collaborators_set:
            if coll.userprofile.user.username == str(username):
                coll.delete()


    #=========================================================================
    # VOTES
    #=========================================================================
    def get_votes(self):
        """
        Return the number of votes obtained from the project
        """
        return Votes.objects.filter(project=self).count()

    @property 
    def votes(self):
        return self.get_votes()

    def can_vote(self, user):
        """
        Check if the current user can vote (must not have voted before)
        """
        # Check that can vote (must not have voted before)
        v = Votes.objects.filter(project=self).filter(user=user)
        if v.count() == 1:
            return False
        else:
            return True

    def can_unvote(self, user):
        """
        Check if the current user can unvote (must have voted before)
        """
        # Check that can unvote (must have voted before)
        v = Votes.objects.filter(project=self).filter(user=user)
        if v.count() == 0:
            return False
        else:
            return True

    def vote(self, user):
        """
        Add a vote to the project
        """
        v = Votes(project=self, user=user)
        v.save()

    def unvote(self, user):
        """
        Remove a vote from the project
        """
        v = Votes.objects.filter(project=self).filter(user=user)
        v.delete()



    def delete_connected_data(self):
        # Delete collaborations
        self.delete_collaborators()

        # Delete material
        self.delete_material()

        # Delete votes
        votes = Votes.objects.filter(project=self)
        map(lambda x: x.delete(), votes)
    

    #=========================================================================
    # WRAPPER
    #=========================================================================
    def get_category_verbose(self):
        """
        Return the complete name of the category
        """
        return get_category_verbose(self.category)

    def get_category_complete(self):
        """
        Return a tuple of category id and category name
        """
        return (self.category, self.get_category_verbose())


    def wrapper(self):
        """
        Return a wrapper for a `Project` object, i.e. a dictionary containing all the data
        """
        wrapper = model_to_dict(self)
        wrapper['category'] = {'id': self.category, 'name': self.get_category_verbose()}

        if wrapper['end_date'] == None:
            wrapper['end_date'] = 'Ongoing'

        # Owner
        wrapper['owner'] = self.get_owner_wrapper()

        # Collaborators        
        wrapper['collaborators'] = self.get_collaborators_wrapper()

        # Votes
        wrapper['num_votes'] = self.get_votes()

        # Material
        wrapper['material'] = self.get_material_wrapper()

        return wrapper
