#!/bin/bash
# Does tools/provision-certs.sh tell the truth about a credential set?
#
#   tests/test_provision_certs.sh
#
# Shell rather than pytest because the thing under test is a shell script and
# the fixtures are real key pairs from openssl. Skips itself where openssl is
# absent. Run by hand; CI does not have openssl guaranteed and this is a
# provisioning tool, not something a node imports.
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT="$REPO/tools/provision-certs.sh"

command -v openssl >/dev/null || { echo "SKIP: no openssl"; exit 0; }

WORK="$(mktemp -d)"
CREATED=()
# shellcheck disable=SC2317  # invoked by the EXIT trap, not called directly
cleanup() {
    for d in ${CREATED+"${CREATED[@]}"}; do rm -rf "$REPO/secrets/$d"; done
    rm -rf "$WORK"
}
trap cleanup EXIT

fails=0

# Runs the script against a credential set and checks the summary line.
# expect_match <name> <pattern> <description>
expect_match() {
    local name="$1" pattern="$2" description="$3" output
    CREATED+=("$name")
    output=$(timeout 20 bash "$SCRIPT" "$name" </dev/null 2>&1 || true)
    if grep -qE "$pattern" <<<"$output"; then
        printf 'ok    %s\n' "$description"
    else
        # shellcheck disable=SC2001  # per-line prefix; ${v//x/y} cannot do ^
        printf 'FAIL  %s\n      wanted /%s/, got:\n%s\n' \
            "$description" "$pattern" "$(sed 's/^/      /' <<<"$output")"
        fails=$((fails + 1))
    fi
}

new_set() {
    local name="$1"
    mkdir -p "$REPO/secrets/$name"
    echo "$REPO/secrets/$name"
}

# --- an RSA pair, which is what the AWS IoT console issues by default -------
dir=$(new_set rsa-selftest)
openssl req -x509 -newkey rsa:2048 -nodes -days 2 -subj "/CN=rsa" \
    -keyout "$dir/private.pem.key" -out "$dir/certificate.pem.crt" 2>/dev/null
expect_match rsa-selftest '^OK: key and certificate match' "RSA pair is accepted"

# --- an EC pair, which openssl rsa -modulus could not read at all -----------
dir=$(new_set ec-selftest)
openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes \
    -days 2 -subj "/CN=ec" \
    -keyout "$dir/private.pem.key" -out "$dir/certificate.pem.crt" 2>/dev/null
expect_match ec-selftest '^OK: key and certificate match' "EC pair is accepted"

# --- a key from a different certificate: the real mismatch ------------------
dir=$(new_set swapped-selftest)
openssl req -x509 -newkey rsa:2048 -nodes -days 2 -subj "/CN=other" \
    -keyout "$dir/private.pem.key" -out /dev/null 2>/dev/null
openssl req -x509 -newkey rsa:2048 -nodes -days 2 -subj "/CN=mine" \
    -keyout /dev/null -out "$dir/certificate.pem.crt" 2>/dev/null
expect_match swapped-selftest '^MISMATCH' "a swapped key is reported as a mismatch"

# --- an encrypted key: must be diagnosed, not called a mismatch ------------
dir=$(new_set encrypted-selftest)
openssl req -x509 -newkey rsa:2048 -passout pass:secret -days 2 -subj "/CN=enc" \
    -keyout "$dir/private.pem.key" -out "$dir/certificate.pem.crt" 2>/dev/null
expect_match encrypted-selftest '^could not read a public key' \
    "an encrypted key is diagnosed, not called a mismatch"

# --- a truncated key: likewise ---------------------------------------------
dir=$(new_set truncated-selftest)
echo "-----BEGIN PRIVATE KEY-----" > "$dir/private.pem.key"
openssl req -x509 -newkey rsa:2048 -nodes -days 2 -subj "/CN=trunc" \
    -keyout /dev/null -out "$dir/certificate.pem.crt" 2>/dev/null
expect_match truncated-selftest '^could not read a public key' \
    "a truncated key is diagnosed, not called a mismatch"

echo
if [ "$fails" -eq 0 ]; then
    echo "all provision-certs checks passed"
else
    echo "$fails check(s) failed" >&2
fi
exit "$fails"
