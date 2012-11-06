from django import forms
from django.forms import ModelForm

from app_users.models import UserProfile
from app_projects.models import Project, Material
from app_projects.models_nn import Collaborations


class MaterialForm(ModelForm):
	class Meta:
		model = Material
		widgets = {
			'tumblr': forms.TextInput(attrs={'placeholder': 'blog name'}),
			'flickr': forms.TextInput(attrs={'placeholder': 'photoset id'}),
			'youtube1': forms.TextInput(attrs={'placeholder': 'video id', 'label':'Youtube Video'}),
			'youtube2': forms.TextInput(attrs={'placeholder': 'video id', 'label':'Youtube Video'}),
        }



class FlickrForm(forms.Form):
	title       = forms.CharField()
	description = forms.CharField()
	image       = forms.FileField()




class Tumblr_TextForm(forms.Form):
	title = forms.CharField()
	body  = forms.CharField()

class Tumblr_LinkForm(forms.Form):
	title = forms.CharField()
	url   = forms.URLField()

class Tumblr_QuoteForm(forms.Form):
	quote = forms.CharField()

class Tumblr_ChatForm(forms.Form):
	title 		 = forms.CharField()
	conversation = forms.CharField(widget=forms.Textarea(attrs={'placeholder': "Tom: Hi! How are you?\n Jack: I'm fine, thanks."}))


class Tumblr_PhotoForm(forms.Form):
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
	source = forms.URLField(required=False, label='URL of the audio file')
	# data   = forms.FileField(required=False, label='Or upload an audio file', help_text='Limit: 5MB')

	# def clean(self):
	# 	cleaned_data = self.cleaned_data

	# 	source = cleaned_data.get("source")
	# 	data   = cleaned_data.get("data")

	# 	if source and data:
	# 		raise forms.ValidationError("Please, choose only one type of upload (URL or upload from your PC)")

	# 	if not source and not data:
	# 		raise forms.ValidationError("Please, insert an URL or upload an audio file")

	# 	if data and data.size > 5242880:
	# 		raise forms.ValidationError('Please keep filesize under 5MB')

	# 	return cleaned_data


# class Tumblr_VideoForm(forms.Form):
# 	data   = forms.FileField(required=False, label='Upload a video', help_text='Limit: 5MB')

# 	def clean(self):
# 		cleaned_data = self.cleaned_data

# 		data   = cleaned_data.get("data")

# 		if data and data.size > 5242880:
# 			raise forms.ValidationError('Please keep filesize under 5MB')

# 		return cleaned_data






class ProjectForm(ModelForm):
	class Meta:
		model = Project
		exclude = ('owner','material')




class CollaboratorsAddForm(forms.Form):

	def __init__(self, *args, **kwargs):
		pj_filter = kwargs.pop('pj_filter')
		super(CollaboratorsAddForm, self).__init__(*args, **kwargs)
		
		#options = UserProfile.objects.exclude()
		#collaborators = forms.ModelMultipleChoiceField(queryset=options)
		colls = Collaborations.objects.filter(project=pj_filter)
		already_present = []
		for coll in colls: 
			already_present.append(coll.userprofile.id)

		already_present.append(pj_filter.owner.id)



		self.fields.insert(len(self.fields)-1, 'collaborators',
                           forms.ModelChoiceField(queryset=UserProfile.objects.exclude(id__in=already_present) ))

		self.fields['project'].widget.attrs['readonly'] = True

	
	
	project     = forms.ModelChoiceField( queryset=Project.objects.all() )
 	date_joined = forms.DateField(required=False, help_text='Please use the following format: YYYY-MM-DD')
