# Device credentials

**Nothing in here except this file and the Amazon root CA is committed.**
`.gitignore` blocks `secrets/*/`.

## Layout

```
secrets/
  AmazonRootCA1.cer        public, tracked
  sensehat-01/
    private.pem.key        per-device, never committed
    certificate.pem.crt    per-device, never committed
```

One directory per *credential set*. Normally that is the device's own id;
`devices.json` can point a device at a different set when two devices share a
certificate.

## Provisioning a device

1. AWS IoT console → Manage → Things → create a thing, attach a policy, and
   download the certificate and private key.
2. `mkdir -p secrets/<name>` and place the two files with the names above.
3. `tools/provision-certs.sh <name>` to verify the key matches the
   certificate. It reads RSA and EC keys alike, and tells an unreadable
   key (encrypted, truncated) apart from a genuinely mismatched one.
   `tests/test_provision_certs.sh` checks that it still does.
4. Tell the Pi who it is: `echo <device-id> | sudo tee /etc/pihome/device`.

Set `PIHOME_CERT_DIR` to override the location entirely - useful if the
credentials live outside the checkout.

## Outstanding

- **No device is provisioned.** The fleet is being stood up on a new AWS
  account — see [`../docs/aws-iot.md`](../docs/aws-iot.md). Set `provisioned`
  to `true` in `devices.json` as each node connects.
