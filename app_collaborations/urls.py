from respite.urls import resource, routes, templates
from app_collaborations.views import CollaborationViews


urlpatterns = resource(
    prefix = 'collaborations/',
    views = CollaborationViews,
    routes = [
        #=========================================================================
        # CHOOSE PROJECT
        routes.route(
            regex = r'^(?:$|index%s$)' % (templates.format),
            view = 'choose_project',
            method = 'GET',
            name = 'app_collaborations.choose_project'
        ),
        #=========================================================================
        # DEFINE PARAMETERS
        routes.route(
            regex = r'^(?P<id>[0-9]+)(?:/$|%s$)' % (templates.format),
            view = 'find_collaborators',
            method = 'GET',
            name = 'app_collaborations.find_collaborators'
        ),
        # DEFINE PARAMETERS
        routes.route(
            regex = r'^(?P<id>[0-9]+)(?:/$|%s$)' % (templates.format),
            view = 'find_collaborators',
            method = 'POST',
            name = 'app_collaborations.find_collaborators'
        ),
        #=========================================================================
        # CALCULATE RESULTS
        routes.route(
            regex = r'^(?P<id>[0-9]+)/results(?:/$|%s$)' % (templates.format),
            view = 'calculate_results',
            method = 'GET',
            name = 'app_collaborations.calculate_results'
        ),
    ]
)
