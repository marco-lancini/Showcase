from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from app_users.models import UserProfile, Employment
from app_users.models_nn import CreativeFields
from app_collaborations.options import CREATIVE_FIELDS


class UserProfileForm(ModelForm):
	"""
	Form tailored on the :class:`UserProfile` model

    :returns:  form with all the fields of a :class:`UserProfile` (data related to the authentication are excluded)
	"""
	class Meta:
		model = UserProfile
		exclude = ('user', 'employment')


class UserAuthForm(ModelForm):
	"""
	Form tailored on the

    :returns:  form 
	"""
	class Meta:
		model = User
		fields = ('email',)



class EmploymentForm(ModelForm):
	class Meta:
		model = Employment




class CreativeFieldsAddForm(forms.Form):
	class Meta:
		model = CreativeFields
		exclude = ('userprofile',)

	def __init__(self, *args, **kwargs):
		user_filter = kwargs.pop('user_filter')
		super(CreativeFieldsAddForm, self).__init__(*args, **kwargs)
		
		fields = CreativeFields.objects.filter(userprofile=user_filter)
		already_present = [ x.creative_field for x in fields ]

		actual_choices = [ (k, v) for k, v in CREATIVE_FIELDS if k not in already_present ]
		actual_choices = tuple(tuple(x) for x in actual_choices)

		self.fields.insert(len(self.fields)-1, 'creative_field', forms.ChoiceField(choices=actual_choices))
