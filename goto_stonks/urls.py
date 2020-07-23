"""goto_stonks URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from webapp.views.manager import projects, invites
from webapp.views.user import auth

urlpatterns = [
    path('admin/', admin.site.urls),
    path('manager/projects', projects.index, name='manager.projects'),
    path('manager/projects/<int:pk>/edit', projects.edit, name='manager.edit_project'),
    path('manager/invites', invites.index, name='manager.invites'),

    path('login', auth.login_page, name='login'),
    path('register', auth.register_page, name='register'),
    path('logout', auth.logout_page, name='logout'),
]
