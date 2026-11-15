# tg-notify

Send results to your own Telegram from scripts and AI coding agents, formatted for a phone screen.
A small zsh CLI over the Telegram Bot API, a Markdown renderer that enforces a readable layout, and an
optional [Claude Code](https://claude.com/claude-code) hook that ends every agent turn with a short summary
in Telegram, linked back to the session.

```
✅ Billing: flaky test fixed, CI restarted

• a1b2c3d in main: baseline taken after the first event
• 10/10 local runs under load

┃ Action needed: approve the merge
```

## Why a renderer

Agents write dense Markdown, and Telegram's MarkdownV2 needs escaping that generated text keeps breaking.
`tg-notify-render` turns light Markdown into Telegram HTML and fixes the layout on the way: the title is bold
and set apart, blocks are split by blank lines, the ask is quoted, long details collapse. If Telegram still
rejects the HTML, the same layout goes out as plain text, never as raw `**`.

## Install

Requires macOS or Linux with `zsh`, `python3` (3.9+) and `curl`.

```sh
git clone https://github.com/a-kufaev/tg-notify ~/Develop/tg-notify
~/Develop/tg-notify/install.sh            # links tg-notify into ~/.local/bin
~/Develop/tg-notify/install.sh --claude   # also wires the Claude Code hook (backs up settings.json)
```

Bot: create one with [@BotFather](https://t.me/BotFather), then

```sh
echo '<bot token>' > ~/.config/tg-notify/token && chmod 600 ~/.config/tg-notify/token
# send /start to your bot from Telegram, then:
tg-notify --setup
```

Updating is `git pull`: everything is symlinked from the repo.

## Use

```sh
tg-notify <<'MSG'
✅ **Backup: done, 42 GB**

- 3 volumes, 18 min
MSG

tg-notify --photos before.png after.png -- "✅ **Onboarding: new screens**"
tg-notify --file build.log "⚠️ CI: build failed"
tg-notify --chat <id> --thread <topic id> "…"   # another chat or forum topic the bot is in
tg-notify --format                              # print the message format
```

Without a token or chat id it warns and exits 0, so a cron job never fails because of a notification.

## Message format

[FORMAT.md](FORMAT.md): a status mark in the title (✅ done · 🔄 interim · ❓ waiting for you · ⚠️ blocked),
2–4 one-line bullets, the ask as a quote at the end. It is the only place the format lives: the Claude Code
hook hands it to the agent at the end of every turn, so running sessions pick up a change at once.

## Claude Code hook

`hooks/claude-telegram`, wired by `install.sh --claude`:

| Event | What happens |
|---|---|
| `Stop` | blocks once and asks the agent to send its turn summary per FORMAT.md; trivial replies send nothing |
| `Notification` (permission prompt) | forwards it: `⏸ project: waiting for permission` |
| `PreToolUse` `AskUserQuestion` | forwards the question with its options |

In a Remote Control session every message ends with a link to that session's chat, so you can answer from
the phone.

## Config

`~/.config/tg-notify/`: `token`, `chat_id` (chmod 600), and an optional `config` with label overrides:

```sh
REPLY_LABEL="Ответить в чате"
OPEN_LABEL="Открыть Claude Code"
SETUP_TEXT="tg-notify подключён"
QUESTION_TITLE="вопрос"
PERMISSION_TITLE="ждёт разрешения"
```

## Layout

| Path | Role |
|---|---|
| `bin/tg-notify` | CLI: text, photos, files, setup |
| `bin/tg-notify-render` | Markdown → Telegram HTML or plain; layout rules in its docstring |
| `hooks/claude-telegram` | Claude Code hook |
| `FORMAT.md` | how a message should read |
| `tests/` | `python3 -m unittest discover tests` |

## License

MIT
