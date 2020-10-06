# Release Notes
Library for creating release notes based on PR descriptions for a set of git changes

Example:
```shell
python release_notes.py github_token start_sha end_sha github_org github_repo -r repo_location --vpc_name staging --env_name staging --search_branch staging --slack_webhook_key slack_key
```

This would label PR's  inbetween first and second sha with "staging" and send the release notes to slack.
If you are using a personal github account the "github_org" would be your github username.

You can also pass in jira paramaters to label jira tickets.
`--jira_token jiraToken --jira_username bob@company.com --jira_url https://company.atlassian.net`

The github token must have "repo" scope access and the token's user must have write access to the repo.
