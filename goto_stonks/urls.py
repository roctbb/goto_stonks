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
from webapp.views.user import auth, dashboard
from webapp.views.api import open
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('manager/projects', projects.index, name='manager.projects'),
    path('manager/projects/<int:pk>/edit', projects.edit, name='manager.edit_project'),
    path('manager/projects/<int:pk>/to_market', projects.to_market, name='manager.project_to_market'),
    path('manager/projects/<int:pk>/to_end', projects.to_end, name='manager.project_to_end'),
    path('manager/projects/<int:pk>/change', projects.change, name='manager.project_change'),
    path('manager/projects/<int:pk>/pay', projects.pay_divs, name='manager.pay_divs'),
    path('manager/invites', invites.index, name='manager.invites'),
    path('manager/', lambda r:redirect('manager.projects'), name='manager_index'),

    path('login', auth.login_page, name='login'),
    path('register', auth.register_page, name='register'),
    path('logout', auth.logout_page, name='logout'),
    path('dashboard', dashboard.index, name='dashboard'),
    path('invest/<int:pk>', dashboard.invest, name='invest'),
    path('stock/<int:pk>', dashboard.stock, name='stock'),
    path('', lambda r:redirect('dashboard'), name='index'),

    path('api/open/prices', open.get_prices, name='api.open.get_prices'),
]
