#!/usr/bin/env python3

import sys
import argparse
import logging
from git import Repo
from git import InvalidGitRepositoryError

logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("linhist")

parser = argparse.ArgumentParser(
    prog="linhist",
    description="A tool to check and maintain a linear Git history",
    epilog="For more help on Linhist check https://github.com/wiltonloch/linhist",
)
subparsers = parser.add_subparsers()

check_merge_parser = subparsers.add_parser(
    "check-merge", help="Checks if a merge operation would result in linear history"
)
check_merge_parser.add_argument(
    "--repository",
    type=str,
    help="Path to the repository where to perform the check",
    default=".",
    required=False,
)
check_merge_parser.add_argument(
    "--source", type=str, help="Source branch for the merge check", required=True
)
check_merge_parser.add_argument(
    "--target", type=str, help="Target branch for the merge check", required=True
)

args = parser.parse_args()

repository_path = args.repository
source = args.source
target = args.target

try:
    repository = Repo(repository_path)
except InvalidGitRepositoryError:
    logger.error('The argument passed to "--repository" is not a valid Git repository')
    sys.exit(1)

if source not in repository.branches:
    logger.error(
        'The argument passed to "--source" is not an existing branch in the Git repository'
    )
    sys.exit(1)

if target not in repository.branches:
    logger.error(
        'The argument passed to "--target" is not an existing branch in the Git repository'
    )
    sys.exit(1)

common_ancestor = repository.merge_base(source, target)[0]
target_tip = repository.rev_parse(target)

if target_tip == common_ancestor:
    logger.info("CHECK PASSED: Merging will result in linear Git history")
    sys.exit(0)
else:
    logger.info("CHECK FAILED: Merging will result in non-linear Git history.")
    logger.info(
        "If both branches have some common ancestor, try rebasing the source on the target."
    )
    logger.info(
        "Remember that child branches should be rebased on their parents, not the opposite."
    )
    sys.exit(1)
