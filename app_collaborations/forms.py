from django import forms
from django.utils.translation import ugettext as _

from app_collaborations.options import get_creative_fields
from app_users.countries import AVAILABILITY, COUNTRIES

#=========================================================================
# CHOICES
#=========================================================================
PAY = (
    (0, 'No'),
    (1, 'Yes'),
)

LOCATIONS = (('--', _('Any')),) + COUNTRIES


#=========================================================================
# FORM
#=========================================================================
class CollaborationsForm(forms.Form):
    """
    Ask user for preferences about collaborators

    :pay: boolean that indicate the will to pay for collaborators
    :location: location of collaborators to search
    :availability: Full-Time, Part-Time, Consulting, Freelance, Internship
    :creative_fields: list of creative fields to search (prefiltered using only those belonging to the category of the project)
    """
    def __init__(self, *args, **kwargs):
        """
        Filter creative fields based on the category of the project
        """
        p = kwargs.pop('pj_filter')
        super(CollaborationsForm, self).__init__(*args, **kwargs)

        # Filter creative fields based on the category of the project
        category = p.get_category_complete()
        filtered_fields = get_creative_fields(category)

        # Add field
        self.fields.insert( len(self.fields)-1, 'creative_fields',
                            forms.MultipleChoiceField( required=False, widget=forms.CheckboxSelectMultiple, choices=filtered_fields, 
                                                       help_text='Leave empty to search automatically' ) )


    pay          = forms.ChoiceField(required=True, widget=forms.Select, choices=PAY, label='Are you willing to pay your collaborators?',
                                     help_text='If No, the service will look only for those users available to work for free')
    location     = forms.ChoiceField(required=True, widget=forms.Select, choices=LOCATIONS, label='Choose country of your collaborators')
    availability = forms.MultipleChoiceField(required=True, widget=forms.CheckboxSelectMultiple, choices=AVAILABILITY, 
                                             label='Choose the availability of the collaborators you need')
