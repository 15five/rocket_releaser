import logging
import re
from typing import List

import github3
import jira

from .prs import PRs

logger = logging.getLogger(__name__)


class TicketLabeler:
    """
    class for labeling github/jira pr's/tickets
    """

    # you can find more transition id's with the following code:
    """
    import jira
    import json
    jira = jira.JIRA('https://yourJira.atlassian.net', basic_auth=('your_account@company.com', 'JIRA SECRET'))
    issue = jira.issue('DEV-91') # replace this number with issue you want to get availible transitions for
    # keep in mind isssues in different states may have different transitions!
    transitions=[(t['name'], t['id']) for t in jira.transitions(issue)]
    d = dict(transitions)
    print(json.dumps(d, indent=4 ,sort_keys=True))
    """

    TRANSITION_IDS = {
        "Backlog": "871",
        "Blocked": "831",
        "Close": "851",
        "Code Review": "771",
        "Deployed": "861",
        "Ready to Test": "841",
        "Reopen Issue": "811",
        "Start Progress": "801",
        "Start Testing": "791",
        "Stop progress": "821",
    }

    TRANSITION_KEYWORDS = [
        "close",
        "closes",
        "closed",
        "fix",
        "fixes",
        "fixed",
        "resolve",
        "resolves",
        "resolved",
    ]

    JIRA_INFO_RE = re.compile(
        r"""
        (?P<transition>{transition_kw_options})?  # optional keywords that mark Jira transitions
        \s*                                       # optional whitespace character
        (?P<issue>\[*[A-Z]{{2,}}-\d+\]*)          # Jira issue name. Match examples: [ENG-123], ENG-123, DIV-1234
    """.format(
            transition_kw_options="|".join(TRANSITION_KEYWORDS)
        ),
        flags=re.VERBOSE | re.IGNORECASE,
    )

    PREVIEW_ENV_NAME: str = "preview"
    STAGING_ENV_NAME: str = "staging"
    PRODUCTION_ENV_NAME: str = "production"

    def __init__(
        self,
        githubToken: str,
        pull_request_dicts: List[dict],
        repo_owner: str,
        repo_name: str,
        jira_token: str = "",
        jira_username: str = "",
        jira_url: str = "",
    ):
        """
        :param githubToken: GitHub oauth githubToken
        """
        self.githubToken = githubToken
        self.pull_request_dicts = pull_request_dicts
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.jira_token = jira_token
        self.jira_url = jira_url
        self.gh = github3.GitHub(token=self.githubToken)

        # documentation claims you need to use username/password combo but username/token works as well
        if jira_token:
            self.jira = jira.JIRA(jira_url, basic_auth=(jira_username, self.jira_token))

    def label_tickets(self, env_name: str, vpc_name: str, dry_run=False) -> int:
        """
        labels github pr's and associated jira tickets with env_name.
        Note that if env_name matches self.PRODUCTION_ENV_NAME the jira issue will be closed

        :param env_name: the name of the vpc to label the tickets/issues with
        :return: number of jira tickets found
        """
        if dry_run:
            logger.info("Dry run - not actually making any changes")

        jira_ticket_name_list = []

        label: str = f"{vpc_name}({env_name})" if vpc_name != env_name else env_name

        for pr in self.pull_request_dicts:

            title = pr.get("title")
            pr_num = pr.get("number")

            try:
                logger.info(
                    f"labeling pr #{pr_num} {title} at "
                    f"https://github.com/{self.repo_owner}/{self.repo_name}/pull/{pr_num} with {label}"
                )
                if not dry_run:
                    self.label_pr_or_issue(pr, label)

            except github3.exceptions.GitHubException:
                logger.exception("Error during labeling: ")

            if not self.jira_token:
                continue

            jira_ticket_maps = []
            jira_ticket_maps_title = self.get_jira_ticket_maps(pr.get("title", ""))
            jira_ticket_maps_body = self.get_jira_ticket_maps(pr.get("body", ""))

            for jira_ticket_map_title in jira_ticket_maps_title:
                jira_ticket_maps.append(jira_ticket_map_title)

            for jira_ticket_map_body in jira_ticket_maps_body:
                if jira_ticket_map_body.get("transition"):
                    jira_ticket_maps.append(jira_ticket_map_body)
                # we ignore tickets without transition in body because they may be unrelated
                # ex: "this story is similar to ENG-4235" ~ we dont want to label ENG-4235

            if not jira_ticket_maps:
                logger.warning(f"couldnt find jira # in pr #{pr_num} {title}")
                continue

            # ugly hack ~ by converting to dict & back we ensure we dont have duplicate issues
            # (same issue may be mentioned in title and again in body)
            jira_ticket_maps = list(
                {map["issue"]: map for map in jira_ticket_maps}.values()
            )

            for jira_ticket_map in jira_ticket_maps:
                jira_ticket_name = jira_ticket_map.get("issue")
                transition_kw = jira_ticket_map.get("transition")

                try:
                    if jira_ticket_name not in jira_ticket_name_list:
                        jira_ticket_name_list.append(jira_ticket_name)
                    logger.info(
                        f"labeling jira ticket at {self.jira_url}/browse/{jira_ticket_name}"
                        f" with {label}"
                    )
                    issue = self.jira.issue(jira_ticket_name)

                    # a ticket may have more than one PR
                    # so we only transition if final PR
                    if transition_kw:

                        if env_name == self.PREVIEW_ENV_NAME:
                            logger.info(
                                "env_name matches preview - making sure if ticket is still in progress "
                                "its marked in review"
                            )
                            if not dry_run:
                                self.mark_in_review_jira_ticket(issue)

                        elif env_name == self.STAGING_ENV_NAME:
                            logger.info(
                                "env_name matches staging - marking jira ticket as ready to test"
                            )
                            if not dry_run:
                                self.mark_ready_test_jira_ticket(issue)

                        # we don't have enough qa currently to test everything before it goes to prod
                        # so we don't close the ticket when it hits prod in case it still needs testing
                        # elif env_name == self.PRODUCTION_ENV_NAME:
                        #     logger.info('env_name matches production - closing jira ticket')
                        #     if not dry_run:
                        #         self.mark_deployed_jira_ticket(issue)

                    if not dry_run:
                        # this HAS to be last because you cant add labels to closed issue
                        self.label_jira_ticket(issue, jira_ticket_name, label)

                except (jira.exceptions.JIRAError, ValueError):
                    logger.exception("error with " + str(title))

        return len(jira_ticket_name_list)

    @staticmethod
    def get_jira_ticket_maps(search_string: str) -> List[dict]:
        """
        Looks for all Jira related information in a string, including transition keywords and ticket number.

        Will match the following strings:
            * '[ENG-123]'
            * 'ENG-123'
            * 'eng-12345'
            * 'closes DEV-1234`
            * 'Fixes DS-123'

        Note: The 'issue' value is always returned _without_ brackets.

        :param search_string: str that will be searched for all Jira information.
        :return: List of dictionaries, each having the keys 'issue' and 'transition'
        """
        cleaned_info_list = []
        for match_object in TicketLabeler.JIRA_INFO_RE.finditer(search_string):
            info_dict = match_object.groupdict()

            # lowercase the transition keyword if it is found
            transition = info_dict.get("transition")
            if transition:
                transition = transition.lower()

            # remove brackets and uppercase the issue name
            issue = info_dict.get("issue", "").replace("[", "").replace("]", "").upper()

            # edge case: 1-on-1 looks like a issue to regex, so we filter that out
            # alternatively we could require brackets surrounding issue
            if issue == "ON-1":
                continue

            cleaned_dict = {"transition": transition, "issue": issue}
            cleaned_info_list.append(cleaned_dict)

        return cleaned_info_list

    def label_pr_or_issue(self, pr: dict, label: str):
        """
        :param pr: dict with number key mapping to a string
        """
        pr_num = pr.get("number")
        issue = self.gh.issue(self.repo_owner, self.repo_name, pr_num)
        issue.add_labels(label)

    def label_jira_ticket(self, issue, ticket_name, label):

        if " " in label:
            raise ValueError("labels can't have spaces!")

        if label not in issue.fields.labels:
            issue.update(fields={"labels": issue.fields.labels + [label]})

        return issue

    def mark_deployed_jira_ticket(self, issue: jira.Issue):
        """
        Closes w/ comment then marks as deployed
        """
        if issue is None:
            raise TypeError("issue is None - issue should be of type jira.Issue")

        if (
            issue.fields.status.name != "Closed"
            and issue.fields.status.name != "Deployed"
        ):
            self.jira.transition_issue(
                issue,
                self.TRANSITION_IDS["Close"],
                fields={"resolution": {"name": "Done"}},
                comment="auto transitioned by deploy",
            )

        if issue.fields.status.name != "Deployed":
            # Note that you can't comment when transitioning to Deployed status
            self.jira.transition_issue(
                issue, self.TRANSITION_IDS["Deployed"], comment=""
            )

    def mark_ready_test_jira_ticket(self, issue: jira.Issue):
        """
        :param issue: jira Issue
        """
        if issue is None:
            raise TypeError("issue is None - issue should be of type jira.Issue")

        if issue.fields.status.name in ("Reopened", "Open", "In Progress", "In Review"):
            self.jira.transition_issue(issue, self.TRANSITION_IDS["Ready to Test"])

    def mark_in_review_jira_ticket(self, issue: jira.Issue):
        """
        :param issue: jira Issue
        """
        if issue is None:
            raise TypeError("issue is None - issue should be of type jira.Issue")

        if issue.fields.status.name in ("Reopened", "Open", "In Progress"):
            self.jira.transition_issue(issue, self.TRANSITION_IDS["Code Review"])
