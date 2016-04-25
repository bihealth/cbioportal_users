"""cbioportal_users URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    url('^$', RedirectView.as_view(url='/usermgmt')),
    url(r'^accounts/login/?$', auth_views.login,
        {'template_name': 'admin/login.html'}, name='auth_login'),
    url(r'^accounts/logout/?$', auth_views.logout,
        {'next_page': '/accounts/login'}, name='auth_logout'),
    url(r'^accounts/', include('django.contrib.auth.urls')),

    url(r'^admin/', admin.site.urls),
    url(r'^usermgmt/', include('usermgmt.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
