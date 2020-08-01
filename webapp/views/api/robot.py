from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from webapp.models import Project, get_user_balance
from django.http import JsonResponse


@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_projects(request):
    answer = []

    projects = Project.objects.filter(state='market').all()

    for project in projects:
        answer.append({
            "id": project.id,
            "name": project.name,
            "price": project.stock_price(),
            "stocks": project.stocks_by(request.user)
        })

    return JsonResponse(answer, safe=False)


@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_balance(request):
    return JsonResponse({
        "id": request.user.id,
        "username": request.user.username,
        "balance": get_user_balance(request.user),
    }, safe=False)


def market_deal(request, pk, type):
    project = Project.objects.get(pk=pk)
    if project:
        number = request.GET.get('number')
        if project.state != 'market':
            return JsonResponse({
                "state": "error",
                "error": "not on market"
            }, safe=False)

        if not number:
            return JsonResponse({
                "state": "error",
                "error": "no number"
            }, safe=False)

        try:
            number = int(number)
        except:
            return JsonResponse({
                "state": "error",
                "error": "invalid number"
            }, safe=False)

        if type == 'buy':
            if project.buy(request.user, number):
                return JsonResponse({
                    "state": "success"
                }, safe=False)
            else:
                return JsonResponse({
                    "state": "error",
                    "error": "invalid operation"
                }, safe=False)
        if type == 'sell':
            if project.sell(request.user, number):
                return JsonResponse({
                    "state": "success"
                }, safe=False)
            else:
                return JsonResponse({
                    "state": "error",
                    "error": "invalid operation"
                }, safe=False)

    else:
        return JsonResponse({
            "state": "error",
            "error": "stock not found"
        }, safe=False)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def buy(request, pk):
    return market_deal(request, pk, 'buy')


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def sell(request, pk):
    return market_deal(request, pk, 'sell')
