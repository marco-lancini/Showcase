from django import forms
from django.forms import ModelForm

from app_users.models import UserProfile
from app_projects.models import Project, Material
from app_projects.models_nn import Collaborations


#=========================================================================
# PROJECT
#=========================================================================
class ProjectForm(ModelForm):
	"""
    Manage a `Project` (both for creation and editing)

    .. seealso:: :class:`app_projects.models.Project`
    """
	class Meta:
		model = Project
		exclude = ('owner','material')


#=========================================================================
# COLLABORATORS
#=========================================================================
class CollaboratorsAddForm(forms.Form):
	"""
    Manage the `Collaborators` associated to the project

    .. seealso:: :class:`app_projects.models_nn.Collaborations`
    """
	def __init__(self, *args, **kwargs):
		pj_filter = kwargs.pop('pj_filter')
		super(CollaboratorsAddForm, self).__init__(*args, **kwargs)
		
		# Extract the actual collaborators of the project
		colls = Collaborations.objects.filter(project=pj_filter)
		already_present = []
		for coll in colls: 
			already_present.append(coll.userprofile.id)

		# Add the current user to the already_present users
		already_present.append(pj_filter.owner.id)

		# ModelChoiceField with a list of users that exclude the ones contained in already_present
		self.fields.insert(len(self.fields)-1, 'collaborators',
                           forms.ModelChoiceField(queryset=UserProfile.objects.exclude(id__in=already_present) ))

		# Set the project field as readonly
		self.fields['project'].widget.attrs['readonly'] = True
	
	project     = forms.ModelChoiceField( queryset=Project.objects.all() )
 	date_joined = forms.DateField(required=False, help_text='Please use the following format: YYYY-MM-DD')




#=========================================================================
# MATERIAL
#=========================================================================
class MaterialForm(ModelForm):
	"""
    Manage the `Material` associated to the project

    .. seealso:: :class:`app_projects.models.Material`
    """
	class Meta:
		model = Material
		widgets = {
			'tumblr': forms.TextInput(attrs={'placeholder': 'blog name'}),
			'flickr': forms.TextInput(attrs={'placeholder': 'photoset id'}),
			'youtube1': forms.TextInput(attrs={'placeholder': 'video id', 'label':'Youtube Video'}),
			'youtube2': forms.TextInput(attrs={'placeholder': 'video id', 'label':'Youtube Video'}),
        }


#=========================================================================
# FLICKR
#=========================================================================
class FlickrForm(forms.Form):
	"""
	Upload a photo to Flickr

	.. seealso:: :class:`app_socialnetworks.flickr.FlickrClient`
	"""
	title       = forms.CharField()
	description = forms.CharField()
	image       = forms.FileField()


#=========================================================================
# TUMBLR
#=========================================================================
class Tumblr_TextForm(forms.Form):
	"""
	Post text to Tumblr

	.. seealso:: :func:`app_socialnetworks.tumblr.TumblrClient.add_text`
	"""
	title = forms.CharField()
	body  = forms.CharField()


class Tumblr_LinkForm(forms.Form):
	"""
	Post link to Tumblr

	.. seealso:: :func:`app_socialnetworks.tumblr.TumblrClient.add_link`
	"""
	title = forms.CharField()
	url   = forms.URLField()


class Tumblr_QuoteForm(forms.Form):
	"""
	Post quote to Tumblr

	.. seealso:: :func:`app_socialnetworks.tumblr.TumblrClient.add_quote`
	"""
	quote = forms.CharField()


class Tumblr_ChatForm(forms.Form):
	"""
	Post chat to Tumblr

	.. seealso:: :func:`app_socialnetworks.tumblr.TumblrClient.add_chat`
	"""
	title 		 = forms.CharField()
	conversation = forms.CharField(widget=forms.Textarea(attrs={'placeholder': "Tom: Hi! How are you?\n Jack: I'm fine, thanks."}))


class Tumblr_PhotoForm(forms.Form):
	"""
	Post photo to Tumblr

	.. seealso:: :func:`app_socialnetworks.tumblr.TumblrClient.add_photo`
	"""
	source  = forms.URLField(required=False, label='URL of the photo')
	data    = forms.FileField(required=False, label='Or upload an image', help_text='Limit: 5MB')

	def clean(self):
		cleaned_data = self.cleaned_data

		source = cleaned_data.get("source")
		data   = cleaned_data.get("data")

		if source and data:
			raise forms.ValidationError("Please, choose only one type of upload (URL or upload from your PC)")

		if not source and not data:
			raise forms.ValidationError("Please, insert an URL or upload an image")

		if data and data.size > 5242880:
			raise forms.ValidationError('Please keep filesize under 5MB')

		return cleaned_data
		

class Tumblr_AudioForm(forms.Form):
	"""
	Post audio to Tumblr

	.. seealso:: :func:`app_socialnetworks.tumblr.TumblrClient.add_audio`
	"""
	source = forms.URLField(required=False, label='URL of the audio file')


# class Tumblr_VideoForm(forms.Form):
# 	data   = forms.FileField(required=False, label='Upload a video', help_text='Limit: 5MB')

# 	def clean(self):
# 		cleaned_data = self.cleaned_data

# 		data   = cleaned_data.get("data")

# 		if data and data.size > 5242880:
# 			raise forms.ValidationError('Please keep filesize under 5MB')

# 		return cleaned_data

