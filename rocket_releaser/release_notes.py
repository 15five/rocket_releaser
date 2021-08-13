import argparse
import json
import logging
import os
import subprocess
from string import Template
from typing import Any, Dict, List

from .changelog import ChangeLog
from .prs import PRs
from .shas import branch_exists, SHAs
from .slack import post_deployment_message_to_slack
from .ticket_labeler import TicketLabeler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_template_context(
    num_tickets: str,
    env_name: str,
    from_revision: str,
    to_revision: str,
    release_notes_format: Dict[str, Any],
    pull_request_dicts: List[Dict],
    org_name: str,
    repo_name: str,
):
    changelog = ChangeLog(pull_request_dicts, org_name, repo_name).parse_bodies()
    if from_revision == to_revision and not changelog:
        changelog = "Start and end commit hashes are the same - no changes for release notes to log"

    # assumes that env_name is the same as the branch name
    # currently for 15Five this assumption works (only difference is dev/preview but that doesnt get hotfixes)
    is_hotfix = any(
        [
            "hotfix" in pr.get("title", "").lower()
            and env_name.lower() in pr.get("title", "").lower()
            for pr in pull_request_dicts
        ]
    )
    hotfix_alert = release_notes_format["hotfix_alert_format"] if is_hotfix else ""

    env_name = env_name[0].upper() + env_name[1:]

    template_context: Dict[str, str] = {}
    template_context["NUM_TICKETS"] = num_tickets
    template_context["ENV"] = env_name
    template_context["RELEASE_NOTES"] = changelog
    template_context["NUM_PRS"] = str(len(pull_request_dicts))
    template_context["CHANGESET"] = f"{from_revision[:7]}...{to_revision[:7]}"
    template_context[
        "CHANGESET_LINK"
    ] = f"https://github.com/{org_name}/{repo_name}/compare/{template_context['CHANGESET']}"
    template_context["HOTFIX_ALERT"] = hotfix_alert

    return template_context


def get_config(repo_dir: str):
    script_directory = os.path.dirname(__file__)
    default_format_path = os.path.join(script_directory, "defaultFormat.json")
    with open(default_format_path) as f:
        release_notes_format: Dict[str] = json.load(f)
    try:
        custom_config_path = os.path.join(repo_dir, "rocket_releaser_format.json")
        with open(custom_config_path) as f:
            release_notes_format = json.load(f)
    except FileNotFoundError:
        logger.debug(f"Custom config not found in {repo_dir}, using default")
        pass
    return release_notes_format


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

    num_tickets: int = 0

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
        num_tickets = ticket_labeler.label_tickets(env_name, vpc_name, dry_run=dry_run)
        logger.info(f"labeled {num_tickets} tickets")

    release_notes_format = get_config(repo_dir)

    template_context = build_template_context(
        str(num_tickets),
        env_name,
        from_revision,
        to_revision,
        release_notes_format,
        pull_request_dicts,
        org_name,
        repo_name,
    )

    plaintext = Template(release_notes_format["plaintext_format"]).substitute(
        template_context
    )
    slack_format_string = json.dumps(release_notes_format["slack_format"])
    safe_context: Dict[str] = {}
    for key in template_context:
        # Prevent quotations marks or newlines from ruining JSON syntax
        safe_context[key] = (
            template_context[key].replace('"', '\\"').replace("\n", "\\n")
        )
    templated_string = Template(slack_format_string).substitute(safe_context)
    slack_blocks: Dict[str] = json.loads(templated_string)

    if verbose:
        print(plaintext)

    if dry_run:
        return plaintext

    if slack_webhook_key:
        logger.info(f"Pushing ChangeLog data to {env_name} Slack channel.")
        post_deployment_message_to_slack(slack_webhook_key, slack_blocks)
    else:
        logger.warning("no slack webhook key. Not pushing to slack.")

    logger.info("Done.")

    return plaintext


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
        help="If you skip labeling tickets the jira token won't matter",
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
                "slack_webhook_key": "CENSORED"
                if parsed_args.slack_webhook_key
                else "",
                "env_name": parsed_args.env_name,
                "vpc_name": parsed_args.vpc_name,
                "label_tickets": parsed_args.label_tickets,
                "verbose": parsed_args.verbose,
                "dry_run": parsed_args.dry_run,
                "fetch_before": parsed_args.fetch_before,
                "jira_token": "CENSORED" if parsed_args.jira_token else "",
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
