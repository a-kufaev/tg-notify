# tg-notify

Send results from scripts and AI agents to your own Telegram, formatted to read on a phone.
Includes a [Claude Code](https://claude.com/claude-code) hook: every agent turn ends with a short summary,
and questions and permission prompts reach your phone with a link back to the session.

```
✅ Billing: flaky test fixed, CI restarted

• a1b2c3d in main: baseline taken after the first event
• 10/10 local runs under load

┃ Action needed: approve the merge
```

## Install

macOS or Linux with `zsh`, `python3` 3.9+ and `curl`.

```sh
git clone https://github.com/a-kufaev/tg-notify ~/Develop/tg-notify
~/Develop/tg-notify/install.sh
tg-notify --setup
```

`install.sh` links everything from the repo and ends with a checklist of what is left. `--setup` asks for a
bot token ([@BotFather](https://t.me/BotFather) → `/newbot`), has you press Start in the bot's chat, and
sends a test message.

## Update

```sh
tg-notify --update
```

It pulls the repo and re-runs the installer. Everything is linked from the repo, so an edit you make there is
live at once too.

## Use

```sh
tg-notify <<'MSG'
✅ **Backup: done, 42 GB**

- 3 volumes, 18 min
MSG

tg-notify --photos before.png after.png -- "✅ **New onboarding screens**"
tg-notify --file build.log "⚠️ **CI failed**"
```

More: the header of [bin/tg-notify](bin/tg-notify). Write a message the way [FORMAT.md](FORMAT.md) says;
the renderer adds the spacing and quotes the ask line.

## Configure

`~/.config/tg-notify/config`. Every key is described in [config.example](config.example): summaries on or
off, their language, your own format file, labels. Changes apply to the next message.

## Change it

- **Format**: edit `FORMAT.md`, or point `FORMAT_FILE` at your own copy so updates never conflict.
  Sessions pick it up when they start.
- **Rendering**: `bin/tg-notify-render`. Preview without sending: `tg-notify-render < message.md`.
- **Hook**: `hooks/claude-telegram`.
- Run the tests after a change: `python3 -m unittest discover tests`.

## Uninstall

```sh
~/Develop/tg-notify/install.sh --uninstall
```

Your token and config stay in `~/.config/tg-notify`.

MIT license.
