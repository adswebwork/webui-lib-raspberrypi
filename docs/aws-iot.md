# AWS IoT Core

## Standing up a new account

This fleet has no AWS account attached. The account it previously used is no
longer accessible, and its certificates went with it — nothing here connects
to anything until the steps below are done once.

### 1. The endpoint

```bash
aws iot describe-endpoint --endpoint-type iot:Data-ATS
```

Put the result in `devices.json` as `iot_endpoint`, or export
`PIHOME_IOT_ENDPOINT` on each Pi. There is no default: an endpoint identifies
one account, and guessing wrong fails as a TLS timeout on a screenless Pi,
which is indistinguishable from a network fault.

### 2. A policy

One policy is enough for this fleet. Scope it to the topics
[`schema/topics.md`](../schema/topics.md) describes rather than `iot:*` on
`*` — a certificate that can only touch `home/<device>/#` is worth far more
than one that can do anything, on the day a key leaks.

### 3. A thing and a certificate per device

For each of `sensehat-01`, `mains-01`, `fan-01`, `camera-01`:

```bash
aws iot create-thing --thing-name sensehat-01
tools/rotate-certs.sh new sensehat-01 sensehat-01 <policy-name>
```

`rotate-certs.sh new` creates the key pair, attaches the thing and policy,
writes them to `secrets/<set>/`, and checks the key matches the certificate.
Set `provisioned` to `true` in `devices.json` as each one connects — the
registry is only useful while it tells the truth.

## Credentials

One directory per credential set under `secrets/`, never committed. See
[`secrets/README.md`](../secrets/README.md).

A device uses the set named by `credentials` in `devices.json`, and its own id
when that key is absent — which is the normal case. The indirection exists
because two devices sharing one certificate has to stay expressible; the
previous fleet did exactly that, and it belongs in the registry as data rather
than hidden in a call.

Set `PIHOME_CERT_DIR` to override the location entirely.

## Rotating later

`tools/rotate-certs.sh` has two commands rather than one, and the gap between
them is the point:

1. `new` — create the replacement, attach the same thing and policy.
2. Bring the node up on it and watch it publish.
3. `revoke <certificate-id>` — deactivate, detach, delete the old one.

Deactivating a certificate a device is still using takes it offline
immediately and silently. Do step 3 before step 2 and the fleet goes dark
with nothing in the logs to explain it.

## The previous account

Its certificates were committed to the predecessor repository, which has been
deleted, along with the AWS account they authenticated against. They were
never installed on any Pi in the current fleet — every machine is a clean
Raspberry Pi OS install — so nothing here depends on them and nothing needs
migrating.

The Amazon LWA `clientId`/`clientSecret`/`productId` from the old Angular
scaffold are a separate matter: they belong to an Amazon *developer* account,
not to AWS, and if that account is still reachable they are worth revoking
there. See [`domain-model.json`](domain-model.json).
