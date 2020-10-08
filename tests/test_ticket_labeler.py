from rocket_releaser.ticket_labeler import TicketLabeler
import pytest
from pytest_mock import MockFixture
from unittest.mock import Mock
from rocket_releaser.prs import PRs


@pytest.fixture(autouse=True)
def mock_reqs(mocker):
    mocker.patch("github3.GitHub")
    mocker.patch("jira.JIRA")


def test_no_jira_ticket_mentioned(mocker: MockFixture):
    pull_request_dicts = [
        {
            "number": 5,
            "title": "removing middle finger emoji",
            "body": "extra text goes here.",
        }
    ]

    t = TicketLabeler(
        "",
        pull_request_dicts,
        "",
        "",
        "fakeJiraToken",
        "bob@company.com",
        "https://foo.atlassian.net",
    )
    numTickets = t.label_tickets("", "")
    assert numTickets == 0


def test_one_jira_tickets_with_number_in_title(mocker: MockFixture):
    pull_request_dicts = [
        {"number": 5, "title": "removing middle finger emoji [ENG-666]"}
    ]

    t = TicketLabeler(
        "",
        pull_request_dicts,
        "",
        "",
        "fakeJiraToken",
        "bob@company.com",
        "https://foo.atlassian.net",
    )
    numTickets = t.label_tickets("", "")
    assert numTickets == 1


def test_one_jira_tickets_with_number_in_body(mocker: MockFixture):
    pull_request_dicts = [
        {
            "number": 5,
            "title": "removing middle finger emoji",
            "body": "removing middle finger emoji fixes [ENG-666]",
        }
    ]

    t = TicketLabeler(
        "",
        pull_request_dicts,
        "",
        "",
        "fakeJiraToken",
        "bob@company.com",
        "https://foo.atlassian.net",
    )
    numTickets = t.label_tickets("", "")
    assert numTickets == 1


def test_random_jira_tickets_in_body_are_not_counted(mocker: MockFixture):
    pull_request_dicts = [
        {
            "number": 5,
            "title": "removing middle finger emoji",
            "body": "removing middle finger emoji. Similar to other ticket [ENG-666]",
        }
    ]

    t = TicketLabeler(
        "",
        pull_request_dicts,
        "",
        "",
        "fakeJiraToken",
        "bob@company.com",
        "https://foo.atlassian.net",
    )
    numTickets = t.label_tickets("", "")
    assert numTickets == 0


# todo: assert preview/staging/prod tickets were transitioned


def test_one_jira_ticket_preview(mocker: MockFixture):
    pull_request_dicts = [{"number": 5, "title": "closes [ENG-666]"}]

    t = TicketLabeler(
        "",
        pull_request_dicts,
        "",
        "",
        "fakeJiraToken",
        "bob@company.com",
        "https://foo.atlassian.net",
    )
    numTickets = t.label_tickets("preview", "preview")
    assert numTickets == 1


def test_one_jira_ticket_staging(mocker: MockFixture):
    pull_request_dicts = [{"number": 5, "title": "fixes [ENG-666]"}]

    t = TicketLabeler(
        "",
        pull_request_dicts,
        "",
        "",
        "fakeJiraToken",
        "bob@company.com",
        "https://foo.atlassian.net",
    )
    numTickets = t.label_tickets("staging", "staging")
    assert numTickets == 1


def test_one_jira_ticket_production(mocker: MockFixture):
    pull_request_dicts = [{"number": 5, "title": "closes  [ENG-666]"}]

    t = TicketLabeler(
        "",
        pull_request_dicts,
        "",
        "",
        "fakeJiraToken",
        "bob@company.com",
        "https://foo.atlassian.net",
    )
    numTickets = t.label_tickets("production", "production")
    assert numTickets == 1


def test_multiple_jira_tickets_with_number_in_title(mocker: MockFixture):
    pull_request_dicts = [
        {"number": 5, "title": "removing middle finger emoji [ENG-666]"},
        {"number": 6, "title": "More foobar [ENG-667]"},
    ]

    t = TicketLabeler(
        "",
        pull_request_dicts,
        "",
        "",
        "fakeJiraToken",
        "bob@company.com",
        "https://foo.atlassian.net",
    )
    numTickets = t.label_tickets("", "")
    assert numTickets == 2


def test_multiple_jira_tickets_with_number_in_body(mocker: MockFixture):
    pull_request_dicts = [
        {
            "number": 5,
            "title": "removing middle finger emoji",
            "body": "removing middle finger emoji fixes [ENG-666]",
        },
        {"number": 6, "title": "More foobar", "body": "More foobar closes [ENG-667]"},
    ]

    t = TicketLabeler(
        "",
        pull_request_dicts,
        "",
        "",
        "fakeJiraToken",
        "bob@company.com",
        "https://foo.atlassian.net",
    )
    numTickets = t.label_tickets("", "")
    assert numTickets == 2


