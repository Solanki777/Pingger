import requests
import time


def check_monitor(url):

    try:
        start_time = time.time()

        response = requests.get(
            url,
            timeout=10
        )

        end_time = time.time()

        response_time = round(
            (end_time - start_time) * 1000,
            2
        )

        return {
            "success": 200 <= response.status_code < 300,
            "status_code": response.status_code,
            "response_time": response_time,
            "error": None,
        }

    except requests.Timeout:

        return {
            "success": False,
            "status_code": None,
            "response_time": None,
            "error": "Request timed out",
        }

    except requests.ConnectionError:

        return {
            "success": False,
            "status_code": None,
            "response_time": None,
            "error": "Connection failed",
        }

    except requests.RequestException as e:

        return {
            "success": False,
            "status_code": None,
            "response_time": None,
            "error": str(e),
        }