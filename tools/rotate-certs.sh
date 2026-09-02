#!/bin/bash
# Rotate an AWS IoT device certificate.
#
#   tools/rotate-certs.sh new    <credential-set> <thing-name> <policy-name>
#   tools/rotate-certs.sh revoke <certificate-id>
#
# Two commands, deliberately not one. Creating a replacement is safe and
# reversible; destroying the old one is neither, and the gap between them is
# where you confirm the device actually connects. Run `new`, bring the node up
# on the new credential, watch it publish, and only then run `revoke`.
#
# Deactivating a certificate a device is still using takes that device offline
# immediately and silently - it simply stops connecting. No Pi is deployed
# right now, so nothing can break today, but the order is the same next time
# when something can.
#
# Needs the AWS CLI, configured for the account that owns the IoT endpoint in
# docs/aws-iot.md. The certificate ids to revoke are listed there.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

die() { echo "$*" >&2; exit 1; }

usage() {
    sed -n '2,/^set -euo/p' "${BASH_SOURCE[0]}" | sed 's/^# \?//;$d' >&2
    exit 64
}

command -v aws >/dev/null || die "aws CLI not found. https://aws.amazon.com/cli/"
aws sts get-caller-identity >/dev/null 2>&1 \
    || die "AWS credentials are not working. Check your profile and region."

cmd="${1:-}"
shift || true

case "$cmd" in
new)
    SET="${1:-}"; THING="${2:-}"; POLICY="${3:-}"
    if [ -z "$SET" ] || [ -z "$THING" ] || [ -z "$POLICY" ]; then
        usage
    fi

    DIR="$REPO/secrets/$SET"
    if [ -e "$DIR/private.pem.key" ]; then
        die "$DIR already holds a private key. Move it aside first - this
script will not overwrite a credential that something may still be using."
    fi
    mkdir -p "$DIR"
    chmod 700 "$DIR"

    echo "creating a certificate for thing '$THING' with policy '$POLICY'..."
    arn=$(aws iot create-keys-and-certificate \
            --set-as-active \
            --certificate-pem-outfile "$DIR/certificate.pem.crt" \
            --private-key-outfile "$DIR/private.pem.key" \
            --query certificateArn --output text)
    chmod 600 "$DIR/private.pem.key" "$DIR/certificate.pem.crt"

    aws iot attach-policy --policy-name "$POLICY" --target "$arn"
    aws iot attach-thing-principal --thing-name "$THING" --principal "$arn"

    # The id is the last path segment of the ARN, and is also the sha256 of
    # the DER certificate - the same value docs/aws-iot.md lists for the old
    # ones, so the two can be compared directly.
    new_id="${arn##*/}"

    echo
    echo "new certificate id: $new_id"
    echo "written to:         secrets/$SET/  (never committed - see .gitignore)"
    echo
    "$REPO/tools/provision-certs.sh" "$SET"
    echo
    echo "Next: bring the node up on this credential and confirm it publishes."
    echo "Only then:  tools/rotate-certs.sh revoke <old-certificate-id>"
    ;;

revoke)
    CERT_ID="${1:-}"
    [ -n "$CERT_ID" ] || usage
    case "$CERT_ID" in
        *[!0-9a-f]* | "") die "certificate id must be 64 hex characters" ;;
    esac
    [ "${#CERT_ID}" -eq 64 ] || die "certificate id must be 64 hex characters"

    arn=$(aws iot describe-certificate --certificate-id "$CERT_ID" \
            --query certificateDescription.certificateArn --output text) \
        || die "no such certificate: $CERT_ID"
    status=$(aws iot describe-certificate --certificate-id "$CERT_ID" \
            --query certificateDescription.status --output text)

    echo "certificate: $CERT_ID"
    echo "status:      $status"
    echo
    echo "This deactivates it, detaches its policies and things, and deletes it."
    echo "Any device still using it stops connecting immediately."
    printf 'Type the last 6 characters of the id to confirm: '
    read -r answer
    [ "$answer" = "${CERT_ID: -6}" ] || die "not confirmed; nothing changed"

    echo "deactivating..."
    aws iot update-certificate --certificate-id "$CERT_ID" --new-status INACTIVE

    echo "detaching policies..."
    aws iot list-attached-policies --target "$arn" \
        --query 'policies[].policyName' --output text \
    | tr '\t' '\n' | while read -r policy; do
        [ -n "$policy" ] || continue
        echo "  - $policy"
        aws iot detach-policy --policy-name "$policy" --target "$arn"
    done

    echo "detaching things..."
    aws iot list-principal-things --principal "$arn" \
        --query 'things[]' --output text \
    | tr '\t' '\n' | while read -r thing; do
        [ -n "$thing" ] || continue
        echo "  - $thing"
        aws iot detach-thing-principal --thing-name "$thing" --principal "$arn"
    done

    echo "deleting..."
    aws iot delete-certificate --certificate-id "$CERT_ID" --force-delete
    echo "revoked and deleted: $CERT_ID"
    echo "Tick it off in docs/aws-iot.md."
    ;;

*)
    usage
    ;;
esac
