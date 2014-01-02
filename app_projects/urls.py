from respite.urls import resource, routes, templates
from app_projects.views import ProjectViews


urlpatterns = resource(
    prefix = 'projects/',
    views = ProjectViews,
    routes = [
        #=========================================================================
        # INDEX
        routes.route(
            regex = r'^(?:$|index%s$)' % (templates.format),
            view = 'index',
            method = 'GET',
            name = 'app_projects.index'
        ),
        #=========================================================================
        # NEW
        routes.route(
            regex = r'^new(?:/$|%s$)' % (templates.format),
            view = 'new',
            method = 'GET',
            name = 'app_projects.new'
        ),
        #=========================================================================
        # CREATE
        routes.route(
            regex = r'^(?:$|index%s$)' % (templates.format),
            view = 'create',
            method = 'POST',
            name = 'app_projects.create'
        ),
        #=========================================================================
        # SHOW
        routes.route(
            regex = r'^(?P<id>[0-9]+)(?:/$|%s$)' % (templates.format),
            view = 'show',
            method = 'GET',
            name = 'app_projects.project_view'
        ),
        #=========================================================================
        # EDIT
        routes.route(            
            regex = r'^(?P<id>[0-9]+)/edit(?:/$|%s$)' % (templates.format),
            view = 'edit',
            method = 'GET',
            name = 'app_projects.project_edit'
        ),
        routes.route(            
            regex = r'^(?P<id>[0-9]+)/edit(?:/$|%s$)' % (templates.format),
            view = 'edit',
            method = 'POST',
            name = 'app_projects.project_edit'
        ),
        #=========================================================================
        # REPLACE
        routes.route(            
            regex = r'^(?P<id>[0-9]+)(?:/$|%s$)' % (templates.format),
            view = 'replace',
            method = 'PUT',
            name = 'app_projects.project_replace'
        ),
        #=========================================================================
        # UPDATE
        routes.route(            
            regex = r'^(?P<id>[0-9]+)(?:/$|%s$)' % (templates.format),
            view = 'update',
            method = 'PATCH',
            name = 'app_projects.project_update'
        ),
        #=========================================================================
        # DESTROY
        routes.route(            
            regex = r'^(?P<id>[0-9]+)/destroy(?:/$|%s$)' % (templates.format),
            view = 'destroy',
            method = 'GET',
            name = 'app_projects.project_destroy'
        ),
        routes.route(            
            regex = r'^(?P<id>[0-9]+)/destroy(?:/$|%s$)' % (templates.format),
            view = 'destroy',
            method = 'DELETE',
            name = 'app_projects.project_destroy'
        ),
        #=========================================================================
        # VOTE
        routes.route(
            regex = r'^(?P<id>[0-9]+)/vote(?:/$|%s$)' % (templates.format),
            view = 'vote',
            method = 'POST',
            name = 'app_projects.project_vote'
        ),
        # UNVOTE
        routes.route(
            regex = r'^(?P<id>[0-9]+)/unvote(?:/$|%s$)' % (templates.format),
            view = 'unvote',
            method = 'POST',
            name = 'app_projects.project_unvote'
        ),
        #=========================================================================
        # LIST BY CATEGORY
        routes.route(
            regex = r'^category/(?P<category>\w+)(?:/$|%s$)' % (templates.format),
            view = 'list_by_category',
            method = 'GET',
            name = 'app_projects.project_list_by_category'
        ),
        # BROWSE BY CATEGORY
        routes.route(
            regex = r'^category(?:/$|%s$)' % (templates.format),
            view = 'browse_by_category',
            method = 'GET',
            name = 'app_projects.project_browse_by_category'
        ),
        # LIST BY VOTES
        routes.route(
            regex = r'^votes/(?P<min_votes>[0-9]+)/(?P<max_votes>[0-9]+)(?:/$|%s$)' % (templates.format),
            view = 'list_by_votes',
            method = 'GET',
            name = 'app_projects.project_list_by_votes'
        ),
        # BROWSE BY VOTES
        routes.route(
            regex = r'^votes(?:/$|%s$)' % (templates.format),
            view = 'browse_by_votes',
            method = 'GET',
            name = 'app_projects.project_browse_by_votes'
        ),
        #=========================================================================
        # ADD COLLABORATOR
        routes.route(
            regex = r'^(?P<id>[0-9]+)/collaborators(?:/$|%s$)' % (templates.format),
            view = 'collaborators_manage',
            method = 'GET',
            name = 'app_projects.collaborators_manage'
        ),
        routes.route(
            regex = r'^(?P<id>[0-9]+)/collaborators(?:/$|%s$)' % (templates.format),
            view = 'collaborators_manage',
            method = 'POST',
            name = 'app_projects.collaborators_manage'
        ),
        # DELETE COLLABORATOR
        routes.route(
            regex = r'^(?P<id>[0-9]+)/collaborators/delete/(?P<username>\w+)(?:/$|%s$)' % (templates.format),
            view = 'collaborators_delete',
            method = 'POST',
            name = 'app_projects.collaborators_delete'
        ),
        #=========================================================================
        # ADD/EDIT MATERIAL
        routes.route(            
            regex = r'^(?P<id>[0-9]+)/material(?:/$|%s$)' % (templates.format),
            view = 'material',
            method = 'GET',
            name = 'app_projects.project_material'
        ),
        routes.route(            
            regex = r'^(?P<id>[0-9]+)/material(?:/$|%s$)' % (templates.format),
            view = 'material',
            method = 'POST',
            name = 'app_projects.project_material'
        ),
        #=========================================================================
        # FLICKR
        routes.route(            
            regex = r'^(?P<id>[0-9]+)/flickr/add(?:/$|%s$)' % (templates.format),
            view = 'flickr_add',
            method = 'GET',
            name = 'app_projects.flickr_add'
        ),
        routes.route(            
            regex = r'^(?P<id>[0-9]+)/flickr/add(?:/$|%s$)' % (templates.format),
            view = 'flickr_add',
            method = 'POST',
            name = 'app_projects.flickr_add'
        ),
        #=========================================================================
        # TUMBLR - TEXT
        routes.route(            
            regex = r'^(?P<id>[0-9]+)/tumblr/text(?:/$|%s$)' % (templates.format),
            view = 'tumblr_text',
            method = 'GET',
            name = 'app_projects.tumblr_text'
        ),
        routes.route(            
            regex = r'^(?P<id>[0-9]+)/tumblr/text(?:/$|%s$)' % (templates.format),
            view = 'tumblr_text',
            method = 'POST',
            name = 'app_projects.tumblr_text'
        ),
        # TUMBLR - LINK
        routes.route(            
            regex = r'^(?P<id>[0-9]+)/tumblr/link(?:/$|%s$)' % (templates.format),
            view = 'tumblr_link',
            method = 'GET',
            name = 'app_projects.tumblr_link'
        ),
        routes.route(            
            regex = r'^(?P<id>[0-9]+)/tumblr/link(?:/$|%s$)' % (templates.format),
            view = 'tumblr_link',
            method = 'POST',
            name = 'app_projects.tumblr_link'
        ),
        # TUMBLR - QUOTE
        routes.route(            
            regex = r'^(?P<id>[0-9]+)/tumblr/quote(?:/$|%s$)' % (templates.format),
            view = 'tumblr_quote',
            method = 'GET',
            name = 'app_projects.tumblr_quote'
        ),
        routes.route(            
            regex = r'^(?P<id>[0-9]+)/tumblr/quote(?:/$|%s$)' % (templates.format),
            view = 'tumblr_quote',
            method = 'POST',
            name = 'app_projects.tumblr_quote'
        ),
        # TUMBLR - CHAT
        routes.route(            
            regex = r'^(?P<id>[0-9]+)/tumblr/chat(?:/$|%s$)' % (templates.format),
            view = 'tumblr_chat',
            method = 'GET',
            name = 'app_projects.tumblr_chat'
        ),
        routes.route(            
            regex = r'^(?P<id>[0-9]+)/tumblr/chat(?:/$|%s$)' % (templates.format),
            view = 'tumblr_chat',
            method = 'POST',
            name = 'app_projects.tumblr_chat'
        ),
        # TUMBLR - PHOTO
        routes.route(            
            regex = r'^(?P<id>[0-9]+)/tumblr/photo(?:/$|%s$)' % (templates.format),
            view = 'tumblr_photo',
            method = 'GET',
            name = 'app_projects.tumblr_photo'
        ),
        routes.route(            
            regex = r'^(?P<id>[0-9]+)/tumblr/photo(?:/$|%s$)' % (templates.format),
            view = 'tumblr_photo',
            method = 'POST',
            name = 'app_projects.tumblr_photo'
        ),
        # TUMBLR - AUDIO
        routes.route(            
            regex = r'^(?P<id>[0-9]+)/tumblr/audio(?:/$|%s$)' % (templates.format),
            view = 'tumblr_audio',
            method = 'GET',
            name = 'app_projects.tumblr_audio'
        ),
        routes.route(            
            regex = r'^(?P<id>[0-9]+)/tumblr/audio(?:/$|%s$)' % (templates.format),
            view = 'tumblr_audio',
            method = 'POST',
            name = 'app_projects.tumblr_audio'
        ),
        # # TUMBLR - VIDEO
        # routes.route(            
        #     regex = r'^(?P<id>[0-9]+)/tumblr/video(?:/$|%s$)' % (templates.format),
        #     view = 'tumblr_video',
        #     method = 'GET',
        #     name = 'app_projects.tumblr_video'
        # ),
        # routes.route(            
        #     regex = r'^(?P<id>[0-9]+)/tumblr/video(?:/$|%s$)' % (templates.format),
        #     view = 'tumblr_video',
        #     method = 'POST',
        #     name = 'app_projects.tumblr_video'
        # ),

    ]
)
