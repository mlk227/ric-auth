#!/usr/bin/env python
"""
This script is used to run tests, create a coverage report and output the
statistics at the end of the tox run.
To run this script just execute ``tox``
"""

import argparse
import os
import re
import subprocess

from fabric.api import local, warn
from fabric.colors import green, red


def find_changed_files():
    current_branch = subprocess.check_output(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()

    new_files = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard"]).decode().split("\n")

    last_good_commit_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), ".git/last_good_commit")
    if os.path.exists(last_good_commit_file):
        # on sercer
        with open(last_good_commit_file, "r") as f:
            last_good_commit = f.read().strip()
        modified_files = subprocess.check_output(
            ["git", "diff", "--name-only", last_good_commit]).decode().split("\n")
    elif current_branch in ("dev", "master"):
        # if on dev/master, find uncommitted changes
        modified_files = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD"]).decode().split("\n")
    else:
        # else find different files against dev
        modified_files = subprocess.check_output(
            ["git", "diff", "--name-only", "dev"]).decode().split("\n")

    return filter(lambda x: x.endswith('.py') and os.path.exists(x) and "/migrations/" not in x and
                  "/settings/" not in x, new_files + modified_files)


def file_formatting(changed_files, readonly):
    file_names = ' '.join(changed_files)
    if not file_names:
        return

    if not readonly:
        local('isort {}'.format(file_names))
        local('autopep8 --in-place {}'.format(file_names))

    local('flake8 {}'.format(file_names))


def run_tests():
    local("coverage run -a manage.py test -v 2 --keepdb --traceback "
          "--failfast --settings=ric_auth.settings.test")

    local('coverage html')
    total_line = local('grep -n pc_cov coverage/index.html', capture=True)
    percentage = float(re.findall(r'(\d+)%', total_line)[-1])
    if percentage < 100:
        warn(red('Coverage is {0}%'.format(percentage)))
    print(green('Coverage is {0}%'.format(percentage)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run code formatting and tests.')
    parser.add_argument('--read-only', dest='readonly', action='store_true',
                        default=False,
                        help="don't call isort and autopep8 to modify files")
    args = parser.parse_args()

    changed_files = find_changed_files()
    file_formatting(changed_files, args.readonly)
    run_tests()
