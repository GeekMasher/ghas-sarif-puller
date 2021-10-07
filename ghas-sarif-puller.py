#!/usr/bin/env python3

import os
import json
import logging
import argparse
import requests

logger = logging.getLogger("GHAS-SARIF-Puller")

parser = argparse.ArgumentParser("GHAS-SARIF-Puller")
parser.add_argument("--debug", action="store_true", help="Enable Debugging")

group_github = parser.add_argument_group("GitHub")
group_github.add_argument(
    "-r", "--repository", required=True, help="Repository full name (org/repo)"
)
group_github.add_argument(
    "-t",
    "--token",
    default=os.environ.get("GITHUB_TOKEN"),
    help="GitHub PAT (default: $GITHUB_TOKEN)",
)
# Optional
group_github.add_argument(
    "--ref", help="Git Reference / Branch (refs/heads/<branch name>)"
)

group_csv = parser.add_argument_group("SARIF")
group_csv.add_argument("-o", "--output", default="results.sarif")


def getGitHubRepositoryDefaultBranch(org: str, repo: str, token: str):
    url = f"https://api.github.com/repos/{org}/{repo}/branches"
    r = requests.get(
        url,
        headers={"Authorization": f"token {token}"},
    )
    data = r.json()

    if r.status_code == 200 and len(data) > 0:
        for branch in data:
            if branch["name"] in ["main", "master"]:
                return branch["name"]
    #  Default is 'main'
    return "main"

def getCodeScanningSARIF(org: str, repo: str, ref: str, token: str):
    url = f"https://api.github.com/repos/{org}/{repo}/code-scanning/analyses"
    r = requests.get(
        url,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        },
        params={"ref": ref, "tool_name": "CodeQL"},
    )
    data = r.json()

    if data.get('message'):
        logger.warning(f"Message :: {data.get('message')}")

    sarif_url = None
    if r.status_code == 200 and len(data) > 0:
        sarif_url = data[0].get("url")

    if sarif_url:
        # Request the SARIF file
        r = requests.get(
            sarif_url,
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/sarif+json",
            },
        )
        data = r.json()

        print(data)

        if r.status_code == 200 and len(data) > 0:
            return data
    else:
        logger.warning('SARIF URL not found, no SARIF file to download')
        logger.warning('Permission issues might be causing the issue')

    # print(f"Failed to get pull request from base {branch}")
    return None

if __name__ == "__main__":
    arguments = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if arguments.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    org, repo = arguments.repository.split('/')

    logger.info(f" >> {org} / {repo}")

    if not arguments.ref:
        logger.info('Ref not set, dynamically getting reference')
        ref = getGitHubRepositoryDefaultBranch(
            org,
            repo,
            token=arguments.token
        )
        logger.info(f'Discovered reference :: {ref}')

    sarif = getCodeScanningSARIF(
        org,
        repo,
        ref=arguments.ref,
        token=arguments.token
    )

    if sarif:
        logger.info(f'Writing SARIF file to disk :: {arguments.output}')
        with open(arguments.output, 'w') as handle:
            json.dump(sarif, handle, indent=2, sort_keys=True)
    else:
        logger.warning("Unable to write SARIF to disk")
