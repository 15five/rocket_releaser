from rocket_releaser.changelog import ChangeLog


def test_release_bodies_should_recognize_releases():
    pull_request_dict = {"number": 12, "body": "RELEASES\n closes [ENG-413]"}
    assert ChangeLog([pull_request_dict], "org_name", "repo_name").release_bodies


def test_release_bodies_should_recognize_not_releases():
    pull_request_dict = {"number": 12, "body": "bla bla bla"}
    assert not ChangeLog([pull_request_dict], "org_name", "repo_name").release_bodies


def test_parse_bodies_should_only_pick_up_release_block():
    pull_request_dict = {"number": 12, "body": "RELEASES\n closes [ENG-413]\n\nIGNORE"}

    c = ChangeLog([pull_request_dict], "org_name", "repo_name")
    c.parse_bodies()
    assert "IGNORE" not in c.features or c.fixes or c.noteworthy or c.qa_notes


def test_parse_bodies_should_recognize_noteworthy():
    pull_request_dict = {"number": 12, "body": "RELEASES\n closes [ENG-413]"}

    c = ChangeLog([pull_request_dict], "org_name", "repo_name")
    c.parse_bodies()
    assert c.noteworthy


def test_parse_bodies_should_recognize_not_noteworthy():
    pull_request_dict = {"number": 12, "body": "RELEASES\n bla bla bla"}

    c = ChangeLog([pull_request_dict], "org_name", "repo_name")
    c.parse_bodies()
    assert not c.noteworthy


# this test currently failing due to bug in code
# where line is line is recognized as noteworthy instead of fix
def test_parse_bodies_should_recognize_fix():
    pull_request_dict = {"number": 12, "body": "RELEASES\n fixes [ENG-413]"}

    c = ChangeLog([pull_request_dict], "org_name", "repo_name")
    c.parse_bodies()
    assert c.fixes


def test_parse_bodies_should_recognize_no_fix():
    pull_request_dict = {"number": 12, "body": "RELEASES\n closes [ENG-413]"}

    c = ChangeLog([pull_request_dict], "org_name", "repo_name")
    c.parse_bodies()
    assert not c.fixes


def test_parse_bodies_should_recognize_features():
    pull_request_dict = {"number": 12, "body": "RELEASES\n more foobar"}

    c = ChangeLog([pull_request_dict], "org_name", "repo_name")
    c.parse_bodies()
    assert c.features


def test_parse_bodies_should_recognize_no_features():
    pull_request_dict = {
        "number": 12,
        "body": "RELEASES\ncloses [ENG-413]\nfixes error",
    }

    c = ChangeLog([pull_request_dict], "org_name", "repo_name")
    c.parse_bodies()
    assert not c.features


def test_parse_bodies_should_recognize_qa_notes():
    pull_request_dict = {"number": 12, "body": "RELEASES bla\n\nqa\n more foobar"}

    c = ChangeLog([pull_request_dict], "org_name", "repo_name")
    c.parse_bodies()
    assert not c.noteworthy
    assert not c.fixes
    assert not c.features
    assert c.qa_notes


def test_parse_bodies_should_recognize_no_qa_notes():
    pull_request_dict = {"number": 12, "body": "RELEASES\n\nbla"}

    c = ChangeLog([pull_request_dict], "org_name", "repo_name")
    c.parse_bodies()
    assert not c.qa_notes


def test_parse_bodies_should_not_split_qa_notes():
    pull_request_dict = {"number": 12, "body": "RELEASES\n\nQA:\ndo this\n and that"}

    c = ChangeLog([pull_request_dict], "org_name", "repo_name")
    c.parse_bodies()
    assert len(c.qa_notes) == 1


def test_parse_bodies_should_add_jira_link():
    pull_request_dict = {"number": 12, "body": "RELEASES\n[DS-435]"}

    c = ChangeLog(
        [pull_request_dict],
        "org_name",
        "repo_name",
        jira_url="https://company.atlassian.net",
    )
    c.parse_bodies()
    assert "atlassian" in c.noteworthy[0]
