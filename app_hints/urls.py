from respite.urls import resource, routes, templates
from app_hints.views import HintViews


urlpatterns = resource(
    prefix = 'hints/',
    views = HintViews,
    routes = [
        # MOST FREQUENT
        routes.route(
            regex = r'^(?:$|index%s$)' % (templates.format),
            view = 'hints_projects',
            method = 'GET',
            name = 'app_hints.hints_projects'
        ),

    ]
)
