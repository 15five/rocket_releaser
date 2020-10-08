import requests


class BadReturnStatus(Exception):
    pass


class GraphQL:
    def __init__(self, base_api_uri, token: str = ""):
        self.base_api_uri = base_api_uri
        self.headers = {"Authorization": "Bearer " + token}

    def run_query(self, query, variables={}):
        request = requests.post(
            self.base_api_uri,
            json={"query": query, "variables": variables},
            headers=self.headers,
        )

        if request.status_code == 200:
            return request.json()
        else:
            raise BadReturnStatus(
                "Query failed to run by returning code of {}. {}".format(
                    request.status_code, query
                )
            )
