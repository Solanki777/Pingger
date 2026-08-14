from django.shortcuts import render
import requests
import time
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def ping(request):

    result = None
    response_time = None
    status_code = None
    status_type = None

    if request.method == "POST":

        url = request.POST.get("url")

        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            end_time = time.time()

            response_time = round(
                (end_time-start_time) *1000,2
            )
            status_code = response.status_code


            if 200 <= status_code < 300:
                result = "Website is healthy"
                status_type = "success"

            elif 300 <= status_code < 400:
                result = "Website is reachable but redirecting"
                status_type = "warning"

            elif 400 <= status_code < 500:
                result = "Website is reachable but returned a client error"
                status_type = "warning"

            elif 500 <= status_code < 600:
                result = "Website is reachable but returned a server error"
                status_type = "danger"


        except requests.Timeout:

            result = "Website request timed out"
            status_type = "danger"

        except requests.ConnectionError:

            result = "Could not connect to website"
            status_type = "danger"

        except requests.RequestException:

            result = "Website check failed"
            status_type = "danger"

    return render(request,"ping.html",
                {
                    "result":result,
                    "status_code":status_code,
                    "response_time":response_time,
                     "status_type":status_type })