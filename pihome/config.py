"""Per-project JSON config, deep-merged over defaults.

JSON rather than TOML deliberately: the fleet still runs Python 3.7 and 3.9,
and tomllib only arrived in 3.11.
"""
import json
import os


def _deep_merge(base, override):
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load(path, defaults=None):
    """Load a JSON config, merged over `defaults`.

    Pass an absolute path. A relative one is resolved against the current
    working directory, which under systemd is whatever WorkingDirectory says
    and not where the node script lives - so every node builds its path from
    __file__ instead. This function cannot do that for you: it would have to
    inspect the call stack to find out who its caller is.
    """
    if not os.path.isabs(path):
        path = os.path.abspath(path)
    with open(path) as handle:
        data = json.load(handle)
    # Keys beginning with _ are commentary, not configuration.
    data = {k: v for k, v in data.items() if not k.startswith("_")}
    return _deep_merge(defaults or {}, data)
