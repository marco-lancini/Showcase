from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from app_users.models import UserProfile, Employment
from app_users.models_nn import CreativeFields
from app_collaborations.options import CREATIVE_FIELDS


#=========================================================================
# USER
#=========================================================================
class UserProfileForm(ModelForm):
	"""
	Manage the basic informations of a user profile

    .. seealso:: :class:`app_users.models.UserProfile`
	"""
	class Meta:
		model = UserProfile
		exclude = ('user', 'employment')


class UserAuthForm(ModelForm):
	"""
	Manage the account informations of a user profile
	"""
	class Meta:
		model = User
		fields = ('email',)


#=========================================================================
# EMPLOYMENT
#=========================================================================
class EmploymentForm(ModelForm):
	"""
	Manage the employment data of a user

    .. seealso:: :class:`app_users.models.Employment`
	"""
	class Meta:
		model = Employment


#=========================================================================
# CREATIVE FIELDS
#=========================================================================
class CreativeFieldsAddForm(forms.Form):
	"""
	Manage the creative fields of a user

    .. seealso:: :class:`app_users.models_nn.CreativeFields`
	"""
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
