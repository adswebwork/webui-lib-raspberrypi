"""Relative links in the markdown must point at files that exist.

This repo navigates by its documentation - recipes/README.md is an index of 32
scripts, and the project READMEs cross-reference each other and the schema. A
file move breaks those links silently, and the reader who finds out is the one
looking for the thing that moved.

Only relative links are checked. External URLs need the network, which makes
the check flaky and slow, and their rot is a much smaller problem than a
recipe index that points at nothing - see .github/workflows/links.yml, which
checks those weekly without blocking a merge.
"""
import os
import re

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# [text](target) - the target group stops at the first ) or whitespace
_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)")

_SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", ".ruff_cache"}


def _markdown_files():
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in _SKIP_DIRS]
        for name in sorted(files):
            if name.endswith(".md"):
                yield os.path.join(root, name)


def _relative_links():
    """(markdown file, line number, target) for every relative link."""
    for path in _markdown_files():
        with open(path, encoding="utf-8", errors="replace") as handle:
            for number, line in enumerate(handle, 1):
                for match in _LINK.finditer(line):
                    target = match.group(1)
                    if target.startswith(("http://", "https://", "mailto:", "#")):
                        continue
                    yield path, number, target


LINKS = sorted(set(_relative_links()))


def _describe(link):
    path, number, target = link
    return "{}:{} -> {}".format(os.path.relpath(path, REPO), number, target)


def test_there_are_links_to_check():
    """Guard against the regex silently matching nothing after a rewrite."""
    assert len(LINKS) >= 20


@pytest.mark.parametrize("link", LINKS, ids=_describe)
def test_relative_link_resolves(link):
    path, _, target = link
    # Strip any #anchor; we check the file exists, not the heading.
    target = target.split("#")[0]
    if not target:
        return
    resolved = os.path.normpath(os.path.join(os.path.dirname(path), target))
    assert os.path.exists(resolved), "{} does not exist".format(
        os.path.relpath(resolved, REPO))
