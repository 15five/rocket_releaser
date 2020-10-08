import pytest
from rocket_releaser.graphql import GraphQL, BadReturnStatus

g = GraphQL("")


def test_run_query_returns_json_when_good_status_code(mocker):
    class MockResponse:
        status_code = 200

        @staticmethod
        def json():
            return "mock json"

    mocker.patch("requests.post", return_value=MockResponse())

    response = g.run_query("")

    assert response == "mock json"


def test_run_query_raises_error_when_bad_status_code(mocker):
    class MockResponse:
        status_code = 500

        @staticmethod
        def json():
            return "mock json"

    mocker.patch("requests.post", return_value=MockResponse())

    with pytest.raises(BadReturnStatus):
        response = g.run_query("")
