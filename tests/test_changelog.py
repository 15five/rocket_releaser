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


def test_changelog_note_picks_up_right_label():
    pull_request_dict = {
        "number": 1,
        "body": "RELEASES\nDESCRIPTION_1",
        "labels": ["ignore", "feat-CATEGORY1"],
    }
    assert (
        ChangeLog([pull_request_dict], "org_name", "repo_name").parse_bodies()
        == """*CATEGORY1*
• DESCRIPTION_1 <https://github.com/org_name/repo_name/pull/1|PR-1>

"""
    )


def test_changelog_note_uncategorized():
    pull_request_dict = {
        "number": 1,
        "body": "RELEASES\nDESCRIPTION_1",
        "labels": [],
    }
    assert (
        ChangeLog([pull_request_dict], "org_name", "repo_name").parse_bodies()
        == """*Uncategorized*
• DESCRIPTION_1 <https://github.com/org_name/repo_name/pull/1|PR-1>

"""
    )


def test_changelog_note_multiple_lines():
    pull_request_dict = {
        "number": 1,
        "body": "RELEASES\nSentence1. Sentence 2.\nSentence 3.",
        "labels": [],
    }

    # I'm not married to this particular format.
    # It may be better to keep newlines instead of transforming them into spaces.
    # After all, the bullet points distinugish between different PR's.
    assert (
        ChangeLog([pull_request_dict], "org_name", "repo_name").parse_bodies()
        == """*Uncategorized*
• Sentence1. Sentence 2. Sentence 3. <https://github.com/org_name/repo_name/pull/1|PR-1>

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


def test_changelog_with_multiple_notes():
    pull_request_dicts = [
        {
            "number": 1,
            "body": "RELEASES\nDESCRIPTION_1",
            "labels": ["feat-CATEGORY1"],
        },
        {
            "number": 5,
            "body": "RELEASES\nfoo",
            "labels": ["feat-CATEGORY1"],
        },
        {
            "number": 2,
            "body": "RELEASES\nDESCRIPTION_2",
            "labels": ["feat-CATEGORY2"],
        },
        {
            "number": 6,
            "body": "RELEASES\nfah",
            "labels": ["feat-CATEGORY2"],
        },
    ]
    assert (
        ChangeLog(pull_request_dicts, "org_name", "repo_name").parse_bodies()
        == """*CATEGORY1*
• DESCRIPTION_1 <https://github.com/org_name/repo_name/pull/1|PR-1>
• foo <https://github.com/org_name/repo_name/pull/5|PR-5>

*CATEGORY2*
• DESCRIPTION_2 <https://github.com/org_name/repo_name/pull/2|PR-2>
• fah <https://github.com/org_name/repo_name/pull/6|PR-6>

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
