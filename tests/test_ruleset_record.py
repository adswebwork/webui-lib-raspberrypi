"""The committed ruleset must name the checks CI actually produces.

.github/rulesets/protect-main.json records which status checks have to pass
before main can be merged into. GitHub does not read that file - it is applied
by hand - so nothing keeps it honest except this.

The failure it guards against is silent in the worst way: a required check
that never reports is not a blocked merge, it is no gate at all. Rename a job
in ci.yml without updating the ruleset and merges stop being gated, with
nothing red anywhere to say so.
"""
import json
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

yaml = pytest.importorskip("yaml", reason="pip install PyYAML")

RULESET = os.path.join(REPO, ".github", "rulesets", "protect-main.json")
WORKFLOW = os.path.join(REPO, ".github", "workflows", "ci.yml")


def _ruleset():
    with open(RULESET) as handle:
        return json.load(handle)


def _required_contexts():
    for rule in _ruleset()["rules"]:
        if rule["type"] == "required_status_checks":
            return {c["context"] for c in
                    rule["parameters"]["required_status_checks"]}
    return set()


def _ci_check_names():
    """Job names as they appear as checks, expanding any matrix."""
    with open(WORKFLOW) as handle:
        workflow = yaml.safe_load(handle)

    names = set()
    for job_id, job in workflow["jobs"].items():
        matrix = (job.get("strategy") or {}).get("matrix") or {}
        # Only single-dimension matrices are expanded; this workflow has one.
        axes = {k: v for k, v in matrix.items() if isinstance(v, list)}
        if len(axes) == 1:
            (values,) = axes.values()
            for value in values:
                names.add("{} ({})".format(job_id, value))
        elif axes:
            raise AssertionError(
                "multi-axis matrix in job {!r}; teach this test how the check "
                "names are built before relying on it".format(job_id))
        else:
            names.add(job_id)
    return names


def test_ruleset_file_parses():
    _ruleset()


def test_every_required_check_is_a_job_ci_actually_runs():
    """A required check that never reports blocks nothing."""
    missing = _required_contexts() - _ci_check_names()
    assert not missing, (
        "ruleset requires checks CI does not produce: {}. "
        "These would never report, so they gate nothing.".format(sorted(missing)))


def test_every_ci_job_is_required():
    """A job that runs but is not required is a check nobody has to pass."""
    unguarded = _ci_check_names() - _required_contexts()
    assert not unguarded, (
        "CI runs {} but the ruleset does not require them - failing them would "
        "not block a merge.".format(sorted(unguarded)))


def test_a_pull_request_is_required_at_all():
    """Status checks gate pull requests; without one there is nothing to gate."""
    types = {r["type"] for r in _ruleset()["rules"]}
    assert "pull_request" in types
    assert "required_status_checks" in types
