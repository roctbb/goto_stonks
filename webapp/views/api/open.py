from webapp.models import Project
from django.http import JsonResponse


def get_prices(request):
    market_projects = Project.objects.filter(state='market').all()

    result = [
        {
            "name": project.name,
            "price": project.stock_price()
        }
        for project in market_projects
    ]

    return JsonResponse(result, safe=False)


