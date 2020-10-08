import re
import logging
from typing import List

logger = logging.getLogger(__name__)


class ChangeLog:
    def __init__(
        self, pull_request_dicts: List[dict], org_name: str, repo_name: str, jira_url=""
    ):
        self.pull_request_dicts = pull_request_dicts

        self.features = []
        self.fixes = []
        self.noteworthy = []
        self.qa_notes = []
        self.org_name = org_name
        self.repo_name = repo_name
        self.jira_url = jira_url

    @property
    def release_bodies(self):
        return [
            (pr.get("number"), pr.get("body"))
            for pr in self.pull_request_dicts
            if "release" in pr.get("body").lower()
        ]

    @staticmethod
    def is_noteworthy(line: str):
        return "[" in line

    @staticmethod
    def is_fix(line: str):
        line = line.lower()
        return "fixes [" in line or line.startswith("fix")

    @staticmethod
    def add_github_link(org_name: str, repo_name: str, line, pr_number):
        return f"{line} PR: <https://github.com/{org_name}/{repo_name}/pull/{pr_number}|{pr_number}>"

    @staticmethod
    def add_jira_link(line: str, jira_url: str):
        return re.sub(
            r"\[(\w+-\d+)\]",
            lambda match: f"<{jira_url}/browse/{match.group(1)}|{match.group(1)}>",
            line,
        )

    @staticmethod
    def linkify(org_name: str, repo_name: str, line: str, pr_number, jira_url=""):
        """add jira & github links"""

        if jira_url:
            line = ChangeLog.add_jira_link(line, jira_url)
        line = ChangeLog.add_github_link(org_name, repo_name, line, pr_number)
        return line

    @staticmethod
    def make_jira_id_bold(line: str):
        return line.replace("[", "*[").replace("]", "]*")

    def parse_bodies(self):
        for pr_number, body in self.release_bodies:
            # Remove HTML comments. Will not work in all cases.
            lines = re.sub("<!--.+?>", "", body, flags=re.DOTALL)
            lines = lines.strip().split("\n")
            # Clean lines up
            lines = list(map(lambda line_: line_.strip().lstrip("-").strip(), lines))

            fixes = ""
            noteworthy = ""
            features = ""
            collecting_releases = False
            for line in lines:
                if collecting_releases and not line:
                    # No more lines in RELEASES block
                    break

                if collecting_releases:
                    if self.is_fix(line):
                        fixes = fixes + " " + line
                    elif self.is_noteworthy(line):
                        line = self.make_jira_id_bold(line)
                        noteworthy = noteworthy + " " + line
                    else:
                        features = features + " " + line

                if not collecting_releases and line.lower().startswith("release"):
                    collecting_releases = True

            if fixes:
                self.fixes.append(
                    self.linkify(
                        self.org_name, self.repo_name, fixes, pr_number, self.jira_url
                    )
                )
            if noteworthy:
                self.noteworthy.append(
                    self.linkify(
                        self.org_name,
                        self.repo_name,
                        noteworthy,
                        pr_number,
                        self.jira_url,
                    )
                )
            if features:
                self.features.append(
                    self.linkify(
                        self.org_name,
                        self.repo_name,
                        features,
                        pr_number,
                        self.jira_url,
                    )
                )

            qa_notes = ""
            collecting_qa_notes = False
            for line in lines:
                if collecting_qa_notes and not line:
                    # No more lines in QA block
                    break

                if collecting_qa_notes:
                    qa_notes = qa_notes + " " + line

                if not collecting_qa_notes and line.lower().startswith("qa"):
                    collecting_qa_notes = True

            if qa_notes:
                self.qa_notes.append(
                    self.linkify(
                        self.org_name,
                        self.repo_name,
                        qa_notes,
                        pr_number,
                        self.jira_url,
                    )
                )

        return self
