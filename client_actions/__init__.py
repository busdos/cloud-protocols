import requests


def post_action(url, protocol, action, payload):
    complete_url = f"{url}/protocols/{protocol}/{action}"
    
    # print(f"Posing to url {complete_url} with payload {payload}")
    res = requests.post(url=complete_url, json=payload)
    # print(f"Received response: {res}")

    return res.json()