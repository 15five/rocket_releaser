import subprocess
import logging
from os import path
from typing import List
import re

logger = logging.getLogger(__name__)


def branch_exists(repo_dir: str, branch_name: str):
    try:
        base_args = ["git", f'--git-dir={path.join(repo_dir, ".git")}']
        subprocess.check_call(
            base_args + ["show-ref", "--verify", "--quiet", "refs/heads/" + branch_name]
        )
        return True
    except subprocess.CalledProcessError:
        return False


class SHAs:
    def __init__(self, repo_dir: str, fetch_before: bool = True):
        """
        :param fetch_before: Whether to fetch branch to make sure you have it when calling for_branch.
        """

        self.fetch_before = fetch_before

        self.base_args = [
            "git",
            f'--git-dir={path.join(repo_dir, ".git")}',
            f"--work-tree={repo_dir}",
        ]

    def get_shas(
        self, from_revision: str, to_revision: str, branch: str = "master"
    ) -> List[str]:
        """
        Get SHAs from from_revision to to_revision.
        :param branch: Branch to pull commits from.
        """

        if self.fetch_before:
            fetch_args = self.base_args + [
                "fetch",
                "origin",
                f"{branch}:{branch}",
                "--update-head-ok",
            ]

            try:
                subprocess.check_output(fetch_args)
                logger.debug(f"Pulled branch with the following args: {fetch_args}")
            except subprocess.CalledProcessError:
                logger.exception("subprocess call failed")

        rev_list_args = self.base_args + [
            "rev-list",
            # https://stackoverflow.com/questions/7251477/what-are-the-differences-between-double-dot-and-triple-dot-in-git-dif
            # to be honest not sure what difference is between .. and ... when on same branch
            # but staying with ... to be on safe side because it includes more
            # I didn't find any differences when doing manual tests
            from_revision + "..." + to_revision,
            "--format=%B",  # raw body (unwrapped subject and body) https://git-scm.com/docs/git-rev-list
        ]

        try:
            commit_msgs = subprocess.check_output(rev_list_args).decode("utf-8")
        except subprocess.CalledProcessError:
            logger.exception("subprocess call failed")
            commit_msgs = ""

        logger.debug(f"rev-list commit messages: {commit_msgs}")

        shas = self._get_shas(commit_msgs)

        logger.debug(f"rev-list SHAs: {shas}")

        return shas

    def _get_shas(self, commit_msgs: str) -> List[str]:
        """returns shas, inlcuding cherry-picked shas"""

        shas = []

        for line in commit_msgs.split("\n"):

            line = line.rstrip("\r")

            if re.match(r"commit \w+$", line):
                shas.append(line.replace("commit ", ""))

            if line.startswith("(cherry picked from commit "):
                shas.append(line.replace("(cherry picked from commit ", "").rstrip(")"))

        return shas
