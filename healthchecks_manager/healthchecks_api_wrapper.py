import json
from typing import List
import requests

API_URL_BASE = "https://healthchecks.io/api/v1"
API_key = ""


def get_id_from_endpoint(endpoint: str):
    """
    given a endpoint like https://hc-ping.com/2453273d-864d-4671-9ef9-a024b1a6fa83
    returns 2453273d-864d-4671-9ef9-a024b1a6fa83
    """
    return endpoint[endpoint.rfind("/") + 1 :]


def get_checks() -> List[dict]:
    checks_response = requests.get(
        API_URL_BASE + "/checks/", headers={"X-Api-key": API_key}
    )
    checks_response.raise_for_status()
    check_response_json: dict = checks_response.json()

    return check_response_json["checks"]


def create_check(check_name: str, creation_params: dict = {}) -> List[dict]:
    creation_response = requests.post(
        API_URL_BASE + "/checks/",
        headers={"X-Api-key": API_key},
        data=json.dumps(creation_params),
    )
    creation_response.raise_for_status()
    creation_response_json: dict = creation_response.json()

    return creation_response_json


def get_channels() -> List[dict]:
    channels_response = requests.get(
        API_URL_BASE + "/channels/", headers={"X-Api-key": API_key}
    )
    channels_response.raise_for_status()
    channels_response_json = channels_response.json()

    return channels_response_json["channels"]
