from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from webapp.models import Invite


@staff_member_required
def index(request):
    if request.method == 'POST':
        for i in range(10):
            Invite().generate().save()
    invites_list = Invite.objects.all()

    return render(request, 'manager/invites/index.html', {'invites': invites_list})

