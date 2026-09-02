#!/bin/bash
# Fetch the Amazon root CA and smoke-test a device's AWS IoT credentials.
#
# This replaces five byte-identical copies of the script the AWS console drops
# into connect_device_package.zip. It does NOT create things, policies or
# certificates - do that in the AWS IoT console, then place the files as
# described in secrets/README.md and run this to check they work.
#
#   tools/provision-certs.sh sys1
set -euo pipefail

DEVICE="${1:-}"
if [ -z "$DEVICE" ]; then
    echo "usage: $0 <credential-set>   e.g. $0 sys1" >&2
    exit 64
fi

REPO="$(cd "$(dirname "$0")/.." && pwd)"
DIR="$REPO/secrets/$DEVICE"
CA="$REPO/secrets/AmazonRootCA1.cer"

[ -d "$DIR" ] || { echo "no such credential set: $DIR" >&2; exit 1; }

if [ ! -f "$CA" ]; then
    echo "fetching Amazon root CA..."
    curl -fsSL https://www.amazontrust.com/repository/AmazonRootCA1.pem -o "$CA"
fi

for f in private.pem.key certificate.pem.crt; do
    [ -f "$DIR/$f" ] || { echo "missing $DIR/$f" >&2; exit 1; }
done

echo "checking certificate..."
openssl x509 -in "$DIR/certificate.pem.crt" -noout -subject -dates

echo "checking the key matches the certificate..."
# Compare the two public keys as PEM text. Not `openssl rsa -modulus`, which
# dies with "Not an RSA key" on an EC key - AWS IoT will issue an EC
# certificate if you ask for one, and under `set -o pipefail` that aborted this
# script on a perfectly good credential set. `openssl pkey` handles RSA, EC and
# Ed25519 alike, and both commands emit the same SPKI PEM for the same key.
#
# Deliberately not piped into a digest: hashing an empty input still produces a
# valid hash, so a key that could not be read at all would compare unequal and
# be reported as a mismatch - sending you to look for a swapped file when the
# real problem is an encrypted or truncated one.
#
# -passin so an encrypted key fails with a message rather than blocking on a
# passphrase prompt nothing is there to answer. `|| true` because this script
# runs under `set -e`, which would otherwise abort before the checks below.
key_pub=$(openssl pkey  -in "$DIR/private.pem.key"     -pubout -passin pass: 2>/dev/null) || true
crt_pub=$(openssl x509 -in "$DIR/certificate.pem.crt" -noout -pubkey    2>/dev/null) || true

if [ -z "$key_pub" ]; then
    echo "could not read a public key from $DIR/private.pem.key" >&2
    echo "Is it a private key, and is it unencrypted? The AWS IoT console only" >&2
    echo "offers the private key once - re-create the certificate if it is lost." >&2
    exit 1
fi
if [ -z "$crt_pub" ]; then
    echo "could not read a public key from $DIR/certificate.pem.crt" >&2
    echo "Is it a PEM certificate? Check it is not the public key file." >&2
    exit 1
fi

if [ "$key_pub" = "$crt_pub" ]; then
    algorithm=$(openssl x509 -in "$DIR/certificate.pem.crt" -noout -text \
        | sed -n 's/.*Public Key Algorithm: //p' | head -1)
    echo "OK: key and certificate match ($algorithm)"
else
    echo "MISMATCH: this key does not belong to this certificate" >&2
    exit 1
fi
