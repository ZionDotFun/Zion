import json

import requests


def _make_get_request(url:str, headers:None, params= None):
    response = requests.get(url=url,headers=headers,params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError(f"Error: {response.status_code}: {response.content}")
    
def _make_post_request(url:str, payload):
    response = requests.post(url=url, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError(f"Error {response.status_code}: {response.content}")
    
def _make_put_request(url:str,payload):
    response = requests.put(url=url, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError(f"Error: {response.status_code}: {response.content}")
    
def _make_delete_request(url):
    response = requests.delete(url)
    if response.status_code == 200:
        try:
            if response.text.strip():
                return response.json()
            else:
                return None
        except json.JSONDecodeError:
            raise ValueError("Received unexpected response format from API")
    else:
        response.raise_for_status()