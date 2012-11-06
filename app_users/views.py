from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.template import RequestContext

from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template

from respite import Views
from respite.decorators import rest_login_required
from respite.utils import generate_form

from app_users.decorators import must_be_itself
from app_users.models import UserProfile
from app_users.models_nn import CreativeFields
from app_users.forms import *
from app_projects.models import Project
from app_socialnetworks.oauthclient import NotConnectedException


#=========================================================================
# UserProfileViews
#=========================================================================
class UserProfileViews(Views):
    """
    UserProfile 
    

    :supported_formats: blablbabla
    :template: bbbba
    """
    supported_formats = ['html', 'json']
    template_path = 'app_users/'

    def _form_validation(self, request, form, status, messages=None):
        if form.is_valid():
            form.save()
            return self.show(request, request.user, messages)
        else:
            # Render the page
            return self._render(
                request = request,
                template = 'user_edit',
                context = {
                    'form': form,
            },
            status = status
        )


    def index(self, request):
        """
        List all users - FORBIDDEN 
        
        :param request: blablbabla

        .. note:: GET
        .. warning:: WARNING
        """
        return HttpResponseForbidden()

    def new(self, request):
        ''' Render form to create a new user - FORBIDDEN '''
        return HttpResponseForbidden()

    def create(self, request):
        ''' Create a new user - FORBIDDEN '''
        return HttpResponseForbidden()


    @rest_login_required
    def show(self, request, username, messages=None, errors=None):
        """
        Render the user with the specified username
        """
        u = get_object_or_404(UserProfile, user__username__iexact=username)

        # Filter users
        u_dict = u.wrapper()

        # Retrieve projects owned
        pj_own = u.get_projects_own_wrapper()
        
        # Retrieve projects in which collaborate
        pj_col = u.get_projects_collaborate_wrapper()

        # Check if the user is trying to see its personal profile
        if str(username) == str(request.user):
            itself = True
        else:
            itself = False

        
        # Render the page    
        return self._render(
            request = request,
            template = 'user_view',
            context = {
                'messages': messages,
                'errors': errors,
                'u': u_dict,
                'itself': itself,
                'projects_own': pj_own,
                'projects_collab': pj_col,
            },
            status = 200
        )

    @rest_login_required
    @must_be_itself
    def edit(self, request, username):
        ''' Render a form to edit a user '''

        # if str(username) != str(request.user):
        #     return self.show(request, request.user, errors=OPERATION_NOT_PERMITTED)

        u = UserProfile.objects.get(user__username__exact=username)

        if request.method == 'POST':
            form = UserProfileForm(request.POST, request.FILES, instance=u)
            return self._form_validation(request, form, 400, messages="Profile successfully edited!")
        else:
            # Form populated by default with user's data
            form = UserProfileForm(instance=u)
            return self._form_validation(request, form, 200)


    @rest_login_required
    @must_be_itself
    def replace(self, request, username):
        # if str(username) != str(request.user):
        #     return self.show(request, request.user, errors=OPERATION_NOT_PERMITTED)

        u = UserProfile.objects.get(user__username__iexact=username)
        form = UserProfileForm(request.PUT, instance=u)

        return self._form_validation(request, form, 400, messages="Profile replaced")

    
    @rest_login_required
    @must_be_itself
    def update(self, request, username):
        # if str(username) != str(request.user):
        #     return self.show(request, request.user, errors=OPERATION_NOT_PERMITTED)

        u = UserProfile.objects.get(user__username__iexact=username)
        fields = []
        for field in request.PATCH:
            try:
                UserProfile._meta.get_field_by_name(field)
                fields.append(field)
            except FieldDoesNotExist:
                continue

        Form = generate_form(model = UserProfile, form = UserProfileForm, fields = fields)
        form = Form(request.PATCH, instance=u)

        return self._form_validation(request, form, 400, messages="Profile updated")



    @rest_login_required
    @must_be_itself
    def destroy(self, request, username):
        ''' Delete an user '''

        u = UserProfile.objects.get(user__username__exact=username)

        # Delete connected data
        u.delete_connected_data()
        
        # Delete UserProfile
        u.delete()

        # Redirect to homepage
        return HttpResponseRedirect("/")


    #=========================================================================
    # SETTINGS
    #=========================================================================
    @rest_login_required
    @must_be_itself
    def settings(self, request, username, messages=None):
        # if str(username) != str(request.user):
        #     return self.show(request, request.user, errors=OPERATION_NOT_PERMITTED)

        u = UserProfile.objects.get(user__username__iexact=username)
        u_dict = u.wrapper()

        # Check if is a custom user or only a social login
        if str(u.user.password) != "!":
            custom = True
        else:
            custom = False

        # Render the page    
        return self._render(
            request = request,
            template = 'user_settings',
            context = {
                'messages': messages,
                'u': u_dict,
                'custom': custom,
                'itself': True,
            },
            status = 200
        )

    @rest_login_required
    @must_be_itself
    def settings_edit(self, request, username):
        # if str(username) != str(request.user):
        #     return self.show(request, request.user, errors=OPERATION_NOT_PERMITTED)

        u = UserProfile.objects.get(user__username__exact=username)

        if request.method == 'POST':
            # Form populated request's data
            form = UserAuthForm(request.POST, instance=u.user)
            if form.is_valid():
                # Update model
                form.save()

                # Redirect to user profile settings
                return self.settings(request, request.user, messages="Email successfully updated!")
        else:
            # Form populated by default with user's data
            form = UserAuthForm(instance=u.user)

        # Render the page    
        return self._render(
            request = request,
            template = 'user_settings_edit',
            context = {
                'form': form,
            },
            status = 200
        )

    #=========================================================================
    # VOTED
    #=========================================================================
    @rest_login_required
    def voted(self, request, username):
        # Retrieve users
        u = get_object_or_404(UserProfile, user__username__iexact=username)
        u_dict = u.wrapper()

        # Retrieve voted projects
        projects = u.get_projects_voted()

        #TODO

        # Check if the user is trying to see its personal profile
        if str(username) == str(request.user):
            itself = True
        else:
            itself = False

        # Render the page    
        return self._render(
            request = request,
            template = 'user_voted',
            context = {
                'u': u_dict,
                'itself': itself,
                'project_list': projects,
            },
            status = 200,
        )


    #=========================================================================
    # CREATIVE FIELDS
    #=========================================================================
    @rest_login_required
    @must_be_itself
    def creative_fields_manage(self, request, username, field_id=None, errors=None):
        u = UserProfile.objects.get(user__username__exact=username)

        # Add Creative Field
        if 'creative-add' in request.POST:
            if request.method == 'POST':
                form = CreativeFieldsAddForm(request.POST, user_filter=u)
                if form.is_valid():
                    new_field = form.cleaned_data['creative_field']
                    cf = CreativeFields(userprofile=u, creative_field=new_field)
                    cf.save()

                    # Redirect the user
                    return self.show(request, username, messages="Creative Field Added!")
        # Delete Creative Field
        else:
            # Instantiate a new form for adding fields anyway
            form = CreativeFieldsAddForm(user_filter=u)

            # Delete Field
            if field_id != None:
                u.delete_creative_field(field_id)


        # Render the page
        return self._render(
            request = request,
            template = 'user_creative_fields',
            context = {
                'errors': errors,
                'u': u.wrapper(),
                'form': form
            },
            status = 200
        )


    @rest_login_required
    @must_be_itself
    def creative_fields_delete(self, request, username, field_id):
        u = UserProfile.objects.get(user__username__exact=username)

        # Check that the field is selected
        creative_fields = u.get_creative_fields()
        if field_id in [x['id'] for x in creative_fields]:
            return self.creative_fields_manage(request, username, field_id=field_id)
        else:
            return self.creative_fields_manage(request, username, errors="That field wasn't selected")



    #=========================================================================
    # EMPLOYMENT
    #=========================================================================
    @rest_login_required
    @must_be_itself
    def employment_manage(self, request, username):
        u = UserProfile.objects.get(user__username__exact=username)

        # Try to fetch the related material
        try:
            employment = u.get_employment()
        except:
            employment = None


        # Check if is connected to linkedin
        connected_accounts = u.get_connected_accounts()
        linkedin = True if 'linkedin' in connected_accounts['names'] else False


        if request.method == 'POST':
            form = EmploymentForm(request.POST, instance=employment)

            if form.is_valid():
                new_employment = form.save(commit=False)

                # Save the new instance
                new_employment.save()

                # Bind it to the user
                u.employment = new_employment
                u.save()

                # Redirect to profile
                return self.show(request, username, "Employment Details successfully edited!")

            else:
                status = 400

        else:
            form   = EmploymentForm(instance=employment)
            status = 200

        # Render page
        return self._render(
            request = request,
            template = 'user_employment',
            context = {
                'linkedin': linkedin,
                'form': form,
            },
            status = status,
        )


    @rest_login_required
    @must_be_itself
    def employment_linkedin(self, request, username):
        u = UserProfile.objects.get(user__username__exact=username)

        # Query linkedin to update data
        try:
            u.get_linkedin_employment()
        except NotConnectedException:
            return self.show(request, username, errors="Not Connected to LinkedIn")
        except Exception:
            return self.show(request, username, errors="Something went wrong. Please retry.")

        
        # Redirect to profile
        return self.show(request, username, "Employment Details successfully imported")

