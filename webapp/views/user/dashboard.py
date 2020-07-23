from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from webapp.models import Project, get_user_balance


@login_required
def index(request):
    balance = get_user_balance(request.user)
    ipo_projects = Project.objects.filter(state='ipo').all()
    market_projects = Project.objects.filter(state='market').all()
    ended_projects = Project.objects.filter(state='ended').all()

    return render(request, 'user/dashboard/index.html', {
        'ipo_projects': ipo_projects,
        'market_projects': market_projects,
        'ended_projects': ended_projects,
        'balance': balance
    })