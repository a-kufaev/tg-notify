#!/bin/sh
# tg-notify installer. Safe to re-run (tg-notify --update does: git pull + this): it repairs what is missing
# and prints what is left to do.
#   ./install.sh               CLI into ~/.local/bin, a config, and the Claude Code hook if ~/.claude exists
#   ./install.sh --no-claude   without the hook
#   ./install.sh --uninstall   remove the links and the hook entries; keeps ~/.config/tg-notify
# Everything is a symlink into this repo, so `git pull` is the whole update.
set -eu
root=$(cd "$(dirname "$0")" && pwd)
bin="$HOME/.local/bin"
conf="${TG_NOTIFY_HOME:-$HOME/.config/tg-notify}"
hook="$HOME/.claude/hooks/telegram"
settings="$HOME/.claude/settings.json"
mode=${1:-install}

# Add (or with "remove", drop) the hook in settings.json for every event it handles.
wire_hook() {
  python3 -I - "$settings" "$hook" "$1" <<'EOF'
import json, os, shutil, sys
path, command, action = sys.argv[1:]
settings = json.load(open(path)) if os.path.exists(path) else {}
hooks = settings.setdefault("hooks", {})
changed = False
for event, matcher in [("SessionStart", None), ("Stop", None), ("Notification", None), ("PreToolUse", "AskUserQuestion")]:
    groups = hooks.setdefault(event, [])
    ours = [g for g in groups if any(h.get("command") == command for h in g.get("hooks", []))]
    if action == "remove" and ours:
        hooks[event] = [g for g in groups if g not in ours]
        changed = True
    elif action == "add" and not ours:
        group = {"hooks": [{"type": "command", "command": command}]}
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
  for f in "$bin/tg-notify" "$bin/tg-notify-render" "$hook"; do
    case $(readlink "$f" 2>/dev/null) in "$root"/*) rm "$f" && echo "removed $f" ;; esac
  done
  [ -f "$settings" ] && wire_hook remove && echo "hook entries removed from $settings (backup: .bak)"
  echo "kept $conf (token, chat, config); delete it by hand if you want"
  exit 0
fi

mkdir -p "$bin" "$conf"
chmod 700 "$conf"
for f in tg-notify tg-notify-render; do ln -sfn "$root/bin/$f" "$bin/$f"; done
[ -f "$conf/config" ] || { cp "$root/config.example" "$conf/config"; chmod 600 "$conf/config"; }
if [ "$mode" != --no-claude ] && [ -d "$HOME/.claude" ]; then
  mkdir -p "$HOME/.claude/hooks"
  ln -sfn "$root/hooks/claude-telegram" "$hook"
  wire_hook add
fi

# Status: what works and what is left.
ok() { echo "  ✓ $1"; }
todo() { echo "  ✗ $1"; left=1; }
left=0
echo "tg-notify ($root)"
ok "CLI: $bin/tg-notify"
case ":$PATH:" in *":$bin:"*) ok "$bin is on PATH" ;;
  *) todo "add to your shell profile: export PATH=\"\$HOME/.local/bin:\$PATH\"" ;; esac
ok "settings: $conf/config"
if [ -L "$hook" ]; then ok "Claude Code hook: $hook"
else echo "  – Claude Code hook not installed"; fi
if [ -s "$conf/token" ] && [ -s "$conf/chat_id" ]; then ok "bot connected"
else todo "connect the bot: tg-notify --setup"; fi
[ $left = 0 ] && echo "Ready. Try: tg-notify '✅ **hello**'" || true
