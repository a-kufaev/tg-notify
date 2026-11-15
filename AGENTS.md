# tg-notify: notes for agents editing this repo

- **One home per fact.** The message format lives only in `FORMAT.md`; the hook hands it to agents, nothing
  copies it. A setting lives in three places that move together: the default in code, `config.example`, the
  README «Settings» table.
- **Nothing personal in the repo**: tokens, chat ids, project names, someone's language. Those go to the
  user's `~/.config/tg-notify/config`.
- **Config parsing**: zsh `source`s the file (`bin/tg-notify`), Python reads it via `lib/tg_notify_config.py`.
  Keep it `KEY="value"` on one line. Avoid names the shell or locale use (`LANG`, `LANGUAGE`, `PATH`).
- **Paths resolve through symlinks** (`${0:A:h:h}`, `os.path.realpath`): the scripts run from `~/.local/bin`
  and `~/.claude/hooks`, the repo is their root.
- **zsh trap**: quote `"${1:-$(cat)}"`; unquoted, the stdin lines are joined with spaces.
- **Tests**: `python3 -m unittest discover tests`. They run with an empty `TG_NOTIFY_HOME`; never let a test
  send a real message (the hook's Notification and AskUserQuestion branches do).
- A behaviour change updates the README section it touches (Settings, Updating, Troubleshooting).
