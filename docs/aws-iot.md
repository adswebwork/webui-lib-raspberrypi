# AWS IoT Core

## Endpoint

`a2r4022mytw4qr-ats.iot.us-east-1.amazonaws.com:8883`, overridable with
`PIHOME_IOT_ENDPOINT` / `PIHOME_IOT_PORT`.

## Credentials

One directory per credential set under `secrets/`, never committed. See
[`secrets/README.md`](../secrets/README.md).

`devices.json` maps a device to the set it authenticates with — not always its
own name. `fan-01` uses `sys2`.

`pihome.credentials.certs_for()` also falls back to the old
`_globalConfig/_sysN/` layout, so a Pi that has not been migrated keeps
working.

## Outstanding security work

**Rotate every device certificate.** Nothing secret has ever been committed to
*this* repository - it starts from a single clean import. The certificates were
committed to its predecessor, the private `adswebwork/raspberrypi`, and remain
in that repository's history across 312 commits. Moving here removed them from
the code you work in; it did not revoke anything, and the certificates do not
expire until 2049.

The old repository is deliberately kept for now, because it is where the
current working certificates live and they are needed to bring a Pi up before
rotation. Once every device below is rotated, archive or delete it - a copy
that outlives its purpose is just an exposure with no upside.

For each of `sys0`, `sys1`, `sys2`, `pi3`:

1. AWS IoT console → Security → Certificates
2. Deactivate, then revoke and delete
3. Create a replacement, attach the same policy and thing
4. Download it into `secrets/<name>/`
5. `tools/provision-certs.sh <name>` to check the key matches
6. `scp` to the Pi and restart the service

**Revoke the Amazon LWA credentials.** A `clientSecret` (64 hex characters),
`clientId` and `productId` were committed in the Angular scaffold's
`config.json` in the old repository. Nothing of them is here - `gitleaks`
confirms this tree is clean, and CI keeps it that way - but they remain in that
repository's history. Revoke them in the Amazon developer console.

## Provisioning camera-01

This node has never connected — there is no credential set for it. Create a
thing, attach a policy, and place the certificate in `secrets/sys4/`.
