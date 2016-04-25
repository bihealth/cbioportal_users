from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView

from . import portal_models
from . import forms

import datetime


class Index(LoginRequiredMixin, TemplateView):
    """Show dashboard index"""
    template_name = 'usermgmt/index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['num_users'] = portal_models.DaoUser.num_users()
        context['num_studies'] = portal_models.DaoStudy.num_studies()
        context['num_study_groups'] = portal_models.DaoStudyGroup.num_groups()
        return context


class UserCreate(LoginRequiredMixin, FormView, TemplateView):
    """Handle creation of users"""
    template_name = 'usermgmt/user_create.html'
    form_class = forms.CreateUserForm

    def get_initial(self):
        return {'enabled': True}

    def form_valid(self, form):
        email = form.cleaned_data['email']
        # TODO(holtgrewe): add this into a transaction, otherwise we can get duplicate users!
        if portal_models.DaoUser.user_exists(email):
            raise Exception('User already exists!')
        portal_models.DaoUser.create_user(
            form.cleaned_data['email'],
            form.cleaned_data['name'],
            form.cleaned_data['enabled'])
        return redirect('user_view', email=email)


class UserStudyAccess(LoginRequiredMixin, FormView, TemplateView):
    """Handle study access assignment"""
    template_name = 'usermgmt/user_access.html'
    form_class = forms.UserAccessForm

    def get_initial(self):
        return {'authorities': [
            a.authority for a in portal_models.DaoAuthority.for_user(
                self.kwargs['email'])]}

    def get_context_data(self, email, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = portal_models.DaoUser.get_user(email)
        return context

    def form_valid(self, form):
        email = self.kwargs['email']
        # TODO(holtgrewe): add this into a transaction
        if not portal_models.DaoUser.user_exists(email):
            raise Exception('No such user found!')
        portal_models.DaoAuthority.update_authorities_for_user(
            email,
            form.cleaned_data['authorities'])
        return redirect('user_view', email=email)


class UserUpdate(LoginRequiredMixin, FormView, TemplateView):
    """Handle update of users"""
    template_name = 'usermgmt/user_update.html'
    form_class = forms.UpdateUserForm

    def get_initial(self):
        return portal_models.DaoUser.get_user(self.kwargs.get('email')).to_dict()

    def get_context_data(self, email, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = portal_models.DaoUser.get_user(email)
        return context

    def form_valid(self, form):
        email = self.kwargs['email']
        # TODO(holtgrewe): add this into a transaction
        if not portal_models.DaoUser.user_exists(email):
            raise Exception('No such user found!')
        portal_models.DaoUser.update_user(
            email,
            form.cleaned_data['name'],
            form.cleaned_data['enabled'])
        return redirect('user_view', email=email)


class UserList(TemplateView):
    template_name = 'usermgmt/user_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = portal_models.DaoUser.all_users()
        return context


class UserView(LoginRequiredMixin, TemplateView):
    template_name = 'usermgmt/user_view.html'

    def get_context_data(self, email, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = portal_models.DaoUser.get_user(email)
        context['authorities'] = portal_models.DaoAuthority.for_user(email)
        return context


class UserDelete(LoginRequiredMixin, TemplateView):
    template_name = 'usermgmt/user_delete.html'

    def get_context_data(self, email, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = portal_models.DaoUser.get_user(email)
        return context

    def post(self, request, *args, **kwargs):
        portal_models.DaoUser.delete_user(self.kwargs['email'])
        return redirect('user_list')


class StudyList(LoginRequiredMixin, TemplateView):
    template_name = 'usermgmt/study_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['studies'] = portal_models.DaoStudy.all_studies()
        return context


class StudyView(LoginRequiredMixin, TemplateView):
    template_name = 'usermgmt/study_view.html'

    def get_context_data(self, identifier, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        study = portal_models.DaoStudy.get(identifier)
        context['study'] = study
        context['direct_users'] = portal_models.DaoUser.with_direct_access_to(identifier)
        context['all_users'] = portal_models.DaoUser.with_direct_access_to('ALL')
        context['num_group_users'] = 0
        context['group_users'] = []
        for group in study.groups:
            context['group_users'].append(
                (group, portal_models.DaoUser.with_direct_access_to(group)))
            context['num_group_users'] += len(context['group_users'][-1][-1])
        return context


class StudyUsers(LoginRequiredMixin, FormView, TemplateView):
    """Handle study access assignment"""
    template_name = 'usermgmt/user_access.html'
    form_class = forms.StudyUsersForm

    def get_initial(self):
        return {'users': [
            u.email for u in portal_models.DaoUser.with_direct_access_to(
                self.kwargs['identifier'])]}

    def get_context_data(self, identifier, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['study'] = portal_models.DaoStudy.get(identifier)
        return context

    def form_valid(self, form):
        identifier = self.kwargs['identifier']
        # TODO(holtgrewe): add this into a transaction
        if not portal_models.DaoStudy.exists(identifier):
            raise Exception('No such study found!')
        portal_models.DaoAuthority.update_authorities_for_study(
            identifier,
            form.cleaned_data['users'])
        return redirect('study_view', identifier=identifier)


class GroupList(LoginRequiredMixin, TemplateView):
    template_name = 'usermgmt/group_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = portal_models.DaoStudyGroup.all_groups()
        return context


class GroupView(LoginRequiredMixin, TemplateView):
    template_name = 'usermgmt/group_view.html'

    def get_context_data(self, name, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        group = portal_models.DaoStudyGroup.get(name)
        context['group'] = group
        context['direct_users'] = portal_models.DaoUser.with_direct_access_to(name)
        return context


class GroupUsers(LoginRequiredMixin, FormView, TemplateView):
    """Handle group access assignment"""
    # TODO: rename to group_users?
    template_name = 'usermgmt/group_access.html'
    form_class = forms.GroupUsersForm

    def get_initial(self):
        return {'users': [
            u.email for u in portal_models.DaoUser.with_direct_access_to(
                self.kwargs['name'])]}

    def get_context_data(self, name, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = portal_models.DaoStudyGroup.get(name)
        return context

    def form_valid(self, form):
        name = self.kwargs['name']
        # TODO(holtgrewe): add this into a transaction
        if not portal_models.DaoStudyGroup.exists(name):
            raise Exception('No such group found!')
        portal_models.DaoAuthority.update_authorities_for_group(
            name,
            form.cleaned_data['users'])
        return redirect('group_view', name=name)


class Export(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        result = ['users:']
        for user in portal_models.DaoUser.all_users():
            result += [
                '- email: {}'.format(repr(user.email)),
                '  name: {}'.format(repr(user.name)),
                '  enabled: {}'.format(int(user.enabled)),
            ]
        result += ['', 'authorities:']
        for authority in portal_models.DaoAuthority.all_authorities():
            result += [
                '- email: {}'.format(repr(authority.email)),
                '  authority: {}'.format(repr(authority.authority)),
            ]
        response = HttpResponse('\n'.join(result), content_type='text/plain')
        fname = datetime.datetime.now().strftime('%Y-%m-%d_%H-%m-%s_cbioportal_users.yaml')
        res['Content-Disposition'] = 'inline; filename={}'.format(fname)
        return response


class Export(LoginRequiredMixin, TemplateView):
    template_name = 'usermgmt/import.html'

    def get(self, *args, **kwargs):
        result = ['users:']
        for user in portal_models.DaoUser.all_users():
            result += [
                '- email: {}'.format(repr(user.email)),
                '  name: {}'.format(repr(user.name)),
                '  enabled: {}'.format(int(user.enabled)),
            ]
        result += ['', 'authorities:']
        for authority in portal_models.DaoAuthority.all_authorities():
            result += [
                '- email: {}'.format(repr(authority.email)),
                '  authority: {}'.format(repr(authority.authority)),
            ]
        response = HttpResponse('\n'.join(result), content_type='text/plain')
        fname = datetime.datetime.now().strftime('%Y-%m-%d_%H-%m-%s_cbioportal_users.yaml')
        response['Content-Disposition'] = 'attachment; filename={}'.format(fname)
        return response


class Import(LoginRequiredMixin, TemplateView):
    template_name = 'usermgmt/import.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = forms.ImportForm()
        return context

    def post(self, request, *args, **kwargs):
        form = forms.ImportForm(request.POST, request.FILES)
        if not form.is_valid():
            return self.render_to_response(
                self.get_context_data(*args, **kwargs))
        try:
            portal_models.import_from_yaml(request.FILES['file'].read())
        except Exception as e:
            print(e) # XXX
            context = self.get_context_data(*args, **kwargs)
            context['form'].add_error('file', 'Invalid YAML!')
            return self.render_to_response(context)
        return redirect('index')
