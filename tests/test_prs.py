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

    def set_return_val(self, number, body):
        node = {"number": number, "body": body}
        self.val["data"]["repository"]["commit"]["associatedPullRequests"]["edges"][0][
            "node"
        ] = node

    def run_query(self, *args, **kwargs):
        return self.val


m = MockGraphQL()
p = PRs("fake token", "15five", "fifteen5")


@pytest.fixture(autouse=True)
def mock_graphql(mocker: MockFixture):
    global p

    mocker.patch("rocket_releaser.prs.GraphQL", return_value=m)

    yield

    # reset prs so tests dont affect eachother
    p = PRs("fake token", "15five", "fifteen5")


def test_pull_request_dicts_should_have_correct_content():
    m.set_return_val(12, "test")

    pull_request_dicts = p.pull_request_dicts(["fake sha"])
    assert len(pull_request_dicts) == 1
    assert pull_request_dicts[0]["number"] == 12
    assert pull_request_dicts[0]["body"] == "test"
    assert pull_request_dicts[0]["deploy_sha"] == "fake sha"
