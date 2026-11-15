#!/bin/sh
# Link tg-notify into ~/.local/bin; with --claude also link the Claude Code hook and wire it into
# ~/.claude/settings.json (Stop, Notification, PreToolUse:AskUserQuestion). Safe to re-run.
set -eu
root=$(cd "$(dirname "$0")" && pwd)

mkdir -p "$HOME/.local/bin" "$HOME/.config/tg-notify"
chmod 700 "$HOME/.config/tg-notify"
for f in tg-notify tg-notify-render; do ln -sfn "$root/bin/$f" "$HOME/.local/bin/$f"; done
echo "linked ~/.local/bin/tg-notify → $root/bin"

[ "${1:-}" = --claude ] || exit 0
mkdir -p "$HOME/.claude/hooks"
ln -sfn "$root/hooks/claude-telegram" "$HOME/.claude/hooks/telegram"
python3 -I - "$HOME/.claude/settings.json" "$HOME/.claude/hooks/telegram" <<'EOF'
import json, os, shutil, sys
path, command = sys.argv[1], sys.argv[2]
settings = json.load(open(path)) if os.path.exists(path) else {}
hooks = settings.setdefault("hooks", {})
wanted = [("Stop", None), ("Notification", None), ("PreToolUse", "AskUserQuestion")]
added = []
for event, matcher in wanted:
    groups = hooks.setdefault(event, [])
    if any(h.get("command") == command for g in groups for h in g.get("hooks", [])):
        continue
    group = {"hooks": [{"type": "command", "command": command}]}
    if matcher:
        group = {"matcher": matcher, **group}
    groups.append(group)
    added.append(event)
if added:
    if os.path.exists(path):
        shutil.copy(path, path + ".bak")
    with open(path, "w") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
        f.write("\n")
print("hook wired: " + (", ".join(added) if added else "already in place"))
EOF
