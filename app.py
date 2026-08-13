import requests
response = requests.get("https://anantra.onrender.com/")

print(response.status_code)