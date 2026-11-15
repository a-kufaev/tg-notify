"""Reads ~/.config/tg-notify/config for the Python parts (the renderer, the hook); tg-notify itself sources it.
The file is KEY="value" lines, valid zsh too; comments go on their own lines. All keys: config.example."""
import os

HOME = os.path.expanduser(os.environ.get("TG_NOTIFY_HOME", "~/.config/tg-notify"))


def load(defaults: dict[str, str]) -> dict[str, str]:
    """`defaults` with the values the config sets for the same keys; unknown keys are ignored."""
    values = dict(defaults)
    try:
        with open(os.path.join(HOME, "config"), encoding="utf-8") as config:
            lines = config.read().splitlines()
    except OSError:
        return values
    for line in lines:
        key, sep, value = line.strip().partition("=")
        if sep and key in values and not key.startswith("#"):
            values[key] = value.strip().strip("\"'")
    return values
