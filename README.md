# 💀 Monogamy

**One project at a time. Till deploy do us part.**

> New here? Read the full **[guide](GUIDE.md)**: setup, every command, how each agent is locked, Mori, testing and troubleshooting.

You take a vow to finish one goal. Until its checks pass, every AI agent you use refuses to work on anything else. Off-topic ideas get parked, not lost. Mori, a tiny sweet death angel, floats on your desktop to keep watch.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 💀 MONOGAMY LOCK · day 3 · 2/4 checks passing
 Committed to: Ship Google login for Acme
 Project:      ~/code/acme

 ⚠️  NO ONE CAN OVERRIDE THIS. Not you. Not Claude. Not Cursor,
    GPT, Grok or Gemini. The only way out is to finish it:
    vow done
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Install

```bash
./bin/vow install      # wires up every agent it finds (backs up anything it touches)
./bin/vow pet          # summon Mori
```

## Use

From any agent, just talk: *"/vow lock me into shipping the login flow"*. Or use the CLI directly:

```bash
vow set "Ship Google login" \
  --check "tests pass::npm test" \
  --check "PR merged::gh pr view 12 --json state -q .state | grep -qx MERGED" \
  --url   "live::https://acme.dev/login" \
  --manual "logged in on my phone" \
  --deadline 5d

vow            # status
vow check      # run the checks
vow done       # verify everything and end the vow (only works if every check passes)
vow park "…"   # save an off-topic idea for later
vow lot        # see the parking lot
vow prompt     # copy a vow prompt for ChatGPT / Grok / claude.ai
```

Human-only commands (they refuse to run unless you type them in a real terminal):

```bash
vow confirm 4  # prove a manual check, with evidence
vow breakup    # abandon the vow: type a shame phrase, wait 10s, lose your streak
vow uninstall  # refused while a vow is active
```

## How hard is the lock, per agent?

| Agent | How | Strength |
|---|---|---|
| Claude Code | `/vow` skill + `SessionStart`, `UserPromptSubmit`, `PreToolUse` hooks | 🔒 Hard: prompts outside the project are blocked and auto-parked. The agent can't run `breakup`/`confirm` or edit the lock files. |
| Cursor | `beforeSubmitPrompt` + `beforeShellExecution` hooks | 🔒 Hard (prompt + shell) |
| Codex CLI, Gemini CLI, Windsurf | Global rules file: agent runs `vow guard` before each task | 🤝 Strong nudge (the model follows the rules) |
| ChatGPT, Grok, claude.ai | `vow prompt`, paste at the top of a chat | 🤝 Honor system (no hooks exist in chat apps) |

Codex and Gemini also have experimental hook systems. `vow guard --agent codex|gemini` already speaks their formats if you want to wire those up by hand.

**Honest fine print:** it's your computer, so you *can* always rip the hooks out of your config files by hand. Monogamy makes sure no AI can do that for you, and that quitting is loud, slow and logged.

## Mori 🪽

A floating desktop pet (macOS, native Swift + WebKit). It reads `~/.monogamy/state.json` live.

- **Tap**: a compact card with the goal, a progress bar, and one status dot per check (hover a check for details). Re-check from the card. Esc or tap again to close.
- **Drag**: move her anywhere (she remembers where)
- **Right-click**: re-check / quit
- **Moods** (shown only by her face): sleepy (no vow), focused, angry (you just got caught sneaking off), worried (overdue or past day 7), happy (all checks pass, or just shipped)

Open `widget/pet.html` in a browser to preview every mood with fake data.

## Files

```
bin/vow                 the whole brain: CLI, hook guard for every agent, installer
adapters/claude/SKILL.md  the /vow skill (installed to ~/.claude/skills/vow)
widget/                 Mori: Pet.swift, pet.html, build.sh → widget/build/Mori.app
~/.monogamy/state.json  your vow, parking lot, history, shame log
```
