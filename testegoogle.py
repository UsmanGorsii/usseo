import requests

proxies = {
        "http":"http://localhost:8888",
        "https":"http://localhost:8888"
    }
print(requests.get("https://api.ipify.org?format=json", proxies=proxies).json())
