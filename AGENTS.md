# tg-notify: notes for agents editing this repo

- **One home per fact.** The message format lives only in `FORMAT.md`; the hook puts it into the agent's
  context at SessionStart, nothing copies it. A setting is its default in code plus its entry in
  `config.example`; the README only points there.
- **The Stop reminder is a fallback**: the UI shows it, so it fires only when a turn made tool calls and ran no
  tg-notify (read from the transcript), and stays one short line.
- **English only, nothing personal in the repo**: tokens, chat ids, project names, someone's language. Those go to the
  user's `~/.config/tg-notify/config`.
- **Config parsing**: zsh `source`s the file (`bin/tg-notify`), Python reads it via `lib/tg_notify_config.py`.
  Keep it `KEY="value"` on one line. Avoid names the shell or locale use (`LANG`, `LANGUAGE`, `PATH`).
- **Paths resolve through symlinks** (`${0:A:h:h}`, `os.path.realpath`): the scripts run from `~/.local/bin`
  and `~/.claude/hooks`, the repo is their root.
- **zsh trap**: quote `"${1:-$(cat)}"`; unquoted, the stdin lines are joined with spaces.
- **Tests**: `python3 -m unittest discover tests`. They run with an empty `TG_NOTIFY_HOME`; never let a test
  send a real message (the hook's Notification and AskUserQuestion branches do).
- The README stays minimal: install, update, use, configure, change, uninstall. Details go to file headers.
