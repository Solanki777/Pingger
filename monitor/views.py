from django.shortcuts import render
import requests


def ping(request):

    result = None

    if request.method == "POST":

        url = request.POST.get("url")

        try:
            response = requests.get(url, timeout=10)

            result = (
                f"Website is reachable! "
                f"Status Code: {response.status_code}"
            )

        except requests.RequestException:
            result = "Website is down or unreachable."

    return render(request,"ping.html",
                  {
                      "result":result
                      
                  })