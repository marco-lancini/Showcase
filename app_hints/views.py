# from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.http import HttpResponseRedirect

from respite import Views
from respite.decorators import rest_login_required

from app_users.models import UserProfile
from app_projects.models import Project
from app_projects.models_nn import Votes, Collaborations

import collections
from operator import itemgetter

        


#=========================================================================
# HintViews
#=========================================================================
class HintViews(Views):
    supported_formats = ['html', 'json']
    template_path     = 'app_hints/'


    @rest_login_required
    def hints_projects(self, request):
        # Retrieve current user
        username = str(request.user)
        u = get_object_or_404(UserProfile, user__username__iexact=username)
        u_dict = u.wrapper()

        # Calculate an ordered list of most frequent categories (both from his projects and from his votes)
        # most_frequent: [(u'IT', 3), (u'PI', 1), (u'DS', 1)]
        max_num_category = 5
        most_frequent    = self.__most_frequent_categories(u, max_num_category)

        # For each category keep only those projects not connected with the user
        not_connected = map( (lambda category: self.__not_connected_in_category(category, u)), most_frequent )

        # Select most voted projects of each category
        # most_voted:
        #   [[{'num_votes': 1, 'p': <Project>}, {'num_votes': 0, 'p': <Project>}],
        #    [],
        #    [{'num_votes': 0, 'p': <Project>}]]
        max_pj = 10
        most_voted = map( (lambda projects: self.__most_voted(projects, max_pj)), not_connected )

        # Flatten the list and filter out num_votes
        # selected_projects:
        #   [{'num_votes': 1, 'p': <Project>},
        #    {'num_votes': 0, 'p': <Project>},
        #    {'num_votes': 0, 'p': <Project>}]
        # selected_projects:
        #   [<Project>, <Project>, <Project>]
        selected_projects = [item['p'] for sublist in most_voted for item in sublist] 


        # Render the page
        return self._render(
            request = request,
            template = 'hints',
            context = {
                'u': u_dict,
                'itself': True,
                'project_list': selected_projects,
            },
            status = 200
        )





    #=========================================================================
    # MOST FREQUENT
    #=========================================================================
    def __most_frequent_categories(self, u, max_num_category):
        """
        Returns an ordered list of categories with the corresponding projects involved
        (owned or voted)
        """
        # Extract the categories among the projects (both owned or in which he collaborate)
        from_projects = []
        from_projects.extend( u.get_projects_own() )
        from_projects.extend( u.get_projects_collaborate() )

        # Extract the categories among his votes (those he voted)
        from_votes = u.get_projects_voted()

        # Group the categories coming from the 2 sets 
        all_categories = from_projects + from_votes 

        # Count the frequencies of each category (duplicates will increase the counter)
        most_frequent = self.__group_and_count(all_categories, max_num_category)

        # Return an ordered list: [(u'IT', 3), (u'PI', 1), (u'DS', 1)]
        return most_frequent

    
    def __group_and_count(self, projects_set, limit):
        # Group by category
        categories = [x.category for x in projects_set]
        categories = collections.Counter(categories)    # Counter({u'IT': 2, u'PI': 1, u'DS': 1})

        # Select the n most common categories
        most_frequent = categories.most_common(limit)   # [(u'IT', 2)] with n=1
                                                        
        return most_frequent



    #=========================================================================
    # FILTER PROJECT NOT CONNECTED WITH THE USER
    #=========================================================================
    def __not_connected_in_category(select, category, u):
        """
        For each category select projects that are not connected with the user u
        (no owner, no collaborator, no voted)
        """
        category_id = category[0]  # category = (u'IT', 2)

        # Gather all projects belonging to the category
        projects_set = Project.objects.filter(category=category_id)

        # Exclude the ones owned by the user
        no_owner = projects_set.exclude(owner=u)

        # Exclude the ones in which the user collaborate
        no_collaborate = no_owner.exclude( id__in=[o.project.id for o in Collaborations.objects.filter(userprofile=u)] )

        # Exclude the ones voted by the user
        no_vote = no_collaborate.exclude( id__in=[o.project.id for o in Votes.objects.filter(user=u)] )
        
        return no_vote



    #=========================================================================
    # MOST VOTED
    #=========================================================================
    def __most_voted(self, projects_set, limit=10):
        """
        Returns the LIMIT most voted project in the category
        """
        # Get corresponding votes
        # [{'p': <Project>, 'num_votes': 0}, {'p': <Project>, 'num_votes': 1}]
        projects_votes = [{'p':x, 'num_votes':x.get_votes()} for x in projects_set]   

        # Order by votes
        most_voted = sorted(projects_votes, key=itemgetter('num_votes'))
        most_voted.reverse()        

        # Returns the n most voted
        return most_voted[:limit]
