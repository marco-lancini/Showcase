from django.db import models
from django.forms.models import model_to_dict
from settings import BASE_URL

from app_users.models import UserProfile
from app_projects.models_nn import Votes, Collaborations
from app_collaborations.options import CATEGORIES

from app_socialnetworks.tumblr import TumblrClient
from app_socialnetworks.flickr import FlickrClient


class Material(models.Model):
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
        return self.description


    #=========================================================================
    # TUMBLR
    #=========================================================================
    def tumblr_get_posts(self):
        # Tumblr
        t = TumblrClient(self.tumblr)
        posts = t.get_blog_posts()
        return posts


    def get_client(self, username):
        # Retrieve user from username
        user = UserProfile.objects.get(user__username__exact=username)
        
        # Instantiate wrapper with authentication permission
        f = TumblrClient(self.tumblr, user_auth=user.user, auth=True)

        return f


    def tumblr_add_text(self, username, title, body):
        # Get client
        f = self.get_client(username)

        # Upload Text Post
        f.add_text(title, body)


    def tumblr_add_link(self, username, title, url):
        f = self.get_client(username)
        f.add_link(title, url)


    def tumblr_add_quote(self, username, quote):
        f = self.get_client(username)
        f.add_quote(quote)

    def tumblr_add_chat(self, username, title, conversation):
        f = self.get_client(username)
        f.add_chat(title, conversation)


    def tumblr_add_photo(self, username, source, data):
        f = self.get_client(username)
        f.add_photo(source, data)

    def tumblr_add_audio(self, username, source):
        f = self.get_client(username)
        f.add_audio(source)

    # def tumblr_add_video(self, username, data):
    #     f = self.get_client(username)
    #     f.add_video(data)    


        


    #=========================================================================
    # FLICKR
    #=========================================================================
    def flickr_get_photos(self):
        ''' Return a list of 6 photos '''
        f = FlickrClient(self.flickr)

        n = 6
        photolist = f.get_photolist(6)
        if photolist:
            photos = [f.get_photo(x) for x in photolist]
        else:
            photos = None

        return photos


    def flickr_get_url(self, owner):
        try:
            user = owner.user.social_auth.filter(user=owner.user.id).filter(provider="flickr")[0]
            uid  = user.uid
            url = 'http://www.flickr.com/photos/%s/sets/%s/' % (uid, self.flickr)
            return url
        except:
            return "http://www.flickr.com/"




    def flickr_add_photo(self, username, title, description, photo):
        # Retrieve user from username
        user = UserProfile.objects.get(user__username__exact=username)
        
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
        return [self.youtube1, self.youtube2]

        

    


    #=========================================================================
    def wrapper(self):
        ''' Return a dict with elem=true if the project has that piece of material '''
        temp = model_to_dict(self)
        del temp['id']

        wrapper = {}
        for k in temp.keys():
            wrapper[k] = True if temp[k] else False

        return wrapper









class Project(models.Model):
    ''' PROJECT class '''
	# Relationships
    # TODO: CASCADE?
    owner    = models.ForeignKey(UserProfile, related_name='projects_own', on_delete=models.CASCADE)

    # Others
    category    = models.CharField(max_length=3, choices=CATEGORIES, blank=False)
    title       = models.CharField(max_length=100, blank=False)
    summary     = models.TextField(max_length=500, blank=False, help_text='Max. 500 characters')
    start_date  = models.DateField(auto_now=False, auto_now_add=False, blank=False, null=False, help_text='Please use the following format: YYYY-MM-DD')
    end_date    = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True, help_text='Please use the following format: YYYY-MM-DD.\nLeave empty if still in progress')
    website     = models.URLField("Website", blank=True)

    # Material
    material = models.ForeignKey(Material, null=True)

    
    #TODO
    #tags

    #=========================================================================
    # METHODS
    #=========================================================================
    def __unicode__(self):
        return 'Project: ' + self.title


    def get_owner(self):
        return self.owner

    def get_owner_wrapper(self):
        owner = self.get_owner()
        return owner.wrapper()




    #=========================================================================
    def get_material(self):
        ''' Return the object Material to instantiate forms in the view '''
        return self.material


    def get_material_wrapper(self):        
        if self.material:
            return self.material.wrapper()
        else:
            return None




    def get_material_extended(self):
        material_dict = self.get_material_wrapper()
        if not material_dict:
            return None


        # Access extra info
        if material_dict['description']:
            material_dict['description'] = self.material.get_description()
        
        if material_dict['flickr']:
            del material_dict['flickr']
            material_dict['flickr_photos'] = self.material.flickr_get_photos()
            material_dict['flickr_url']    = self.material.flickr_get_url(self.owner)

        if material_dict['tumblr']:
            del material_dict['tumblr']
            material_dict['tumblr_posts'] = self.material.tumblr_get_posts()

        if material_dict['youtube1'] or material_dict['youtube2']:
            del material_dict['youtube1']
            del material_dict['youtube2']
            material_dict['youtube_videos'] = self.material.youtube_get_videos()


        return material_dict
    #=========================================================================



    def delete_connected_data(self):
        # Delete collaborations
        self.delete_collaborators()

        # Delete material
        self.delete_material()

        # Delete votes
        votes = Votes.objects.filter(project=self)
        map(lambda x: x.delete(), votes)
    



    
    def get_collaborators(self):
        collaborators_set = Collaborations.objects.filter(project=self)
        collaborators     = [x.userprofile for x in collaborators_set]
        return collaborators

    def get_collaborators_wrapper(self):
        collaborators = self.get_collaborators()
        return [x.wrapper() for x in collaborators]


    def delete_collaborators(self):
        collaborators_set = Collaborations.objects.filter(project=self)
        for coll in collaborators_set:
            coll.delete()


    def delete_collaborator(self, username):
        collaborators_set = Collaborations.objects.filter(project=self).filter(userprofile__user__username=username)
        for coll in collaborators_set:
            coll.delete()


    def delete_material(self):
        if self.material:
            self.material.delete()




    def get_votes(self):
        return Votes.objects.filter(project=self).count()

    @property 
    def votes(self):
        return self.get_votes()


    def can_vote(self, user):
        # Check that can vote (must not have voted before)
        v = Votes.objects.filter(project=self).filter(user=user)
        if v.count() == 1:
            return False
        else:
            return True

    def can_unvote(self, user):
        # Check that can unvote (must have voted before)
        v = Votes.objects.filter(project=self).filter(user=user)
        if v.count() == 0:
            return False
        else:
            return True


    def vote(self, user):
        v = Votes(project=self, user=user)
        v.save()

    def unvote(self, user):
        v = Votes.objects.filter(project=self).filter(user=user)
        v.delete()


    #=========================================================================
    # WRAPPER
    #=========================================================================
    def _get_display(self, key, list):
        d = dict(list)
        if key in d:
            return d[key]
        return None

    def get_category_verbose(self):
        ''' Return the string associated to a category '''
        return self._get_display(self.category, CATEGORIES)    


    def get_category_complete(self):
        return (self.category, self.get_category_verbose())


    def wrapper(self):
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

