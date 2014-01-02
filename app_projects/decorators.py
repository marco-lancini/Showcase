from functools import wraps
from django.shortcuts import get_object_or_404
from app_projects.models import Project

OPERATION_NOT_PERMITTED = "You don't have the permission to take this action"
NO_VOTE_OWNER           = "You can't vote your own project"
NO_VOTE_COLLABORATOR    = "You can't vote a project in which you collaborate"


def must_be_owner(method_name):
    """
        Avoid that a user can edit a project he doesn't own
    """
    def decorator(function):
        @wraps(function)
        def _view(self, request, id, *args, **kwargs):
            p = get_object_or_404(Project, pk=id)
            if str(p.owner.user.username) == str(request.user):
                return function(self, request, id, p, *args, **kwargs)
            else:
                return self.show(request, id, errors=OPERATION_NOT_PERMITTED)

        return _view

    return decorator(method_name)


def no_conflict_of_interests(method_name):
    """
        Avoid that a user vote a project he own or in which he collaborate
    """
    def decorator(function):
        @wraps(function)
        def _view(self, request, id, *args, **kwargs):
            p = get_object_or_404(Project, pk=id)

            # Check Owner
            if str(p.owner.user.username) == str(request.user):
                return self.show(request, id, errors=NO_VOTE_OWNER)

            # Check Collaborators
            collaborators = p.get_collaborators_wrapper()
            if str(request.user) in [x['username'] for x in collaborators]:
                return self.show(request, id, errors=NO_VOTE_COLLABORATOR)
        
            # Return the function
            return function(self, request, id, p, *args, **kwargs)

        return _view

    return decorator(method_name)
