from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.http import HttpResponseRedirect

from respite import Views
from respite.decorators import rest_login_required

from app_collaborations.forms import CollaborationsForm
from app_collaborations.options import get_creative_fields, get_creative_field_verbose
from app_users.models import UserProfile
from app_users.models_nn import CreativeFields
from app_projects.decorators import must_be_owner      


#=========================================================================
# CollaborationViews
#=========================================================================
class CollaborationViews(Views):
    """
    View that manage access to the Collaboration service

    :supported_formats: html, json
    :template_path: path to html files
    """
    supported_formats = ['html', 'json']
    template_path     = 'app_collaborations/'


    #=========================================================================
    # CHOOSE PROJECT
    #=========================================================================
    @rest_login_required
    def choose_project(self, request):
        """
        List all the projects owned by the user and let him choose for which one he wants suggestions
        
        :Decorators: ``rest_login_required``
        :Rest Types: ``GET``
        :URL: ``^collaborations/(?:$|index.(html|json)$)``
        """
        # Retrieve current user
        username = str(request.user)
        u = get_object_or_404(UserProfile, user__username__iexact=username)
        u_dict = u.wrapper()

        # Retrieve owned projects
        owned_projects = u.get_projects_own()

        # Render the page
        return self._render(
            request = request,
            template = 'choose_project',
            context = {
                'u': u_dict,
                'itself': True,
                'project_list': owned_projects,
            },
            status = 200
        )

    #=========================================================================
    # DEFINE PARAMETERS
    #=========================================================================
    @rest_login_required
    @must_be_owner
    def find_collaborators(self, request, id, p):
        """
        Render the form in order to ask user his preferences:
            - willingness to pay
            - location of collaborators
            - availability of collaborators
            - creative fields to search for
        
        :Decorators: ``rest_login_required, must_be_owner``
        :Rest Types: ``GET, POST``
        :URL: ``^collaborations/(?P<id>[0-9]+)(?:/$|.(html|json)$)``
        """

        if request.method == 'POST':
            form = CollaborationsForm(request.POST, pj_filter=p)
            if form.is_valid():
                pay             = form.cleaned_data['pay']
                location        = form.cleaned_data['location']
                availability    = form.cleaned_data['availability']
                creative_fields = form.cleaned_data['creative_fields']

                # Calculate result
                return self.calculate_results(request, id, pay, location, creative_fields, availability)
            else:
                status = 400
        else:
            form   = CollaborationsForm(pj_filter=p)
            status = 200


        # Render page
        return self._render(
            request = request,
            template = 'form_simple',
            context = {
                'param_title': p.title,
                'param_subtitle': "Find Collaborators",
                'param_media': False,
                'url_confirm': reverse('app_collaborations.find_collaborators', args=[p.id]),
                'url_cancel': reverse('app_projects.project_view', args=[p.id]),
                'form': form,
            },
            status = status,
            prefix_template_path = False
        )



    #=========================================================================
    # CALCULATE RESULTS
    #=========================================================================
    @rest_login_required
    @must_be_owner
    def calculate_results(self, request, id, p, pay, location, creative_fields, availabilities):
        """
        Find collaborators:
            1. groups users based on creative fields (excluding the user himself)
            2. keep only those users with a matching availability
            3. filter based on location
            4. filter based on willingness to pay (if yes use all the users, otherwise use all the users with fee equal to true or null)
            5. for each category, order users by number of projects and votes
            6. for each category, select only the first ones
        
        :Decorators: ``rest_login_required, must_be_owner``
        :Rest Types: ``GET``
        :URL: ``^collaborations/(?P<id>[0-9]+)/results(?:/$|.(html|json)$)``
        """
        # Retrieve username of current user
        username = str(request.user)

        # Groups users based on creative fields (excluding the user himself)
        # groups:
        #   {'WD': [<UserProfile: aa>, <UserProfile: altro>],
        #    'WV': [<UserProfile: aa>]}
        groups = self.__filter_creative_fields(p, creative_fields, username)

        # Keep only those users with a matching Availability
        groups = self.__filter_availability(groups, availabilities)

        # Filter based on location
        groups = self.__filter_location(groups, location)

        # Filter based on pay
        #   pay = yes --> use all the users
        #   pay = no  --> use all the users with fee=true or null
        groups = self.__filter_pay(groups, pay)

        # For each category, order users by number of projects and votes
        # users_ordered:
        #   {'WD': [{'num_projects': 4, 'num_votes': 2, 'u': <UserProfile: altro>},
        #           {'num_projects': 1, 'num_votes': 0, 'u': <UserProfile: aa>}],
        #    'WV': [{'num_projects': 1, 'num_votes': 0, 'u': <UserProfile: aa>}]}
        groups = self.__order_by_projects(groups)

        # For each category, select only the first LIMIT users
        limit  = 10
        groups = self.__limit(groups, limit)

        # Return iterator to template
        groups = groups.iteritems()

        # Render page
        return self._render(
            request = request,
            template = 'collaborations_result',
            context = {
                'p': p,
                'groups': groups
            },
            status = 200,
        )



    def __filter_creative_fields(self, p, creative_fields, username):
        ''' Returns all the users with those creative fields '''
        if creative_fields == []:
            # Use all the creative fields of the category of the project
            category = p.get_category_complete()
            fields = get_creative_fields(category)
            creative_fields = [x[0] for x in fields]
        else:
            # Use the creative fields selected by the user
            creative_fields = creative_fields

        # For each field select users having it
        groups = {}
        for cf in creative_fields:
            # Select users with at least one of these fields
            user_with_cf = CreativeFields.objects.filter(creative_field=cf)

            # Avoid duplicates and the user himself
            users = []
            for x in user_with_cf:
                if x.userprofile not in users and x.userprofile.user.username != str(username):
                    users.append(x.userprofile)

            # Get verbose name of creative field
            verbose_name = get_creative_field_verbose(cf)

            # Add users to the group of current creative field
            groups[verbose_name] = users

        return groups


    def __filter_availability(self, groups, availabilities):
        ''' Keep only those users with a matching Availability '''
        new_groups = {}
        for k,v in groups.items():
            new_groups[k] = filter(lambda x: x.availability in availabilities, v)

        return new_groups


    def __filter_location(self, groups, location):
        ''' Keep only those users with a matching Location '''
        any_location = '--'
        if location == any_location:
            return groups

        new_groups = {}
        for k,v in groups.items():
            new_groups[k] = filter(lambda x: x.country == location, v)

        return new_groups


    def __filter_pay(self, groups, pay):
        '''
        Keep only those users with a matching Fee 
            pay = yes --> use all the users
            pay = no  --> use all the users with fee=true or null
        '''
        pay_no, pay_yes = 0, 1

        if pay == pay_yes:
            # Keep all the users
            return groups

        # Use all the users with fee=true or none
        new_groups = {}
        for k,v in groups.items():
            new_groups[k] = filter(lambda x: x.fee == True or x.fee == None, v)

        return new_groups


    def __order_by_projects(self, groups):
        ''' For each user, retrieve number of projects and number of votes of each project '''
        new_groups = {}
        for k,v in groups.items():
            users_projects = map(lambda x: 
                    {'u': x, 
                     'num_projects': len(x.get_projects_own()) + len(x.get_projects_collaborate()),
                     'num_votes': reduce(lambda y,z: y+z.get_votes(), x.get_projects_own(), 0) + 
                                  reduce(lambda y,z: y+z.get_votes(), x.get_projects_collaborate(), 0)
                     }, 
                     v)
            users_sorted   = sorted(users_projects)
            users_sorted.reverse()
            new_groups[k]  = users_sorted

        return new_groups


    def __limit(self, groups, limit=10):
        new_groups = {}
        for k,v in groups.items():
            new_groups[k] = v[:limit]

        return new_groups

