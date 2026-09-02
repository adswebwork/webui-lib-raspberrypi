# Device credentials

**Nothing in here except this file and the Amazon root CA is committed.**
`.gitignore` blocks `secrets/*/`.

## Layout

```
secrets/
  AmazonRootCA1.cer        public, tracked
  sys1/
    private.pem.key        per-device, never committed
    certificate.pem.crt    per-device, never committed
```

One directory per *credential set*, not per device — `devices.json` maps a
device to the set it uses. `fan-01` deliberately uses `sys2`.

## Provisioning a device

1. AWS IoT console → Manage → Things → create a thing, attach a policy, and
   download the certificate and private key.
2. `mkdir -p secrets/<name>` and place the two files with the names above.
3. `tools/provision-certs.sh <name>` to verify the key matches the
   certificate. It reads RSA and EC keys alike, and tells an unreadable
   key (encrypted, truncated) apart from a genuinely mismatched one.
   `tests/test_provision_certs.sh` checks that it still does.
4. Tell the Pi who it is: `echo <device-id> | sudo tee /etc/pihome/device`.

`pihome.credentials` also falls back to the old `_globalConfig/_sysN/` layout,
so a Pi that has not been migrated keeps authenticating.

## Outstanding

- **Rotate every existing certificate.** They were committed to the previous
  repository (`adswebwork/raspberrypi`, private) and remain in its history.
  Nothing secret is in this repository's history - but moving does not revoke
  anything. Until rotation, that old repository is where the working
  certificates come from; see [`../docs/aws-iot.md`](../docs/aws-iot.md).
- **`camera-01` has never been provisioned** — it has no credential set at all.
