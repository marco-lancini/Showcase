import urlparse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.db.models import Count

from respite import Views
from respite.decorators import rest_login_required
from respite.utils import generate_form

from app_collaborations.options import CATEGORIES, get_category_verbose
from app_users.models import UserProfile
from app_projects.decorators import must_be_owner, no_conflict_of_interests
from app_projects.forms import *
from app_projects.models import Material, Project
from app_projects.models_nn import Votes, Collaborations

from app_socialnetworks.oauthclient import NotConnectedException, UploadException, ClearanceException
        


#=========================================================================
# ProjectViews
#=========================================================================
class ProjectViews(Views):
    """
    Project View

    :supported_formats: blablbabla
    :template_path: bbbba
    """
    supported_formats = ['html', 'json']
    template_path     = 'app_projects/'

    def _form_validation(self, request, form, status, type_op, messages=None):
        if form.is_valid():
            # Create, but don't save the new instance
            new_project = form.save(commit=False)

            # Bind it to the user
            username = str(request.user)
            u = UserProfile.objects.get(user__username__iexact=username)
            new_project.owner = u

            # Save the new instance
            new_project.save()

            # Redirect to the new project
            return self.show(request, new_project.id, messages)
        else:
            return self._render(
                request = request,
                template = 'project_new',
                context = {
                    'form': form,
                    'type': type_op,
                },
                status = status
            )


    def index(self, request, projects_set=None, title=None, messages=None):
        if projects_set == None:
            projects_set = Project.objects.all()

        if projects_set == False:
            projects = None
        else:
            projects = [x.wrapper() for x in projects_set]

        if title == None:
            title = "All Projects"

        return self._render(
            request = request,
            template = 'project_list',
            context = {
                'messages': messages,
                'title': title,
                'project_list': projects
            },
            status = 200
        )

    @rest_login_required
    def new(self, request):
        """
        Render the form for create a new project
        GET
        """
        form = ProjectForm()
        
        return self._form_validation(request, form, 200, "Create")


    @rest_login_required
    def create(self, request):
        """
        Receive data from the form of :view:`new` (or via API call) and create the new project
        POST
        """
        form = ProjectForm(request.POST)
        return self._form_validation(request, form, 400, "Create", messages="Project Created!")




    #=========================================================================
    # SHOW
    #=========================================================================
    def show(self, request, id, messages=None, errors=None):
        # Retrieve project
        p = get_object_or_404(Project, pk=id)
        p_dict = p.wrapper()
        
        # Check Owner
        if str(p.owner.user.username) == str(request.user):
            is_owner = True
        else:
            is_owner = False


        # Check Collaborators
        collaborators = p.get_collaborators_wrapper()
        if str(request.user) in [x['username'] for x in collaborators]:
            is_collaborator = True
        else:
            is_collaborator = False


        # Check if can vote/unvote
        try:
            username = str(request.user)
            u = UserProfile.objects.get(user__username__iexact=username)
            if p.can_vote(u):
                can_vote   = True
                can_unvote = False
            else:
                can_vote   = False
                can_unvote = True
        except:
            can_vote   = False
            can_unvote = False

        # Gather privileges
        privileges = {
            'is_owner': is_owner,
            'is_collaborator': is_collaborator,
            'can_vote': can_vote,
            'can_unvote': can_unvote
        }

        # Material
        material_extended = p.get_material_extended()


        # Render the page
        return self._render(
            request = request,
            template = 'project_view',
            context = {
                'messages': messages,
                'errors': errors,
                'p': p_dict,
                'material': material_extended,
                'privileges': privileges,
            },
            status = 200
        )
    #=========================================================================



    
    @rest_login_required
    @must_be_owner
    def edit(self, request, id, p):
        # Create form
        if request.method == 'POST':
            form   = ProjectForm(request.POST, instance=p)
            status = 400
        else:
            form   = ProjectForm(instance=p)
            status = 200

        return self._form_validation(request, form, status, "Edit", messages="Project successfully edited!")
            


    @rest_login_required
    @must_be_owner
    def replace(self, request, id, p):
        # Create form
        form = ProjectForm(request.PUT, instance=p)

        return self._form_validation(request, form, 400, "Replace", messages="Project replaced")

    
    @rest_login_required
    @must_be_owner
    def update(self, request, id, p):
        # Create form
        fields = []
        for field in request.PATCH:
            try:
                Project._meta.get_field_by_name(field)
                fields.append(field)
            except FieldDoesNotExist:
                continue

        Form = generate_form(model = Project, form = ProjectForm, fields = fields)
        form = Form(request.PATCH, instance=p)

        return self._form_validation(request, form, 400, "Update", messages="Project updated")


    @rest_login_required
    @must_be_owner
    def destroy(self, request, id, p):
        # Delete connected data
        p.delete_connected_data()

        # Delete Project
        p.delete()

        # Redirect to project index
        return self.index(request, messages="Project Deleted")


    #=========================================================================
    # VOTES
    #=========================================================================
    @rest_login_required
    @no_conflict_of_interests
    def vote(self, request, id, p):
        # Retrieve user
        username = str(request.user)
        u = UserProfile.objects.get(user__username__iexact=username)

        # Check that can vote (must not have voted before)
        if not p.can_vote(u):
            return self.show(request, id, errors="You can vote only one time")

        # Create a new vote
        p.vote(u)

        return self.show(request, id, messages="Thanks for voting")


    @rest_login_required
    @no_conflict_of_interests
    def unvote(self, request, id, p):
        # Retrieve user
        username = str(request.user)
        u = UserProfile.objects.get(user__username__iexact=username)

        # Check that can unvote (must have voted before)
        if not p.can_unvote(u):
            return self.show(request, id, errors="You can't unvote")

        # Delete the vote
        p.unvote(u)
    
        return self.show(request, id, messages="Vote removed")


    #=========================================================================
    # LIST BY
    #=========================================================================
    def list_by_category(self, request, category):
        
        # Retrieve all the projects belonging to the category specified
        projects_set = Project.objects.filter(category=category)

        # Check if the category has at least one project
        if projects_set.count() > 0:
            # Retrieve the title from the first project
            title = projects_set[0].get_category_verbose()
        else:
            title = get_category_verbose(category)
            projects_set = False

        return self.index(request, projects_set=projects_set, title=title, messages=None)


    def browse_by_category(self, request):
        # Retrieve Categories
        categories = [{'id': x[0], 'name': x[1]} for x in CATEGORIES]

        # Render the page
        return self._render(
            request = request,
            template = 'project_browse',
            context = {
                'categories': categories
            },
            status = 200
        )


    def list_by_votes(self, request, min_votes, max_votes):

        # Create the title
        title = "Votes %s - %s" % (min_votes, max_votes)

        # Calculate boundary
        min_votes = int(min_votes) - 1 
        max_votes = int(max_votes) + 1

        # Get all projects
        all_projects = Project.objects.all()

        # Filter projects belonging to the range of votes
        projects_set = []
        for pj in all_projects:
            v = Votes.objects.filter(project=pj).count()
            if v > min_votes and v < max_votes:
                projects_set.append(pj)       

        return self.index(request, projects_set=projects_set, title=title, messages=None)


    def browse_by_votes(self, request):

        # Retrieve Categories
        categories = [
            {'min': 1, 'max': 10},
            {'min': 10, 'max': 50},
            {'min': 50, 'max': 100},
            {'min': 100, 'max': 1000}
        ]

        # Render the page
        return self._render(
            request = request,
            template = 'project_browse',
            context = {
                'categories': categories
            },
            status = 200
        )


    #=========================================================================
    # COLLABORATORS
    #=========================================================================
    @rest_login_required
    @must_be_owner
    def collaborators_manage(self, request, id, p, coll=None, errors=None):
        # Add Collaborator
        if 'collaborator-add' in request.POST:
            if request.method == 'POST':
                form = CollaboratorsAddForm(request.POST, initial={'project': p}, pj_filter=p)
                if form.is_valid():
                    collaborator = form.cleaned_data['collaborators']
                    c = Collaborations(userprofile=collaborator, project=p)
                    c.save()

                    # Redirect the user
                    return self.show(request, id, messages="Collaborator Added")
        # Delete Collaborator
        else:
            # Instantiate a new form for adding collaborators anyway
            form = CollaboratorsAddForm(initial={'project': p}, pj_filter=p)

            # Delete Collaboration
            if coll != None:
                p.delete_collaborator(coll)


        # Already active collaborations
        collaborators = p.get_collaborators_wrapper()


        # Render the page
        return self._render(
            request = request,
            template = 'project_collaborators',
            context = {
                'errors': errors,
                'p': p.wrapper(),
                'collaborators': collaborators,
                'form': form
            },
            status = 200
        )


    @rest_login_required
    @must_be_owner
    def collaborators_delete(self, request, id, p, username):
        # Check that username is a collaborator
        username = str(username)
        collaborators = p.get_collaborators_wrapper()
        if username in [x['username'] for x in collaborators]:
            return self.collaborators_manage(request, id, coll=username)
        else:
            return self.collaborators_manage(request, id, errors="That user is not a collaborator")


    #=========================================================================
    # MATERIAL
    #=========================================================================
    @rest_login_required
    @must_be_owner
    def material(self, request, id, p):
        # Try to fetch the related material
        try:
            material = p.get_material()
        except:
            material = None


        if request.method == 'POST':
            form = MaterialForm(request.POST, instance=material)

            if form.is_valid():
                new_material = form.save(commit=False)

                # Save the new instance
                new_material.save()

                # Bind it to the project
                p.material = new_material
                p.save()

                # Redirect to the new project
                return self.show(request, id, "Material successfully edited!")

            else:
                status = 400

        else:
            form   = MaterialForm(instance=material)
            status = 200

        # Render page
        return self._render(
            request = request,
            template = 'form_simple',
            context = {
                'param_title': p.title,
                'param_subtitle': "Manage Material",
                'param_media': False,
                'url_confirm': reverse('app_projects.project_material', args=[p.id]),
                'url_cancel': reverse('app_projects.project_view', args=[p.id]),
                'form': form,
            },
            status = status,
            prefix_template_path = False
        )


    #=========================================================================
    # FLICKR
    #=========================================================================
    @rest_login_required
    @must_be_owner
    def flickr_add(self, request, id, p):
        material_dict = p.get_material_wrapper()

        # Check if this project is connected to a Flickr Photoset
        if not material_dict['flickr']:
            return self.show(request, id, errors='You have to connect a Flickr Photoset in order to complete this action. Click on "Manage Material" to link one of your Photosets to this project.')


        if request.method == 'POST':
            form = FlickrForm(request.POST, request.FILES)

            if form.is_valid():
                new_title       = form.cleaned_data['title']
                new_description = form.cleaned_data['description']
                new_photo       = form.cleaned_data['image']
                
                # Upload photo to flickr
                try:
                    p.material.flickr_add_photo(request.user, new_title, new_description, new_photo)
                except UploadException:
                    return self.show(request, id, errors="Something went wrong. Please, retry")
                except ClearanceException:
                    return self.show(request, id, errors="Photoset not found. Are you sure you are the owner of the linked photoset?")
                except Exception:
                    return self.show(request, id, errors="Something went wrong. Please, retry")


                # Redirect to the project
                return self.show(request, id, messages="Photo added!")

            else:
                status = 400

        else:
            form   = FlickrForm()
            status = 200


        # Render page
        return self._render(
            request = request,
            template = 'form_simple',
            context = {
                'param_title': p.title,
                'param_subtitle': "Add Flickr Photo",
                'param_media': True,
                'url_confirm': reverse('app_projects.flickr_add', args=[p.id]),
                'url_cancel': reverse('app_projects.project_view', args=[p.id]),
                'form': form,
            },
            status = status,
            prefix_template_path = False
        )



    #=========================================================================
    # TUMBLR
    #=========================================================================
    @rest_login_required
    @must_be_owner
    def tumblr_text(self, request, id, p):
        material_dict = p.get_material_wrapper()

        # Check if this project is connected to a Tumblt blog
        if not material_dict['tumblr']:
            return self.show(request, id, errors='You have to connect a Tumblr Blog in order to complete this action. Click on "Manage Material" to link your blog to this project.')


        if request.method == 'POST':
            form = Tumblr_TextForm(request.POST)

            if form.is_valid():
                new_title = form.cleaned_data['title']
                new_body  = form.cleaned_data['body']
                
                try:
                    p.material.tumblr_add_text(request.user, new_title, new_body)
                except UploadException:
                    return self.show(request, id, errors="Something went wrong. Please, retry")
                except ClearanceException:
                    return self.show(request, id, errors="You can't modify a blog you don't own.")
                except Exception:
                    return self.show(request, id, errors="Something went wrong. Please, retry")

                # Redirect to the project
                return self.show(request, id, messages="Post added!")

            else:
                status = 400

        else:
            form   = Tumblr_TextForm()
            status = 200


        # Render page
        return self._render(
            request = request,
            template = 'form_simple',
            context = {
                'param_title': p.title,
                'param_subtitle': "Add Tumblr Blog",
                'param_media': False,
                'url_confirm': reverse('app_projects.tumblr_text', args=[p.id]),
                'url_cancel': reverse('app_projects.project_view', args=[p.id]),
                'form': form,
            },
            status = status,
            prefix_template_path = False
        )



    @rest_login_required
    @must_be_owner
    def tumblr_link(self, request, id, p):
        material_dict = p.get_material_wrapper()

        # Check if this project is connected to a Tumblt blog
        if not material_dict['tumblr']:
            return self.show(request, id, errors='You have to connect a Tumblr Blog in order to complete this action. Click on "Manage Material" to link your blog to this project.')


        if request.method == 'POST':
            form = Tumblr_LinkForm(request.POST)

            if form.is_valid():
                new_title = form.cleaned_data['title']
                new_url   = form.cleaned_data['url']
                
                try:
                    p.material.tumblr_add_link(request.user, new_title, new_url)
                except UploadException:
                    return self.show(request, id, errors="Something went wrong. Please, retry")
                except ClearanceException:
                    return self.show(request, id, errors="You can't modify a blog you don't own.")
                except Exception:
                    return self.show(request, id, errors="Something went wrong. Please, retry")

                # Redirect to the project
                return self.show(request, id, messages="Post added!")

            else:
                status = 400

        else:
            form   = Tumblr_LinkForm()
            status = 200


        # Render page
        return self._render(
            request = request,
            template = 'form_simple',
            context = {
                'param_title': p.title,
                'param_subtitle': "Add Tumblr Blog",
                'param_media': False,
                'url_confirm': reverse('app_projects.tumblr_link', args=[p.id]),
                'url_cancel': reverse('app_projects.project_view', args=[p.id]),
                'form': form,
            },
            status = status,
            prefix_template_path = False
        )



    @rest_login_required
    @must_be_owner
    def tumblr_quote(self, request, id, p):
        material_dict = p.get_material_wrapper()

        # Check if this project is connected to a Tumblt blog
        if not material_dict['tumblr']:
            return self.show(request, id, errors='You have to connect a Tumblr Blog in order to complete this action. Click on "Manage Material" to link your blog to this project.')


        if request.method == 'POST':
            form = Tumblr_QuoteForm(request.POST)

            if form.is_valid():
                new_quote = form.cleaned_data['quote']
                
                try:
                    p.material.tumblr_add_quote(request.user, new_quote)
                except UploadException:
                    return self.show(request, id, errors="Something went wrong. Please, retry")
                except ClearanceException:
                    return self.show(request, id, errors="You can't modify a blog you don't own.")
                except Exception:
                    return self.show(request, id, errors="Something went wrong. Please, retry")

                # Redirect to the project
                return self.show(request, id, messages="Post added!")

            else:
                status = 400

        else:
            form   = Tumblr_QuoteForm()
            status = 200


        # Render page
        return self._render(
            request = request,
            template = 'form_simple',
            context = {
                'param_title': p.title,
                'param_subtitle': "Add Tumblr Blog",
                'param_media': False,
                'url_confirm': reverse('app_projects.tumblr_quote', args=[p.id]),
                'url_cancel': reverse('app_projects.project_view', args=[p.id]),
                'form': form,
            },
            status = status,
            prefix_template_path = False
        )


    @rest_login_required
    @must_be_owner
    def tumblr_chat(self, request, id, p):
        material_dict = p.get_material_wrapper()

        # Check if this project is connected to a Tumblt blog
        if not material_dict['tumblr']:
            return self.show(request, id, errors='You have to connect a Tumblr Blog in order to complete this action. Click on "Manage Material" to link your blog to this project.')


        if request.method == 'POST':
            form = Tumblr_ChatForm(request.POST)

            if form.is_valid():
                new_title        = form.cleaned_data['title']
                new_conversation = form.cleaned_data['conversation']
                
                try:
                    p.material.tumblr_add_chat(request.user, new_title, new_conversation)
                except UploadException:
                    return self.show(request, id, errors="Something went wrong. Please, retry")
                except ClearanceException:
                    return self.show(request, id, errors="You can't modify a blog you don't own.")
                except Exception:
                    return self.show(request, id, errors="Something went wrong. Please, retry")

                # Redirect to the project
                return self.show(request, id, messages="Post added!")

            else:
                status = 400

        else:
            form   = Tumblr_ChatForm()
            status = 200


        # Render page
        return self._render(
            request = request,
            template = 'form_simple',
            context = {
                'param_title': p.title,
                'param_subtitle': "Add Tumblr Blog",
                'param_media': False,
                'url_confirm': reverse('app_projects.tumblr_chat', args=[p.id]),
                'url_cancel': reverse('app_projects.project_view', args=[p.id]),
                'form': form,
            },
            status = status,
            prefix_template_path = False
        )



    @rest_login_required
    @must_be_owner
    def tumblr_photo(self, request, id, p):
        material_dict = p.get_material_wrapper()

        # Check if this project is connected to a Tumblt blog
        if not material_dict['tumblr']:
            return self.show(request, id, errors='You have to connect a Tumblr Blog in order to complete this action. Click on "Manage Material" to link your blog to this project.')


        if request.method == 'POST':
            form = Tumblr_PhotoForm(request.POST, request.FILES)

            if form.is_valid():
                new_source  = form.cleaned_data['source']
                new_data    = form.cleaned_data['data']
                
                try:
                    p.material.tumblr_add_photo(request.user, new_source, new_data)
                except UploadException:
                    return self.show(request, id, errors="Something went wrong. Please, retry")
                except ClearanceException:
                    return self.show(request, id, errors="You can't modify a blog you don't own.")
                except Exception:
                    return self.show(request, id, errors="Something went wrong. Please, retry")

                # Redirect to the project
                return self.show(request, id, messages="Post added!")

            else:
                status = 400

        else:
            form   = Tumblr_PhotoForm()
            status = 200


        # Render page
        return self._render(
            request = request,
            template = 'form_simple',
            context = {
                'param_title': p.title,
                'param_subtitle': "Add Tumblr Blog",
                'param_media': True,
                'url_confirm': reverse('app_projects.tumblr_photo', args=[p.id]),
                'url_cancel': reverse('app_projects.project_view', args=[p.id]),
                'form': form,
            },
            status = status,
            prefix_template_path = False
        )


    @rest_login_required
    @must_be_owner
    def tumblr_audio(self, request, id, p):
        material_dict = p.get_material_wrapper()

        # Check if this project is connected to a Tumblt blog
        if not material_dict['tumblr']:
            return self.show(request, id, errors='You have to connect a Tumblr Blog in order to complete this action. Click on "Manage Material" to link your blog to this project.')


        if request.method == 'POST':
            form = Tumblr_AudioForm(request.POST, request.FILES)

            if form.is_valid():
                new_source  = form.cleaned_data['source']
                
                try:
                    p.material.tumblr_add_audio(request.user, new_source)
                except UploadException:
                    return self.show(request, id, errors="Something went wrong. Please, retry")
                except ClearanceException:
                    return self.show(request, id, errors="You can't modify a blog you don't own.")
                except Exception:
                    return self.show(request, id, errors="Something went wrong. Please, retry")

                # Redirect to the project
                return self.show(request, id, messages="Post added!")

            else:
                status = 400

        else:
            form   = Tumblr_AudioForm()
            status = 200


        # Render page
        return self._render(
            request = request,
            template = 'form_simple',
            context = {
                'param_title': p.title,
                'param_subtitle': "Add Tumblr Blog",
                'param_media': True,
                'url_confirm': reverse('app_projects.tumblr_audio', args=[p.id]),
                'url_cancel': reverse('app_projects.project_view', args=[p.id]),
                'form': form,
            },
            status = status,
            prefix_template_path = False
        )


    # @rest_login_required
    # @must_be_owner
    # def tumblr_video(self, request, id, p):
    #     material_dict = p.get_material_wrapper()

    #     # Check if this project is connected to a Tumblt blog
    #     if not material_dict['tumblr']:
    #         return self.show(request, id, errors='You have to connect a Tumblr Blog in order to complete this action. Click on "Manage Material" to link your blog to this project.')


    #     if request.method == 'POST':
    #         form = Tumblr_VideoForm(request.POST, request.FILES)

    #         if form.is_valid():
    #             new_data    = form.cleaned_data['data']
                
    #             #try:
    #             p.material.tumblr_add_video(request.user, new_data)
    #             # except UploadException:
    #             #     return self.show(request, id, errors="Something went wrong. Please, retry")
    #             # except ClearanceException:
    #             #     return self.show(request, id, errors="You can't modify a blog you don't own.")
    #             # except Exception:
    #             #     return self.show(request, id, errors="Something went wrong. Please, retry")

    #             # Redirect to the project
    #             return self.show(request, id, messages="Post added!")

    #         else:
    #             status = 400

    #     else:
    #         form   = Tumblr_VideoForm()
    #         status = 200


    #     # Render page
    #     return self._render(
    #         request = request,
    #         template = 'form_simple',
    #         context = {
    #             'param_title': p.title,
    #             'param_subtitle': "Add Tumblr Blog",
    #             'param_media': True,
    #             'url_confirm': reverse('app_projects.tumblr_video', args=[p.id]),
    #             'url_cancel': reverse('app_projects.project_view', args=[p.id]),
    #             'form': form,
    #         },
    #         status = status,
    #         prefix_template_path = False
    #     )
