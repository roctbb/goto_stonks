from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required


from webapp.forms import ProjectForm
from webapp.models import Project, Invite


@staff_member_required
def index(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('projects')
    else:
        form = ProjectForm()


    ipo_projects = Project.objects.filter(state='ipo').all()
    market_projects = Project.objects.filter(state='market').all()
    ended_projects = Project.objects.filter(state='ended').all()

    return render(request, 'manager/projects/index.html', {
        'ipo_projects': ipo_projects,
        'market_projects': market_projects,
        'ended_projects': ended_projects,
        'form': form
    })

@staff_member_required
def edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('projects')
    else:
        form = ProjectForm(instance=project)


    return render(request, 'manager/projects/edit.html', {'form': form})





