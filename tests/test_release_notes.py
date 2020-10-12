from rocket_releaser import release_notes
import pytest
from pytest_mock import MockFixture
from unittest.mock import Mock
from os import environ


@pytest.fixture(autouse=True)
def mock_reqs(mocker):
    mocker.patch("github3.GitHub")
    mocker.patch("jira.JIRA")
    mocker.patch("rocket_releaser.prs.GraphQL")
    mocker.patch("rocket_releaser.slack.slacker")


def test_main():

    # arguments dont really matter here
    slack_text = release_notes.main(
        [
            "github token",
            "0782415",
            "8038fc3",
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
    assert slack_text
    # slack text should say env of deployment
    assert "prod".upper() in slack_text
    # slack text should have link to github diff of commits
    assert "0782415" in slack_text and "8038fc3" in slack_text
    # because we mocked dependencies no PR's / tickets should be found
    assert "0 PRs found" in slack_text
    assert "0 jira tickets found" in slack_text


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
    assert "0 PRs found" in slack_text


def test_turn_changelog_into_string_has_qa_notes():
    mock_pr_1 = {
        "number": 1,
        "body": """
RELEASES
Fixes ENG-9999

QA
bla bla bla
        """,
    }
    changelog_str = release_notes.turn_changelog_into_string(
        [mock_pr_1], "preview", "0782415", "8038fc3", 1, "org_name", "repo_name"
    )
    assert "Fixes" in changelog_str
    assert "Notes for QA" in changelog_str


def test_turn_changelog_into_string_detects_hotfix():
    mock_pr_1 = {
        "title": "__2019-07-05.0 - to staging (hotfix)",
        "number": 1,
        "body": "",
    }
    changelog_str = release_notes.turn_changelog_into_string(
        [mock_pr_1], "production", "0782415", "8038fc3", 1, "org_name", "repo_name"
    )
    first_line = changelog_str.split("\n")[0]
    assert "HOTFIX" not in first_line

    mock_pr_1 = {
        "title": "__2019-07-05.0 - to production (hotfix)",
        "number": 1,
        "body": "",
    }
    changelog_str = release_notes.turn_changelog_into_string(
        [mock_pr_1], "production", "0782415", "8038fc3", 1, "org_name", "repo_name"
    )
    first_line = changelog_str.split("\n")[0]
    assert "HOTFIX" in first_line


def test_turn_changelog_into_string_detects_when_commits_are_same():
    changelog_str = release_notes.turn_changelog_into_string(
        [], "preview", "", "", 55, "org_name", "repo_name"
    )
    assert "Start and end commit hashes are the same" in changelog_str


def test_turn_changelog_into_string_has_correct_num_jira_tickets():
    mock_pr_1 = {
        "number": 1,
        "body": """
RELEASES
Fixes ENG-9999

QA
bla bla bla
        """,
    }
    changelog_str = release_notes.turn_changelog_into_string(
        [mock_pr_1], "preview", "", "", 55, "org_name", "repo_name"
    )
    assert "55" in changelog_str
