
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def test(request):
    print ("*"*20, request.body)
    if request.method == "POST":
        response = HttpResponse("post")
        return response
    elif request.method == 'GET':
        response = HttpResponse("get")
        return response
    else:
        return HttpResponse("unknown")