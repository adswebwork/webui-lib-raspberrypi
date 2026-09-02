# AWS IoT Core

## Endpoint

`a2r4022mytw4qr-ats.iot.us-east-1.amazonaws.com:8883`, overridable with
`PIHOME_IOT_ENDPOINT` / `PIHOME_IOT_PORT`.

## Credentials

One directory per credential set under `secrets/`, never committed. See
[`secrets/README.md`](../secrets/README.md).

`devices.json` maps a device to the set it authenticates with — not always its
own name. `fan-01` uses `sys2`.

`pihome.credentials.certs_for()` looks in `secrets/<set>/`, or in
`PIHOME_CERT_DIR` if that is set. It accepts either a device id or a raw
credential-set name.

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

There are **seven** distinct certificates in that history, not the four this
document previously listed. Each id below is the SHA-256 of the DER
certificate, which is exactly the id AWS IoT shows in the console, so they can
be looked up directly rather than matched by eye.

| Certificate id | Committed as |
|---|---|
| `7d2673a1be3ab62dc9319830d9b213dc7a4705b559856692d053d3759ba22ec2` | `_globalConfig/_sys0/certificate.pem.crt` |
| `6484d40bc14b888ccc4b624b70f40e2558e645c1bf25536c6e2e0a98d8de25a6` | `_globalConfig/_sys1/certificate.pem.crt` |
| `b921f7a8266449f2aa46200dbcf5e9dfe1de858655be41a4d903d266a8392c0a` | `_globalConfig/_sys2/certificate.pem.crt` |
| `6af3da77cc4a21da13f599234c60bc377646e7bae9fedd381ee61bc0258d346a` | `_assets/aws/system1.cert.pem` |
| `76b628c27388d3778e46a48af8451b7463fad2bf891d4f3fab654f5fc06679af` | `_assets/aws/sys2/system2.cert.pem` |
| `459aa33485a449301652faf053aad9d6c139495c51edd110a109909ee4dd1a6d` | `pi3/certs/connect_device_package/pi3.cert.pem` |
| `b8820749824c38e7a853b58c1162b410110774f9b3adeb06d1b92ce96e5700da` | `pi3/certs/da-certificate.pem.crt` |

All seven are valid until 31 December 2049. These ids are public information -
a certificate is not a secret, only its private key is - and listing them here
is what makes the revocation checkable rather than approximate.

`tools/rotate-certs.sh` walks the whole rotation. In outline, and the order
matters:

1. Create the replacement first and attach the same thing and policy.
2. Place it in `secrets/<set>/` and check it with
   `tools/provision-certs.sh <set>`.
3. Confirm the device actually connects on the new certificate.
4. Only then deactivate the old one, and only after that delete it.

Deactivating before step 3 is how a fleet goes dark. Since no Pi is currently
deployed, steps 1-3 have nothing to break - but the order is written down for
the next time, when they will.

**Revoke the Amazon LWA credentials.** A `clientSecret` (64 hex characters),
`clientId` and `productId` were committed in the Angular scaffold's
`config.json` in the old repository. Nothing of them is here - `gitleaks`
confirms this tree is clean, and CI keeps it that way - but they remain in that
repository's history. Revoke them in the Amazon developer console.

## Provisioning camera-01

This node has never connected — there is no credential set for it. Create a
thing, attach a policy, and place the certificate in `secrets/sys4/`.
