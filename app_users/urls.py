from respite.urls import resource, routes, templates
from app_users.views import UserProfileViews

urlpatterns = resource(
    prefix = 'users/',
    views = UserProfileViews,
    routes = [
        #=========================================================================
        # INDEX - FORBIDDEN
        routes.route(
            regex = r'^(?:$|index%s$)' % (templates.format),
            view = 'index',
            method = 'GET',
            name = 'app_users.index'
        ),
        #=========================================================================
        # NEW - FORBIDDEN
        routes.route(
            regex = r'^new(?:/$|%s$)' % (templates.format),
            view = 'new',
            method = 'GET',
            name = 'app_users.new'
        ),
        #=========================================================================
        # CREATE - FORBIDDEN
        routes.route(
            regex = r'^(?:$|index%s$)' % (templates.format),
            view = 'create',
            method = 'POST',
            name = 'app_users.create'
        ),
        #=========================================================================
        # SHOW
        routes.route(
            regex = r'^(?P<username>\w+)(?:/$|%s$)' % (templates.format),
            view = 'show',
            method = 'GET',
            name = 'app_users.user_view'
        ),
        #=========================================================================
        # EDIT
        routes.route(            
            regex = r'^(?P<username>\w+)/edit(?:/$|%s$)' % (templates.format),
            view = 'edit',
            method = 'GET',
            name = 'app_users.user_edit'
        ),
        routes.route(            
            regex = r'^(?P<username>\w+)/edit(?:/$|%s$)' % (templates.format),
            view = 'edit',
            method = 'POST',
            name = 'app_users.user_edit'
        ),
        #=========================================================================
        # REPLACE
        routes.route(            
            regex = r'^(?P<username>\w+)(?:/$|%s$)' % (templates.format),
            view = 'replace',
            method = 'PUT',
            name = 'app_users.user_replace'
        ),
        #=========================================================================
        # UPDATE
        routes.route(            
            regex = r'^(?P<username>\w+)(?:/$|%s$)' % (templates.format),
            view = 'update',
            method = 'PATCH',
            name = 'app_users.user_update'
        ),
        #=========================================================================
        # DESTROY
        routes.route(            
            regex = r'^(?P<username>\w+)/destroy(?:/$|%s$)' % (templates.format),
            view = 'destroy',
            method = 'GET',
            name = 'app_users.user_destroy'
        ),
        routes.route(            
            regex = r'^(?P<username>\w+)/destroy(?:/$|%s$)' % (templates.format),
            view = 'destroy',
            method = 'DELETE',
            name = 'app_users.user_destroy'
        ),
        #=========================================================================
        # SETTINGS
        routes.route(            
            regex = r'^(?P<username>\w+)/settings(?:/$|%s$)' % (templates.format),
            view = 'settings',
            method = 'GET',
            name = 'app_users.user_settings'
        ),
        # SETTINGS EDIT
        routes.route(            
            regex = r'^(?P<username>\w+)/settings/edit(?:/$|%s$)' % (templates.format),
            view = 'settings_edit',
            method = 'GET',
            name = 'app_users.user_settings_edit'
        ),
        routes.route(            
            regex = r'^(?P<username>\w+)/settings/edit(?:/$|%s$)' % (templates.format),
            view = 'settings_edit',
            method = 'POST',
            name = 'app_users.user_settings_edit'
        ),
        #=========================================================================
        # LIST OF VOTED PROJECTS
        routes.route(            
            regex = r'^(?P<username>\w+)/voted(?:/$|%s$)' % (templates.format),
            view = 'voted',
            method = 'GET',
            name = 'app_users.user_voted'
        ),
        #=========================================================================
        # ADD CREATIVE FIELDS
        routes.route(            
            regex = r'^(?P<username>\w+)/fields(?:/$|%s$)' % (templates.format),
            view = 'creative_fields_manage',
            method = 'GET',
            name = 'app_users.user_fields'
        ),
        routes.route(            
            regex = r'^(?P<username>\w+)/fields(?:/$|%s$)' % (templates.format),
            view = 'creative_fields_manage',
            method = 'POST',
            name = 'app_users.user_fields'
        ),
        # DELETE CREATIVE FIELD
        routes.route(
            regex = r'^(?P<username>\w+)/fields/delete/(?P<field_id>\w+)(?:/$|%s$)' % (templates.format),
            view = 'creative_fields_delete',
            method = 'POST',
            name = 'app_users.creative_fields_delete'
        ),
        #=========================================================================
        # EMPLOYMENT
        routes.route(            
            regex = r'^(?P<username>\w+)/employment(?:/$|%s$)' % (templates.format),
            view = 'employment_manage',
            method = 'GET',
            name = 'app_users.user_employment'
        ),
        routes.route(            
            regex = r'^(?P<username>\w+)/employment(?:/$|%s$)' % (templates.format),
            view = 'employment_manage',
            method = 'POST',
            name = 'app_users.user_employment'
        ),
        # EMPLOYMENT FROM LINKEDIN
        routes.route(            
            regex = r'^(?P<username>\w+)/employment/linkedin(?:/$|%s$)' % (templates.format),
            view = 'employment_linkedin',
            method = 'GET',
            name = 'app_users.user_employment_linkedin'
        ),
        
    ]
)
