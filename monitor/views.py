from django.shortcuts import render
import requests
import time


def ping(request):

    result = None
    response_time = None
    status_code = None

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


            result = "website is reachable"

        except requests.RequestException:
            result = "Website is down or unreachable."

    return render(request,"ping.html",
                {
                    "result":result,
                    "status_code":status_code,
                    "response_time":response_time })