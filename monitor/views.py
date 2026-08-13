from django.http import HttpResponse
import requests

def ping(request):
    url = "https://anantra.onrender.com"

    try :
        response = requests.get(url,timeout = 10)
        return HttpResponse(
            f"website is alive with response :{response.status_code}"
        )
    except requests.RequestException as e:
        return HttpResponse(
            f"website is down or unreachable due to : {e}"
        )
