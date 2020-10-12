import argparse
import datetime
import logging
import re
import subprocess
from sys import stdout, argv
from typing import List

from .changelog import ChangeLog
from .prs import PRs
from .shas import branch_exists, SHAs
from .slack import post_deployment_message_to_slack
from .ticket_labeler import TicketLabeler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def turn_changelog_into_string(
    pull_request_dicts: List[dict],
    env_name: str,
    from_revision: str,
    to_revision: str,
    num_jira_tickets: int,
    org_name: str,
    repo_name: str,
):

    changelog = ChangeLog(pull_request_dicts, org_name, repo_name).parse_bodies()

    link = (
        f"<https://github.com/{org_name}/{repo_name}/compare/{from_revision[:7]}...{to_revision[:7]}|"
        f"{from_revision[:7]}...{to_revision[:7]}>"
    )
    now_str = datetime.datetime.now().isoformat(" ")
    title_line = f"*{env_name.upper()} RELEASE* {now_str} ({link})"

    # assumes that env_name is the same as the branch name
    # currently for 15Five this assumption works (only difference is dev/preview but that doesnt get hotfixes)
    is_hotfix = any(
        [
            "hotfix" in pr.get("title", "").lower()
            and env_name.lower() in pr.get("title", "").lower()
            for pr in pull_request_dicts
        ]
    )

    if is_hotfix:
        title_line = ":fire: *HOTFIX* :fire: " + title_line

    messages = [
        title_line,
        f"{num_jira_tickets} jira tickets found.",
        f"{len(changelog.pull_request_dicts)} PRs found.",
    ]

    if from_revision == to_revision:
        messages.append(
            "Start and end commit hashes are the same - no changes for release notes to log"
        )
        return "\n".join(messages)

    attr_names_and_category_names = [
        ("noteworthy", "Noteworthy Changes"),
        ("features", "Features"),
        ("fixes", "Fixes"),
    ]

    for attr_name, category_name in attr_names_and_category_names:
        category_items = getattr(changelog, attr_name)
        if category_items:
            messages.append(f"\n*{category_name}*")
            messages.extend(category_items)

    if changelog.qa_notes and env_name.lower() in ("preview", "staging"):
        messages.append("\n*Notes for QA*")
        messages.extend(changelog.qa_notes)

    text = "\n".join(messages)

    return text


def release_notes(
    github_token: str,
    from_revision: str,
    to_revision: str,
    org_name: str,
    repo_name: str,
    repo_dir: str = None,
    search_branch: str = "master",
    slack_webhook_key: str = "",
    env_name: str = "prod",
    vpc_name: str = "prod",
    jira_token: str = "",
    jira_username: str = "",
    jira_url: str = "",
    label_tickets=True,
    verbose=False,
    dry_run=False,
    fetch_before=True,
):

    if not repo_dir:
        repo_dir = get_default_repo_dir()

    if not branch_exists(repo_dir, search_branch):
        raise ValueError(search_branch + " branch does not exist in " + repo_dir)

    logger.info(
        f"Pulling deploy SHAs from {search_branch} branch in {repo_dir}. {from_revision}...{to_revision}"
    )
    deploy_shas = SHAs(repo_dir, fetch_before).get_shas(
        from_revision, to_revision, branch=search_branch
    )

    logger.info(f"Pulling PR bodies from GitHub. Searching {len(deploy_shas)} SHAs.")
    prs = PRs(github_token, org_name, repo_name)

    # Shas might be associated with unmerged pr's if the pr rebased itself to include that sha
    # We only want merged pr's
    pull_request_dicts = [
        pr for pr in prs.pull_request_dicts(deploy_shas) if pr["merged"]
    ]

    num_jira_tickets: int = 0

    if label_tickets:
        ticket_labeler = TicketLabeler(
            github_token,
            pull_request_dicts,
            org_name,
            repo_name,
            jira_token,
            jira_username,
            jira_url,
        )
        num_jira_tickets = ticket_labeler.label_tickets(
            env_name, vpc_name, dry_run=dry_run
        )
        logger.info(f"labeled {num_jira_tickets} tickets")

    slack_text = turn_changelog_into_string(
        pull_request_dicts,
        env_name,
        from_revision,
        to_revision,
        num_jira_tickets,
        org_name,
        repo_name,
    )

    if verbose:
        print(slack_text)

    if dry_run:
        return slack_text

    if slack_webhook_key:
        logger.info(f"Pushing ChangeLog data to {env_name} Slack channel.")
        post_deployment_message_to_slack(slack_webhook_key, slack_text)
    else:
        logger.warning("no slack webhook key. Not pushing to slack.")

    logger.info("Done.")

    return slack_text


