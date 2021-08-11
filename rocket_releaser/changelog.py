from collections import defaultdict
import re
import logging
from typing import DefaultDict, List

logger = logging.getLogger(__name__)


class ChangeLog:
    def __init__(
        self, pull_request_dicts: List[dict], org_name: str, repo_name: str, jira_url=""
    ):
        self.pull_request_dicts = pull_request_dicts

        self.features = []
        self.org_name = org_name
        self.repo_name = repo_name
        self.jira_url = jira_url

    @property
    def release_bodies(self):
        return [
            (pr.get("number"), pr.get("body"), pr.get("labels"))
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
        return f"{line} <https://github.com/{org_name}/{repo_name}/pull/{pr_number}|PR-{pr_number}>"

    @staticmethod
    def add_jira_link(line: str, jira_url: str):
        return re.sub(
            r"\[(\w+-\d+)\]",
            lambda match: f"<{jira_url}/browse/{match.group(1)}|{match.group(1)}>",
            line,
        )

    @staticmethod
    def linkify(
        org_name: str, repo_name: str, line: str, pr_number, jira_url: str = ""
    ):
        """add jira & github links"""

        if jira_url:
            line = ChangeLog.add_jira_link(line, jira_url)
        line = ChangeLog.add_github_link(org_name, repo_name, line, pr_number)
        return line

    @staticmethod
    def extract_notes_from_pr(pr_body: str, header: str):
        """
        Extracts the block of text under a specified header
        """
        # Remove HTML comments. Will not work in all cases.
        lines = re.sub("<!--.+?>", "", pr_body, flags=re.DOTALL)
        lines = lines.strip().split("\n")
        # Clean lines up
        lines = list(map(lambda line_: line_.strip().lstrip("-").strip(), lines))

        features = ""
        collecting_releases = False
        for line in lines:
            if collecting_releases and not line:
                # No more lines in RELEASES block
                break

            if collecting_releases:
                features = features + " " + line

            if not collecting_releases and line.lower().startswith(header):
                collecting_releases = True

        return features

    @staticmethod
    def extract_category_from_pr(labels: List[str], category_indicator: str):
        for label in labels:
            if label.startswith(category_indicator):
                return label.replace(category_indicator, "")
        return "Uncategorized"

    def parse_bodies(self):
        notes_by_category: DefaultDict[str, List[str]] = defaultdict(list)
        for pr_number, body, labels in self.release_bodies:
            features = ChangeLog.extract_notes_from_pr(body, "release")
            linky_features = self.linkify(
                self.org_name,
                self.repo_name,
                features,
                pr_number,
                self.jira_url,
            )
            category = ChangeLog.extract_category_from_pr(labels, "feat-")
            notes_by_category[category].append("•" + linky_features)

        release_notes = ""
        for category in notes_by_category:
            notes = "\n".join(notes_by_category[category])
            notes_section = f"*{category}*\n{notes}\n\n"
            release_notes += notes_section

        return release_notes
