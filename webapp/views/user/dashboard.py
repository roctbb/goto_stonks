from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from webapp.forms import IpoInvestForm, StockForm
from webapp.models import Project, get_user_balance

from django.template.defaulttags import register

@register.filter
def roundit(n, s):
    return round(n, s)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def invest_sum(project, user):
    return project.invested_by(user)

@register.filter
def all_stock_sum(project, user):
    return project.all_stocks_by(user)

@register.filter
def stock_sum(project, user):
    return project.stocks_by(user)


@register.filter
def frozen_stock_sum(project, user):
    return project.frozen_stocks_by(user)

@register.filter
def percent(project, user):
    return project.percent_change_by(user)

@register.filter
def multiply(value, arg):
    return value * arg

@login_required(login_url='/login')
def index(request):
    balance = get_user_balance(request.user)
    ipo_projects = Project.objects.filter(state='ipo').all()
    market_projects = Project.objects.filter(state='market').all()
    ended_projects = Project.objects.filter(state='ended').all()

    invest_forms = {}

    for project in ipo_projects:
        invest_forms[project.id] = IpoInvestForm(request.user, project).as_ul()

    stock_forms = {}

    for project in market_projects:
        stock_forms[project.id] = StockForm(request.user, project).as_ul()

    return render(request, 'user/dashboard/index.html', {
        'ipo_projects': ipo_projects,
        'market_projects': market_projects,
        'ended_projects': ended_projects,
        'balance': balance,
        'invest_forms': invest_forms,
        'stock_forms': stock_forms
    })


@login_required(login_url='/login')
def invest(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        form = IpoInvestForm(request.user, project, data=request.POST)
        if form.is_valid() and form.save():
            return redirect('dashboard')
        return HttpResponse('Недостаточно средств')

@login_required(login_url='/login')
def stock(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        form = StockForm(request.user, project, data=request.POST)
        if form.is_valid() and form.save():
            return redirect('dashboard')
        return HttpResponse('Неудается провести операцию')