def get_default_repo_dir():
    try:
        get_repo_dir_command = ["git", "rev-parse", "--show-toplevel"]
        repo_dir: str = subprocess.check_output(get_repo_dir_command).decode("utf-8")
        return repo_dir.strip()
    except subprocess.CalledProcessError:
        raise ValueError("You are not in a git repo - please specify git repo")


def main(args: List[str]):
    parser = argparse.ArgumentParser()
    parser.add_argument("github_token", help="GitHub API token")
    parser.add_argument("from_revision")
    parser.add_argument("to_revision")
    parser.add_argument("org_name")
    parser.add_argument("repo_name")
    parser.add_argument(
        "-r",
        "--repo_dir",
        help=f"Defaults to current repo if you are inside a repository",
        default="",
    )
    parser.add_argument(
        "-b", "--search_branch", help='Default is "master"', default="master"
    )
    parser.add_argument(
        "-s",
        "--slack_webhook_key",
        help='Eg. "ABC457E/FElF56789FE/FLIELAJFLKAJLKEFFE"',
        default="",
    )
    parser.add_argument("-e", "--env_name", help='Eg. "prod"', default="prod")
    parser.add_argument(
        "-V",
        "--vpc_name",
        help='Eg. "prod_1". If you dont have a VPC use the same value as env_name.',
        default="prod",
    )
    parser.add_argument(
        "-l",
        "--dont_label_tickets",
        help="if you skip labeling tickets the jira token wont matter",
        action="store_false",
        dest="label_tickets",
        default=True,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        default=False,
    )
    parser.add_argument(
        "-d",
        "--dry_run",
        action="store_true",
        dest="dry_run",
        default=False,
    )
    parser.add_argument(
        "--skip-fetch",
        action="store_false",
        dest="fetch_before",
        default=True,
    )
    parser.add_argument("--jira_token", help="Jira API token", default="")
    parser.add_argument("--jira_username", help='Eg. "bob@company.com"', default="")
    parser.add_argument(
        "--jira_url", help='Eg. "https://company.atlassian.net"', default=""
    )

    parsed_args = parser.parse_args(args)

    logger.info(
        "Running release notes script with following options: "
        + str(
            {
                "github_token": "CENSORED",
                "from_revision": parsed_args.from_revision,
                "to_revision": parsed_args.to_revision,
                "org_name": parsed_args.org_name,
                "repo_name": parsed_args.repo_name,
                "repo_dir": parsed_args.repo_dir,
                "search_branch": parsed_args.search_branch,
                "slack_webhook_key": "CENSORED",
                "env_name": parsed_args.env_name,
                "vpc_name": parsed_args.vpc_name,
                "label_tickets": parsed_args.label_tickets,
                "verbose": parsed_args.verbose,
                "dry_run": parsed_args.dry_run,
                "fetch_before": parsed_args.fetch_before,
                "jira_token": "CENSORED",
                "jira_username": parsed_args.jira_username,
                "jira_url": parsed_args.jira_url,
            }
        )
    )

    if parsed_args.verbose:
        logger.setLevel(logging.DEBUG)

    return release_notes(
        parsed_args.github_token,
        parsed_args.from_revision,
        parsed_args.to_revision,
        parsed_args.org_name,
        parsed_args.repo_name,
        repo_dir=parsed_args.repo_dir,
        search_branch=parsed_args.search_branch,
        slack_webhook_key=parsed_args.slack_webhook_key,
        env_name=parsed_args.env_name,
        vpc_name=parsed_args.vpc_name,
        jira_token=parsed_args.jira_token,
        jira_username=parsed_args.jira_username,
        jira_url=parsed_args.jira_url,
        label_tickets=parsed_args.label_tickets,
        verbose=parsed_args.verbose,
        dry_run=parsed_args.dry_run,
    )
