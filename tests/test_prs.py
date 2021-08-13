from rocket_releaser.prs import PRs
import pytest
from pytest_mock import MockFixture


class MockGraphQL:

    val = {
        "data": {
            "repository": {
                "commit": {"associatedPullRequests": {"edges": [{"node": None}]}}
            }
        }
    }

    def set_return_val(self, number, body, label_name):
        node: dict = {
            "number": number,
            "body": body,
            "labels": {"nodes": [{"name": label_name}]},
        }
        self.val["data"]["repository"]["commit"]["associatedPullRequests"]["edges"][0][
            "node"
        ] = node

    def set_no_associated_prs(self):
        self.val["data"]["repository"]["commit"]["associatedPullRequests"] = []

    def set_error(self):
        self.val = {"errors": [{"message": "foo"}]}

    def run_query(self, *args, **kwargs):
        return self.val


m = MockGraphQL()
p = PRs("fake token", "15five", "repoName")


@pytest.fixture(autouse=True)
def mock_graphql(mocker: MockFixture):
    global p

    mocker.patch("rocket_releaser.prs.GraphQL", return_value=m)

    yield

    # reset prs so tests dont affect eachother
    p = PRs("fake token", "15five", "repoName")


def test_pull_request_dicts_should_have_correct_content():
    m.set_return_val(12, "test", "fake label")

    pull_request_dicts = p.pull_request_dicts(["fake sha"])
    assert len(pull_request_dicts) == 1
    assert pull_request_dicts[0]["number"] == 12
    assert pull_request_dicts[0]["body"] == "test"
    assert pull_request_dicts[0]["deploy_sha"] == "fake sha"
    assert pull_request_dicts[0]["labels"]["nodes"][0]["name"] == "fake label"


def test_method_is_failsafe(caplog):
    m.set_no_associated_prs()

    sha = "fake sha"
    p.pull_request_dicts([sha])
    assert (
        caplog.records[0].message == f"commit {sha} not found or has no associated PRs"
    )


def test_method_logs_errors(caplog):
    m.set_error()

    sha = "fake sha"
    p.pull_request_dicts([sha])
    assert caplog.records[0].message == f"error with sha {sha}: foo"
