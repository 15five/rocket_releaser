import logging
from typing import List

from .graphql import GraphQL

logger = logging.getLogger(__name__)


class PRs:
    def __init__(self, token: str, repo_owner: str, repo_name: str):
        """
        :param token: GitHub oauth token
        """
        self.token = token
        self.repo_owner = repo_owner
        self.repo_name = repo_name

        self._request_dicts = None

    def clear_cache(self):
        self._request_dicts = None

    def pull_request_dicts(self, deploy_shas: List[str] = []) -> List[dict]:
        """
        gets PR's associated with deploy shas. Cached so calling multiple times won't result in unnecessary API calls.
        """

        # number of associatedPullRequests to pull is entirely arbitrary
        # 99% of cases it should only be 1 anyways
        query = """
query associatedPRs($sha: String, $repo: String!, $owner: String!){
  repository(name: $repo, owner: $owner) {
    commit: object(expression: $sha) {
      ... on Commit {
        associatedPullRequests(first:5){
          edges{
            node{
              title
              number
              body
              merged
            }
          }
        }
      }
    }
  }
}
"""

        if self._request_dicts is None:

            pull_request_dicts: List[dict] = []
            seen = {}

            graph_ql = GraphQL("https://api.github.com/graphql", self.token)

            deploy_shas = set(deploy_shas)  # get rid of duplicates

            for sha in deploy_shas:
                result = graph_ql.run_query(
                    query,
                    {"sha": sha, "repo": self.repo_name, "owner": self.repo_owner},
                )

                try:
                    # 'errors' key is only present in result if there is an error
                    logger.warning(
                        f"error with sha {sha}: " + result["errors"][0]["message"]
                    )
                    continue
                except KeyError:
                    pass

                try:
                    for edge in result["data"]["repository"]["commit"][
                        "associatedPullRequests"
                    ]["edges"]:
                        pr = edge["node"]
                        pr_num = pr["number"]

                        # for logging we record sha we got to this pr from
                        pr["deploy_sha"] = sha

                        # two commits may reference the same PR
                        if pr_num not in seen:
                            pull_request_dicts.append(pr)
                            seen[pr_num] = True
                except TypeError:
                    # this can happen if commit is cherry-picked from local commit not in repo
                    logger.warning(
                        "commit %s not found or has no associated PRs", sha, exc_info=1
                    )

            self._request_dicts = pull_request_dicts

        return self._request_dicts
