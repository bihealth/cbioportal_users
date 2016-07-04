from django import forms
from django.utils.functional import lazy

from . import portal_models


class AuthoritiesChoiceField(forms.MultipleChoiceField):

    def __init__(self, *args, **kwargs):
        kwargs['choices'] = lazy(AuthoritiesChoiceField.get_choices)
        super().__init__(*args, **kwargs)

    @classmethod
    def get_choices(klass):
        result = [('ALL', 'ALL [special] -- Access to all studies!')]
        for study in portal_models.DaoStudy.all_studies():
            result.append((study.identifier.upper(),
                           '{} [study] ({})'.format(study.identifier, study.name)))
        for group in portal_models.DaoStudyGroup.all_groups():
            result.append((group.name.upper(), '{} [group]'.format(group.name)))
        return result


class UserAccessForm(forms.Form):
    authorities = AuthoritiesChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Authorities')


class UsersChoiceField(forms.MultipleChoiceField):

    def __init__(self, *args, **kwargs):
        kwargs['choices'] = lazy(UsersChoiceField.get_choices)
        super().__init__(*args, **kwargs)

    @classmethod
    def get_choices(klass):
        result = []
        for user in portal_models.DaoUser.all_users():
            result.append((user.email, '{} - {}'.format(user.email, user.name)))
        return result


class StudyUsersForm(forms.Form):
    users = UsersChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Users')


class GroupUsersForm(StudyUsersForm):
    pass


class UpdateUserForm(forms.Form):
    name = forms.CharField(
        label='User name', max_length=100,
        help_text='Full name of the user')
    enabled = forms.BooleanField(
        required=False,
        label='User enabled', help_text=('Enable or disable the user'))


class CreateUserForm(forms.Form):
    email = forms.EmailField(
        label='Email address', max_length=100,
        help_text=('The email address is used for uniquely identifying '
                   'the user'))
    name = forms.CharField(
        label='User name', max_length=100,
        help_text='Full name of the user')
    enabled = forms.BooleanField(
        label='User enabled', help_text=('Enable or disable the user'))


class ImportForm(forms.Form):
    file = forms.FileField()
