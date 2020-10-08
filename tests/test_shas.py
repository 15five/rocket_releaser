from os import path
import tempfile
from random import randint
import shutil
import subprocess
from git import Repo
from rocket_releaser.shas import branch_exists, SHAs

cherry_pick_commit_msg = """commit 3f9ba302b9d440caba0fc2ba1f19e3614e46a7f1
feature

(cherry picked from commit c8e9114beabca79e4497f9ea40499c80cebe902a)"""

# These are 20 actual commits from fifteen5 repo
commit_msgs = """commit 6bc22dacce6aa6d036ca58bcbed23aceff61609e
Merge pull request #22344 from 15five/ENG-1357-Question-templates-not-cloned-appropriately

Clone questions templates correctly [ENG-1357]
commit d59a711dbc5278d35dff1c926ece789219e4aef4
Merge pull request #22402 from 15five/dev

__2019-03-05.0 - to staging
commit 90b079b9cf0f2d28fec37387d8f45f13ec38e829
Fix my team filtering in BSRs

commit 0fa63c345191896add555d1d2fb0c56023ab4838
Merge pull request #22407 from 15five/hotfix-staging-2019-03-05.0

__2019-03-05.1 - to staging (hotfix)
commit 0640274e4d0ddabc7ccc8e2a5d70b75ae758b946
Better SCIM logging

commit 094b0de3f41c235e2a3d5ac29475c9376aae715b
Merge pull request #22414 from 15five/staging-hf

__2019-03-05.2 - to staging (hotfix)
commit 8fb0524f8011e39c27afd2e37965df7123a20b58
Exclude smart groups when saving UserEditForm

[ENG-1546]
"""


def commit_random_file(branch="master"):
    # see https://gitpython.readthedocs.io/en/stable/tutorial.html
    filename = str(randint(0, 999999999))
    new_file_path = path.join(repo.working_tree_dir, filename)
    open(new_file_path, "wb").close()  # create new file in working tree
    repo.index.add([new_file_path])  # add it to the index
    # Commit the changes to deviate masters history
    return repo.index.commit("Added " + filename)


tmp_dirpath = None
repo = None
first_commit = None
shas = None


def setup_module():
    global repo
    global first_commit
    global shas
    global tmp_dirpath
    tmp_dirpath = tempfile.mkdtemp()
    repo = Repo.init(tmp_dirpath)
    repo.git.config("user.email", "test_user@example.com")
    repo.git.config("user.name", "test_user")
    first_commit = commit_random_file()
    shas = SHAs(tmp_dirpath)


def test_get_shas_internal():
    shas_list = shas._get_shas(commit_msgs)
    assert len(shas_list) == 7


def test_cherry_picked_sha():
    shas_list = shas._get_shas(cherry_pick_commit_msg)
    assert len(shas_list) == 2
    assert shas_list[0] == "3f9ba302b9d440caba0fc2ba1f19e3614e46a7f1"
    assert shas_list[1] == "c8e9114beabca79e4497f9ea40499c80cebe902a"


def test_get_shas_empty_when_no_changes():
    my_shas = shas.get_shas(first_commit.hexsha, first_commit.hexsha)
    assert not my_shas


def test_old_commit_in_shas():
    # a old commit should still be in shas even if chronologically before last deploy

    # create & checkout (-b) branch
    branch_name = "old_branch"
    repo.git.checkout("-b", branch_name)

    # create old commit
    old_commit = commit_random_file(branch=branch_name)

    # create newer commit (realistically this would be another merge, but doesn't matter)
    # we pretend user has deployed this commit
    repo.git.checkout("master")
    last_deployed_commit = commit_random_file()

    # merge old commit into master
    repo.git.merge(branch_name)

    # pretend user deployed "old" commit

    my_shas = shas.get_shas(last_deployed_commit.hexsha, repo.head.commit.hexsha)
    assert my_shas
    assert old_commit.hexsha in my_shas
    assert last_deployed_commit.hexsha not in my_shas
    # ^ already been deployed, we don't want to log release notes of this commit
    assert repo.head.commit.hexsha in my_shas
    # ^ sanity check


def test_not_in_range():
    assert not shas.get_shas("nonexistant sha", "nonexistant sha")


def test_branch_exists():
    assert branch_exists(tmp_dirpath, "master")
    assert not branch_exists(
        tmp_dirpath, "did-you-know-that-cashews-came-from-a-fruit?"
    )


def teardown_module():
    repo.close()
