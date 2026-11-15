#!/bin/sh
# tg-notify installer. Safe to re-run (tg-notify --update does: git pull + this): it repairs what is missing
# and prints what is left to do.
#   ./install.sh               CLI into ~/.local/bin, a config, and the Claude Code hook
#   ./install.sh --no-claude   without the hook
#   ./install.sh --uninstall   remove the links and the hook entries; keeps ~/.config/tg-notify
# The hook goes into every Claude Code config folder it finds: ~/.claude, $CLAUDE_CONFIG_DIR (set by apps
# that run Claude Code with their own profile), and CLAUDE_DIRS from the config.
set -eu
root=$(cd "$(dirname "$0")" && pwd)
bin="$HOME/.local/bin"
conf="${TG_NOTIFY_HOME:-$HOME/.config/tg-notify}"
hook="$root/hooks/claude-telegram"
mode=${1:-install}

# Claude Code config folders, one per line, existing ones only, each once.
claude_dirs() {
  extra=$(TG_NOTIFY_HOME="$conf" python3 -I -c '
import sys; sys.path.insert(0, sys.argv[1])
from tg_notify_config import load; print(load({"CLAUDE_DIRS": ""})["CLAUDE_DIRS"])' "$root/lib")
  python3 -I - "$HOME/.claude" "${CLAUDE_CONFIG_DIR:-}" "$extra" <<'EOF'
import os, sys
seen = []
for entry in sys.argv[1:3] + sys.argv[3].split(":"):
    path = os.path.expanduser(entry.strip())
    if path and os.path.isdir(path) and os.path.realpath(path) not in map(os.path.realpath, seen):
        seen.append(path)
print("\n".join(seen))
EOF
}

# settings.json of one folder: add | remove | check the hook for every event it handles.
# Ours is any command that resolves to this repo's hook, so older symlinked entries count too.
hook_settings() {
  python3 -I - "$1/settings.json" "$hook" "$2" <<'EOF'
import json, os, shutil, sys
path, hook, action = sys.argv[1:]
events = [("SessionStart", None), ("Stop", None), ("Notification", None), ("PreToolUse", "AskUserQuestion")]
settings = json.load(open(path)) if os.path.exists(path) else {}
hooks = settings.setdefault("hooks", {})

def ours(group):
    return any(os.path.realpath(h.get("command", "")) == os.path.realpath(hook) for h in group.get("hooks", []))

if action == "check":
    missing = [e for e, _ in events if not any(ours(g) for g in hooks.get(e, []))]
    print(", ".join(missing))
    sys.exit()
changed = False
for event, matcher in events:
    groups = hooks.setdefault(event, [])
    if action == "remove" and any(ours(g) for g in groups):
        hooks[event] = [g for g in groups if not ours(g)]
        changed = True
    elif action == "add" and not any(ours(g) for g in groups):
        group = {"hooks": [{"type": "command", "command": hook}]}
        groups.append({"matcher": matcher, **group} if matcher else group)
        changed = True
    if not hooks[event]:
        del hooks[event]
if changed:
    if os.path.exists(path):
        shutil.copy(path, path + ".bak")
    with open(path, "w") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
        f.write("\n")
EOF
}

if [ "$mode" = --uninstall ]; then
  # settings first: an older entry points at the ~/.claude/hooks/telegram link and is recognised through it
  claude_dirs | while IFS= read -r dir; do
    [ -f "$dir/settings.json" ] && hook_settings "$dir" remove && echo "hook removed from $dir/settings.json"
  done
  for f in "$bin/tg-notify" "$bin/tg-notify-render" "$HOME/.claude/hooks/telegram"; do
    case $(readlink "$f" 2>/dev/null) in "$root"/*) rm "$f" && echo "removed $f" ;; esac
  done
  echo "kept $conf (token, chat, config); delete it by hand if you want"
  exit 0
fi

mkdir -p "$bin" "$conf"
chmod 700 "$conf"
for f in tg-notify tg-notify-render; do ln -sfn "$root/bin/$f" "$bin/$f"; done
[ -f "$conf/config" ] || { cp "$root/config.example" "$conf/config"; chmod 600 "$conf/config"; }
if [ "$mode" != --no-claude ]; then
  claude_dirs | while IFS= read -r dir; do hook_settings "$dir" add; done
fi

# Status: what works and what is left.
ok() { echo "  ✓ $1"; }
todo() { echo "  ✗ $1"; }
echo "tg-notify ($root)"
ok "CLI: $bin/tg-notify"
case ":$PATH:" in *":$bin:"*) ok "$bin is on PATH" ;;
  *) todo "add to your shell profile: export PATH=\"\$HOME/.local/bin:\$PATH\"" ;; esac
ok "settings: $conf/config"
dirs=$(claude_dirs)
[ "$mode" = --no-claude ] && dirs=
[ -n "$dirs" ] || echo "  – Claude Code hook not installed"
echo "$dirs" | while IFS= read -r dir; do
  [ -n "$dir" ] || continue
  missing=$(hook_settings "$dir" check)
  if [ -z "$missing" ]; then ok "Claude Code hook: $dir"
  else todo "Claude Code hook in $dir lacks $missing: run install.sh"; fi
done
if [ -s "$conf/token" ] && [ -s "$conf/chat_id" ]; then ok "bot connected"
else todo "connect the bot: tg-notify --setup"; fi