def test_one_jira_ticket_but_two_prs(mocker: MockFixture):
    pull_request_dicts = [
        {"number": 5, "title": "removing middle finger emoji"},
        {"number": 6, "title": "More foobar [ENG-667]"},
    ]

    t = TicketLabeler(
        "",
        pull_request_dicts,
        "",
        "",
        "fakeJiraToken",
        "bob@company.com",
        "https://foo.atlassian.net",
    )
    numTickets = t.label_tickets("", "")
    assert numTickets == 1


def test_one_jira_referenced_in_both_title_and_body_only_returns_single_issue(
    mocker: MockFixture,
):
    pull_request_dicts = [
        {"number": 6, "title": "More foobar [ENG-667]", "body": "closes ENG-667"}
    ]

    t = TicketLabeler(
        "",
        pull_request_dicts,
        "",
        "",
        "fakeJiraToken",
        "bob@company.com",
        "https://foo.atlassian.net",
    )
    numTickets = t.label_tickets("", "")
    assert numTickets == 1


def test_get_jira_ticket_maps_for_empty_string():
    search_string = """
    Call me Ishmael. Some years ago--never mind how long precisely --having little or no money in
    my purse, and nothing particular to interest me on shore, I thought I would sail about a little and see the watery
    part of the world.
    """
    jira_ticket_info = TicketLabeler.get_jira_ticket_maps(search_string)
    assert jira_ticket_info == []


def test_get_jira_ticket_maps_for_string_without_jira_info():
    search_string = ""
    jira_ticket_info = TicketLabeler.get_jira_ticket_maps(search_string)
    assert jira_ticket_info == []


def test_get_jira_ticket_maps_for_one_on_ones():
    search_string = "bla bla bla 1-on-1"  # on-1 is not a actual ticket name
    jira_ticket_info = TicketLabeler.get_jira_ticket_maps(search_string)
    assert jira_ticket_info == []


def test_get_jira_ticket_maps_for_single_issue_string_without_brackets():
    search_string = "Some text goes ENG-123 here"
    jira_ticket_info = TicketLabeler.get_jira_ticket_maps(search_string)
    assert jira_ticket_info[0]["issue"] == "ENG-123"
    assert jira_ticket_info[0]["transition"] is None


def test_get_jira_ticket_maps_for_single_issue_string_with_brackets():
    search_string = "Some text goes [ENG-123] here"
    jira_ticket_info = TicketLabeler.get_jira_ticket_maps(search_string)
    assert jira_ticket_info[0]["issue"] == "ENG-123"
    assert jira_ticket_info[0]["transition"] is None


def test_get_jira_ticket_maps_for_single_issue_string_with_transition_keyword():
    search_string = "Some text goes closes ENG-123 here"
    jira_ticket_info = TicketLabeler.get_jira_ticket_maps(search_string)
    assert jira_ticket_info[0]["issue"] == "ENG-123"
    assert jira_ticket_info[0]["transition"] == "closes"


def test_get_jira_ticket_maps_for_single_issue_lowercase_string():
    search_string = "Some text goes [eng-123] here"
    jira_ticket_info = TicketLabeler.get_jira_ticket_maps(search_string)
    assert jira_ticket_info[0]["issue"] == "ENG-123"
    assert jira_ticket_info[0]["transition"] is None


def test_get_jira_ticket_maps_for_single_issue_with_mixed_case_string():
    search_string = "Closes Eng-123, fixing this ticket"
    jira_ticket_info = TicketLabeler.get_jira_ticket_maps(search_string)
    assert jira_ticket_info[0]["issue"] == "ENG-123"
    assert jira_ticket_info[0]["transition"] == "closes"


def test_get_jira_ticket_maps_for_multiple_issue_string():
    search_string = """
        Some text goes ENG-123 here
        RELEASES
        Fixes [DEV-723], after making some changes
        also linked to [ENG-4567]
        """
    jira_ticket_info = TicketLabeler.get_jira_ticket_maps(search_string)
    assert jira_ticket_info[0]["issue"] == "ENG-123"
    assert jira_ticket_info[0]["transition"] is None
    assert jira_ticket_info[1]["issue"] == "DEV-723"
    assert jira_ticket_info[1]["transition"] == "fixes"
    assert jira_ticket_info[2]["issue"] == "ENG-4567"
    assert jira_ticket_info[2]["transition"] is None
