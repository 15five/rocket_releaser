from typing import Dict
from rocket_releaser import release_notes
import pytest
from pytest_mock import MockFixture
from unittest.mock import Mock


@pytest.fixture(autouse=True)
def mock_reqs(mocker):
    mocker.patch("github3.GitHub")
    mocker.patch("jira.JIRA")
    mocker.patch("rocket_releaser.prs.GraphQL")
    mocker.patch("rocket_releaser.slack.slacker")


def test_main():

    # arguments dont really matter here
    plaintext_notes = release_notes.main(
        [
            "github token",
            "56bfe2d",
            "fa6e866",
            "org_name",
            "repo_name",
            "--slack_webhook_key",
            "fake slack key",
            "--jira_username",
            "bob@company.com",
            "--jira_url",
            "https://company.atlassian.net",
        ]
    )

    # slack_text has variable time so we cant do exact comparison check :(

    # slack text should be present
    assert (
        plaintext_notes
        == """Prod Release

*Changeset*: <https://github.com/org_name/repo_name/compare/56bfe2d...fa6e866|56bfe2d...fa6e866>
*Stats*: 0 tickets | 0 PR's"""
    )


def test_release_notes_plaintext(mocker):
    mock_pr_1 = {
        "number": 1,
        "body": """
RELEASES
Fixes ENG-9999

QA
bla bla bla
        """,
        "merged": True,
        "labels": [],
    }

    mocker.patch("rocket_releaser.prs.PRs.pull_request_dicts", return_value=[mock_pr_1])
    plaintext_notes = release_notes.release_notes(
        "github_token",
        "0782415",
        "8038fc3",
        "org_name",
        "repo_name",
        jira_token="jira_token",
        jira_username="",
        jira_url="",
        dry_run=True,
    )
    assert (
        plaintext_notes
        == """Prod Release
*Uncategorized*
• Fixes ENG-9999 <https://github.com/org_name/repo_name/pull/1|PR-1>


*Changeset*: <https://github.com/org_name/repo_name/compare/0782415...8038fc3|0782415...8038fc3>
*Stats*: 1 tickets | 1 PR's"""
    )


def test_release_notes_slack(mocker):
    mock_pr_1 = {
        "number": 1,
        "body": """
RELEASES
Fixes ENG-9999

QA
bla bla bla
        """,
        "merged": True,
        "labels": [],
    }

    mocker.patch("rocket_releaser.prs.PRs.pull_request_dicts", return_value=[mock_pr_1])
    with mocker.patch(
        "rocket_releaser.slack.post_deployment_message_to_slack",
    ) as mocked_post_slack_message:
        release_notes.release_notes(
            "github_token",
            "0782415",
            "8038fc3",
            "org_name",
            "repo_name",
            jira_token="jira_token",
            jira_username="",
            jira_url="",
            dry_run=True,
        )
        mocked_post_slack_message.assert_called_once()
        slack_dict: Dict[str] = mocked_post_slack_message.call_args.args[0]
        assert slack_dict["blocks"][0]["text"]["text"] == "Prod Release"
        assert (
            slack_dict["blocks"][1]["text"]["text"]
            == "*Uncategorized*\n• Fixes ENG-9999"
        )
        assert (
            slack_dict["blocks"][3]["elements"][0]["text"]
            == """*Changeset*: <https://github.com/15five/fifteen5/compare/0782415...8038fc3|0782415...8038fc3>
*Stats*: 0 tickets | 0 PR's"""
        )


def test_release_notes_skips_unmerged_pr(mocker):
    mock_pr_1 = {
        "number": 1,
        "body": """
RELEASES
Fixes ENG-9999

QA
bla bla bla
        """,
        "merged": False,
        "labels": [],
    }

    mocker.patch("rocket_releaser.prs.PRs.pull_request_dicts", return_value=[mock_pr_1])
    slack_text = release_notes.release_notes(
        "github_token",
        "0782415",
        "8038fc3",
        "org_name",
        "repo_name",
        jira_token="jira_token",
        jira_username="",
        jira_url="",
        dry_run=True,
    )
    assert "0 PR's" in slack_text


def test_turn_changelog_into_string_detects_hotfix(mocker):
    mock_pr_1 = {
        "title": "__2019-07-05.0 - to staging (hotfix)",
        "number": 1,
        "body": "",
        "labels": [],
        "merged": True,
    }
    mocker.patch("rocket_releaser.prs.PRs.pull_request_dicts", return_value=[mock_pr_1])
    changelog_str = release_notes.release_notes(
        "github_token",
        "0782415",
        "8038fc3",
        "org_name",
        "repo_name",
    )
    first_line = changelog_str.split("\n")[0]
    assert "HOTFIX" not in first_line

    mock_pr_1 = {
        "title": "__2019-07-05.0 - to production (hotfix)",
        "number": 1,
        "body": "",
        "labels": [],
        "merged": True,
    }
    mocker.patch("rocket_releaser.prs.PRs.pull_request_dicts", return_value=[mock_pr_1])
    changelog_str = release_notes.release_notes(
        "github_token",
        "0782415",
        "8038fc3",
        "org_name",
        "repo_name",
    )
    first_line = changelog_str.split("\n")[0]
    assert "HOTFIX" in first_line


def test_turn_changelog_into_string_detects_when_commits_are_same():
    changelog_str = release_notes.release_notes(
        "github_token",
        "",
        "",
        "org_name",
        "repo_name",
    )
    assert "Start and end commit hashes are the same" in changelog_str


def test_turn_changelog_into_string_has_correct_num_jira_tickets(mocker):
    mock_pr_1 = {
        "number": 1,
        "body": """
RELEASES
feature bla which is not associated to jira ticket

QA
bla bla bla
        """,
        "labels": [],
        "merged": True,
    }
    mocker.patch("rocket_releaser.prs.PRs.pull_request_dicts", return_value=[mock_pr_1])
    changelog_str = release_notes.release_notes(
        "github_token", "", "", "org_name", "repo_name", jira_token="foo"
    )
    assert "0 tickets" in changelog_str
