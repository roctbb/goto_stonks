from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required


from webapp.forms import ProjectForm, ChangeForm
from webapp.models import Project, Invite


@staff_member_required
def index(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manager.projects')
    else:
        form = ProjectForm()


    ipo_projects = Project.objects.filter(state='ipo').all()
    market_projects = Project.objects.filter(state='market').all()
    ended_projects = Project.objects.filter(state='ended').all()

    change_forms = {}

    for project in market_projects:
        change_forms[project.id] = ChangeForm(project).as_ul()


    return render(request, 'manager/projects/index.html', {
        'ipo_projects': ipo_projects,
        'market_projects': market_projects,
        'ended_projects': ended_projects,
        'form': form,
        'change_forms': change_forms
    })

@staff_member_required
def edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('manager.projects')
    else:
        form = ProjectForm(instance=project)


    return render(request, 'manager/projects/edit.html', {'form': form})

@staff_member_required
def to_market(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project.to_market()
    return redirect('manager.projects')

@staff_member_required
def to_end(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project.to_end()
    return redirect('manager.projects')


@staff_member_required
def change(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        form = ChangeForm(project, data=request.POST)
        if form.is_valid() and form.save():
            return redirect('manager.projects')
        return HttpResponse('Неудается провести операцию')


@staff_member_required
def pay_divs(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project.pay_dividents()
    return redirect('manager.projects')


