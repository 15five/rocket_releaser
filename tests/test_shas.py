from os import path
import tempfile
from random import randint
import shutil
import subprocess
from git import Repo
from rocketReleaser.shas import SHAs

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

commit 2e8d42828588c7c323cd3a36bcd5c1885c39a4fd
Only show user's smart groups in edit_profile view

[ENG-1545]

commit 753726301745690d967429d4eda7fc021c517288
Merge pull request #22421 from 15five/staging-hotfix-2019-03-06.0

__2019-03-06.0 - to staging (hotfix)
commit 6f4977b8c67f44c100dc74aae2f710993fd24670
Correct labels

commit 3d14a5e9b7c27158b1f71de8c5d2fc36e4a4ea2e
Merge pull request #22425 from 15five/staging-hotfix-2019-03-06.1

__2019-03-06.1 - to staging (hotfix)
commit a0bba9e25323d92e8b77abec979a247f9c8a8af9
Add regression test

commit 5d1a05c4fcf3cecf7ac6a262d39396d5b4e068bc
Update SCIM patch methods

commit e62f19cf41c474d37db2acc31c84db9a056f58b3
Merge pull request #22431 from 15five/staging-hotfix-2019-03-07.0

__2019-03-07.0 - to staging (hotfix)
commit 5ddc8bb5473a4f9baf428b43646790674eb0cc2d
Fixed reviews cycle "days until" properties

commit 21653e48476752e82f3fd44558b6cead796092d9
Update front-end devDependencies

- babel 7.3.4 (from 7.3.1):

  https://github.com/babel/babel/releases/tag/v7.3.2
  https://github.com/babel/babel/releases/tag/v7.3.3
  https://github.com/babel/babel/releases/tag/v7.3.4

- autoprefixer 9.4.10 (from 9.4.7):

  https://github.com/postcss/autoprefixer/blob/9.4.10/CHANGELOG.md

- lint-staged 8.1.5 (from 8.1.3):

  https://github.com/okonet/lint-staged/releases/tag/v8.1.4
  https://github.com/okonet/lint-staged/releases/tag/v8.1.5

- stylelint-scss 3.5.4 (from 3.5.2):

  https://github.com/kristerkari/stylelint-scss/blob/3.5.4/CHANGELOG.md

- yargs 13.2.2 (from 12.0.5):

  https://github.com/yargs/yargs/blob/v13.2.2/CHANGELOG.md

- eslint 5.15.1 (from 5.13.0):

  https://github.com/eslint/eslint/releases/tag/v5.14.0
  https://github.com/eslint/eslint/releases/tag/v5.14.1
  https://github.com/eslint/eslint/releases/tag/v5.15.0
  https://github.com/eslint/eslint/releases/tag/v5.15.1

- eslint-config-prettier 4.1.0 (from 4.0.0):

  https://github.com/prettier/eslint-config-prettier/blob/v4.1.0/CHANGELOG.md

- jest 24.1.0 (from 24.0.0):

  https://github.com/facebook/jest/blob/v24.1.0/CHANGELOG.md

- js-beautify 1.9.0 (from 1.8.9):

  https://github.com/beautify-web/js-beautify/blob/v1.9.0/CHANGELOG.md

- rollup 1.4.1 (from 1.1.2):

  https://github.com/rollup/rollup/blob/v1.4.1/CHANGELOG.md

- rollup-plugin-node-resolve 4.0.1 (from 4.0.0):

  https://github.com/rollup/rollup-plugin-node-resolve/blob/v4.0.1/CHANGELOG.md

`rollup-plugin-commonjs` and `rollup-pluginutils` are intentionally
omitted.

commit b0a11349a22414a5567713470a0e9791cc182b1f
Update front-end dependencies

- d3-shape 1.3.4 (from 1.3.3):

  https://github.com/d3/d3-shape/releases/tag/v1.3.4

- details-element-polyfill 2.3.1 (from 2.3.0):

  https://github.com/javan/details-element-polyfill/releases/tag/2.3.1

- dompurify 1.0.10 (from 1.0.9):

  https://github.com/cure53/DOMPurify/releases/tag/1.0.10

- downshift 3.2.6 (from 3.2.2):

  https://github.com/downshift-js/downshift/releases/tag/v3.2.3
  https://github.com/downshift-js/downshift/releases/tag/v3.2.4
  https://github.com/downshift-js/downshift/releases/tag/v3.2.5
  https://github.com/downshift-js/downshift/releases/tag/v3.2.6

- marked 0.6.1 (from 0.6.0):

  https://github.com/markedjs/marked/releases/tag/v0.6.1

- react 16.8.4 (from 16.8.2):

  https://github.com/facebook/react/blob/v16.8.4/CHANGELOG.md

- selector-observer 2.1.5 (from 2.1.3):

  https://github.com/josh/selector-observer/compare/v2.1.3...v2.1.5

- vue 2.6.8 (from 2.5.22):

  https://medium.com/the-vue-point/vue-2-6-released-66aa6c8e785e
  https://github.com/vuejs/vue/releases/tag/v2.6.0
  https://github.com/vuejs/vue/releases/tag/v2.6.1
  https://github.com/vuejs/vue/releases/tag/v2.6.2
  https://github.com/vuejs/vue/releases/tag/v2.6.3
  https://github.com/vuejs/vue/releases/tag/v2.6.4
  https://github.com/vuejs/vue/releases/tag/v2.6.5
  https://github.com/vuejs/vue/releases/tag/v2.6.6
  https://github.com/vuejs/vue/releases/tag/v2.6.7
  https://github.com/vuejs/vue/releases/tag/v2.6.8

- what-input 5.1.4 (from 5.1.3):

  https://github.com/ten1seven/what-input/releases/tag/v5.1.4

Vue 2.6.1 fixes parsing single-quotes in HTML attributes.

commit b549cf445a35cff49862cf6ca87267f91c495126
Use Vue 2.6's `v-slot` directive

Replaces deprecated `[slot-scope]` attribute.

https://vuejs.org/v2/api/#v-slot

commit 2e158fc2b0f202e0398dad60214b0f75477bc522
Use `rollup-plugin-terser` for rollup modules

Replaces `rollup-plugin-uglify`.

https://github.com/TrySound/rollup-plugin-terser

This matches what `rollup` itself does:

https://github.com/rollup/rollup/pull/2437

commit 7900b87d14635fbec6cce14c1de89337b73c9b3a\r
Merge pull request #22437 from 15five/staging-hotfix-2019-03-07.1

__2019-03-07.1 - to staging (hotfix)

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
    assert len(shas_list) == 20


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


def teardown_module():
    repo.close()
