from rocket_releaser.changelog import ChangeLog


def test_changelog_note_should_be_in_right_format():
    pull_request_dict = {
        "number": 1,
        "body": "RELEASES\nDESCRIPTION_1",
        "labels": ["feat-CATEGORY1"],
    }
    assert (
        ChangeLog([pull_request_dict], "org_name", "repo_name").parse_bodies()
        == """*CATEGORY1*
• DESCRIPTION_1 <https://github.com/org_name/repo_name/pull/1|PR-1>

"""
    )


def test_changelog_note_should_be_in_right_category():
    pull_request_dict_1 = {
        "number": 1,
        "body": "RELEASES\nDESCRIPTION_1",
        "labels": ["feat-CATEGORY1"],
    }
    pull_request_dict_2 = {
        "number": 2,
        "body": "RELEASES\nDESCRIPTION_2",
        "labels": ["feat-CATEGORY2"],
    }
    assert (
        ChangeLog(
            [pull_request_dict_1, pull_request_dict_2], "org_name", "repo_name"
        ).parse_bodies()
        == """*CATEGORY1*
• DESCRIPTION_1 <https://github.com/org_name/repo_name/pull/1|PR-1>

*CATEGORY2*
• DESCRIPTION_2 <https://github.com/org_name/repo_name/pull/2|PR-2>

"""
    )


def test_parse_bodies_should_add_jira_link():
    pull_request_dict = {"number": 12, "body": "RELEASES\n[DS-435]", "labels": []}

    assert (
        "atlassian"
        in ChangeLog(
            [pull_request_dict],
            "org_name",
            "repo_name",
            jira_url="https://company.atlassian.net",
        ).parse_bodies()
    )
