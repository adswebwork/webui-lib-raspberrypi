# Branch rulesets

## GitHub does not read these files

Rulesets are repository *settings*, configured through the API or the web UI.
Nothing here is applied automatically. Editing `protect-main.json` changes
nothing about what the repository enforces until someone runs the command
below — treat it as a record of intent and a way to reproduce the setting, not
as the setting itself.

This matters because the alternative failure is silent: a file that looks like
configuration, reads like configuration, and protects nothing.

## Applying it

```bash
gh api -X PUT repos/adswebwork/webui-lib-raspberrypi/rulesets/22132657 \
  --input .github/rulesets/protect-main.json
```

`22132657` is the id of the existing `protect main` ruleset. To create a fresh
one instead — in a new repository, say — POST to `.../rulesets` without an id
and record the id it returns here.

To check what is actually live, which is the only thing that counts:

```bash
gh api repos/adswebwork/webui-lib-raspberrypi/rulesets/22132657 | jq '.rules'
```

## What it asks for, and why

| Rule | Reason |
|---|---|
| `deletion` | `main` should not be deletable |
| `non_fast_forward` | no force-pushing shared history |
| `pull_request`, 0 approvals | a PR is what gives the status checks something to gate. Zero approvals because there is one contributor and GitHub does not let anyone approve their own PR — at 1 you cannot merge your own work, Dependabot's included |
| `required_status_checks` | `test (3.9)`, `test (3.13)`, `shell`, `secrets`. These are the job names in `../workflows/ci.yml`; renaming a job there silently stops it gating, because a required check that never reports is simply absent |
| `strict_required_status_checks_policy` | a branch must be current with `main` before merging. A Dependabot PR once merged on CI that had run against a base two commits old, and it was caught by hand |

## Verify enforcement, do not assume it

Four direct pushes to `main` succeeded while a ruleset requiring pull requests
was already active, so something bypasses it — plausibly the repository owner
on a user-owned repository. Confirm before relying on any of this:

```bash
git commit --allow-empty -m "ruleset check" && git push origin main
```

A rejection means enforcement is real. Success means it is not, and the
bypass should be made deliberate (add a bypass actor) rather than left as a
surprise. Clean up with `git reset --hard origin/main~1` if it went through.
