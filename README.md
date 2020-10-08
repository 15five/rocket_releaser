# Rocket Releaser [![CircleCI](https://circleci.com/gh/15five/rocket_releaser.svg?style=svg&circle-token=022a3a89718d088ac8a737b2d03280c4c1864ed0)](https://circleci.com/gh/15five/rocket_releaser) [![PyPI version](https://badge.fury.io/py/rocket_releaser.svg)](https://badge.fury.io/py/rocket_releaser)
Library for creating release notes based on PR descriptions for a set of git changes.

Example:
```shell
python -m rocket_releaser github_token start_sha end_sha github_org github_repo -r repo_location --vpc_name staging --env_name staging --search_branch staging --slack_webhook_key slack_key
```

This would label PR's inbetween first and second sha with "staging" and send the release notes to slack.
If you are using a personal github account the "github_org" would be your github username.

The github token must have "repo" scope access and the token's user must have write access to the repo.

You can also pass in Jira paramaters to label Jira tickets.

`--jira_token jiraToken --jira_username bob@company.com --jira_url https://company.atlassian.net`
