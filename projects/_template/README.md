# _template

Scaffold for a new project. Copy the whole directory:

```bash
cp -r projects/_template projects/my-project
```

## Layout

```
my-project/
├── README.md          what it does, which Pi runs which node
├── config.json        every tunable: pins, thresholds, intervals, messages
├── requirements.txt   assembled from the `requires:` lines of forked recipes
├── nodes/             one entry point per physical Pi, named for its role
├── lib/               recipes you copied and edited
└── service/           systemd units
```

## Checklist

- [ ] Recipes copied into `lib/` and renamed for what they do here
- [ ] One node per physical Pi in `nodes/`
- [ ] Every tunable moved into `config.json`
- [ ] Device ids added to `devices.json` at the repo root
- [ ] Credentials provisioned — see `secrets/README.md`
- [ ] A service unit per node, so it survives a power cut
- [ ] README says which Pi runs what

See [`dog-camera-monitor`](../dog-camera-monitor/) for a filled-in example.
