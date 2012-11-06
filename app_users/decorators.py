OPERATION_NOT_PERMITTED = "You don't have the permission to take this action"

def must_be_itself(method_name):
    """
        Avoid that a user can edit the profile of another one
    """
    def decorator(function):
        """
        Decorator
        """
        def _view(self, request, username, *args, **kwargs):
            """
            If the username of the request is the same as the one of the 
            requested profile, then call function
            """
            if str(username) == str(request.user):
                return function(self, request, username, *args, **kwargs)
            else:
                return self.show(request, request.user, 
                                 errors=OPERATION_NOT_PERMITTED)

        return _view

    return decorator(method_name)
