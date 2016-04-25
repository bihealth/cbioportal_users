from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.Index.as_view(), name='index'),

    url(r'^user/create/?$', views.UserCreate.as_view(), name='user_create'),
    url(r'^user/view/(?P<email>.*)/?$', views.UserView.as_view(), name='user_view'),
    url(r'^user/list/?$', views.UserList.as_view(), name='user_list'),
    url(r'^user/update/(?P<email>.*)/?$', views.UserUpdate.as_view(), name='user_update'),
    url(r'^user/delete/(?P<email>.*)/?$', views.UserDelete.as_view(), name='user_delete'),
    url(r'^user/access/(?P<email>.*)/?$', views.UserStudyAccess.as_view(), name='user_authorities'),

    url(r'^study/list/?$', views.StudyList.as_view(), name='study_list'),
    url(r'^study/view/(?P<identifier>.*)/?$', views.StudyView.as_view(), name='study_view'),
    url(r'^study/users/(?P<identifier>.*)/?$', views.StudyUsers.as_view(), name='study_users'),
    url(r'^group/list/?$', views.GroupList.as_view(), name='group_list'),
    url(r'^group/view/(?P<name>.*)/?$', views.GroupView.as_view(), name='group_view'),
    url(r'^group/users/(?P<name>.*)/?$', views.GroupUsers.as_view(), name='group_users'),

    url(r'^export/?$', views.Export.as_view(), name='export'),
    url(r'^import/?$', views.Import.as_view(), name='import'),
]

