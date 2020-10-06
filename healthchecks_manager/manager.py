from typing import List

from . import healthchecks_api_wrapper

import requests

cache = {}

default_creation_params = {
    "name": None,
    "tags": None,
    "desc": None,
    "timeout": None,
    "grace": None,
    "schedule": None,
    "tz": None,
    "channels": ["*"],
}


def create_check(check_name: str, creation_params: dict = {}):
    """
    Creates a healthcheck.
    """
    if "name" not in creation_params:
        creation_params["name"] = check_name
    for param in default_creation_params:
        if param not in creation_params and default_creation_params[param] is not None:
            creation_params[param] = default_creation_params[param]
    if "*" not in creation_params["channels"]:
        channels = healthchecks_api_wrapper.get_channels()
        # convert list of channels to dict indexed by name
        # ideally user would just pass in channel id isntead of name
        # in which case this would not be needed
        # however there is no way in the GUI to see the channel ID
        # so the user will be using name instead
        channels_by_name = {}
        for channel in channels:
            channel_name = channel["name"].lower()
            if channel_name in channels_by_name:
                raise ValueError(
                    f"python-circleci-package-boilerplate requires all channel names to be unique for identifcation purposes. \
                                {channel}\n\nis a duplicate of channel with id {channels_by_name[channel_name]}"
                )
            channels_by_name[channel_name] = channel["id"]
        channel_ids = []
        for channel_name in creation_params["channels"]:
            channel_name = channel_name.lower()
            channel_ids.append(channels_by_name[channel_name])
        creation_params["channels"] = ",".join(channel_ids)
    check = healthchecks_api_wrapper.create_check(check_name, creation_params)
    endpoint = healthchecks_api_wrapper.get_id_from_endpoint(check["ping_url"])
    return endpoint


def get_endpoint(check_name: str, creation_params: dict = {}):
    """
    Side effect: creates endpoint if it does not exist
    """
    check_name = check_name.lower()
    # try to get endpoint from cache
    endpoint = cache.get(check_name)
    # if not in cache
    if not endpoint:
        # get healthchecks in current project
        checks: List[dict] = healthchecks_api_wrapper.get_checks()
        # convert list of checks to dict indexed by name like cache
        checks_by_name = {}
        for check in checks:
            existing_check_name = check["name"].lower()
            if existing_check_name in checks_by_name:
                # todo: only raise error if duplicate check_name
                # we don't want everything to fail if there is a single duplicate
                raise ValueError(
                    f"python-circleci-package-boilerplate requires all check names to be unique for identifcation purposes. \
                                {check}\n\nis a duplicate of check with ping_url {checks_by_name[existing_check_name]}"
                )
            checks_by_name[existing_check_name] = check["ping_url"]
        endpoint = checks_by_name.get(check_name)
        # if not in existing healthchecks:
        if not endpoint:
            print("creating check")
            endpoint = create_check(check_name, creation_params)
            # save check_name/endpoint to cache
            cache[check_name] = endpoint
        else:
            print("check already exists")
            print("updating cache")
            for check_name in checks_by_name:
                cache[check_name] = checks_by_name[check_name]
    return endpoint


def start(check_name: str, creation_params: dict):
    """
    Signal to healthchecks.io to start timing the check_name in question
    """
    endpoint = get_endpoint(check_name, creation_params)
    requests.get(endpoint + "/start", timeout=5)


def done(check_name: str, creation_params: dict):
    """
    Let healthchecks.io know that the relevant job associated with check_name is completed
    """
    endpoint = get_endpoint(check_name, creation_params)
    requests.get(endpoint, timeout=5)


def fail(check_name: str, creation_params: dict):
    """
    Let healthchecks.io know that the relevant job associated with check_name has failed
    """
    endpoint = get_endpoint(check_name, creation_params)
    requests.get(endpoint + "/fail", timeout=5)


"""
### management command
ping(name + '/' + flag)
make sure to prepend vpcname so people can easily tell what vpc the healthcheck
is failing in
"""
