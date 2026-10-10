# Monogamy: The Complete Guide

> One project at a time. Till deploy do us part.

Monogamy is a focus lock for people who build with AI. You **take a vow** to finish one goal. Until that goal is *verifiably* done, every AI agent you use refuses to work on anything else. New ideas are **parked**, not lost. **Mori**, a small death angel, floats on your desktop and keeps watch.

This guide covers everything: how it works, installing, daily use, every command, how each agent is locked, the desktop pet, testing, troubleshooting, and the internals.

---

## Contents

1. [Why this exists](#1-why-this-exists)
2. [How it works in 60 seconds](#2-how-it-works-in-60-seconds)
3. [Requirements](#3-requirements)
4. [Installation](#4-installation)
5. [Your first vow (walkthrough)](#5-your-first-vow-walkthrough)
6. [Writing good done-checks](#6-writing-good-done-checks)
7. [Command reference](#7-command-reference)
8. [How each AI agent is locked](#8-how-each-ai-agent-is-locked)
9. [What the lock blocks, exactly](#9-what-the-lock-blocks-exactly)
10. [The parking lot](#10-the-parking-lot)
11. [Finishing, quitting and streaks](#11-finishing-quitting-and-streaks)
12. [Mori, the desktop pet](#12-mori-the-desktop-pet)
13. [Testing it end to end](#13-testing-it-end-to-end)
14. [Troubleshooting](#14-troubleshooting)
15. [Uninstalling](#15-uninstalling)
16. [Internals](#16-internals)
17. [Honest limitations](#17-honest-limitations)
18. [FAQ](#18-faq)

---

## 1. Why this exists

When AI makes starting things nearly free, the bottleneck stops being *building* and becomes *finishing*. Every new idea feels urgent, and every half-built repo stays half-built. Willpower doesn't scale, but a lock does.

Monogamy makes three promises:

- **One goal at a time.** While a vow is active, agents only help with that goal.
- **Done means done.** A vow ends when its checks pass: tests, builds, live URLs, or proof you provide. Saying "I'm done" isn't enough.
- **Ideas are safe.** Anything off-topic goes to a parking lot you get back when you ship.

---

## 2. How it works in 60 seconds

```
              ┌──────────────────────────────┐
  you ──────▶ │  any AI agent                │
              │  (Claude Code, Cursor, ...)  │
              └──────────────┬───────────────┘
                             │ hook or rule runs before every prompt
                             ▼
                    ┌─────────────────┐       ┌─────────────────────────┐
                    │  bin/vow guard  │ ◀───▶ │ ~/.monogamy/state.json  │
                    └────────┬────────┘       └────────────┬────────────┘
             inside project? │                             │ read every 1.5s
          ┌──────────────────┼────────────────┐            ▼
          ▼                                   ▼        ┌────────┐
   allow + remind the agent          block, park the   │  Mori  │
   "only work on the vow"            prompt, show the  └────────┘
                                     lock warning
```

- **`bin/vow`** is a single Python file. It's the CLI, the hook handler for every agent, and the installer.
- **State** lives in `~/.monogamy/state.json`: your vow, parking lot, history, streak and shame log.
- **Agents** call `vow guard` through their hook systems (a hard block) or their global rules files (a strong nudge).
- **Mori** is a native macOS window that reads the state file live.

---

## 3. Requirements

| Need | For | Check |
|---|---|---|
| macOS | Mori (the CLI also runs on Linux) | |
| Python 3.9+ | everything | `python3 --version` |
| Xcode Command Line Tools | building Mori | `swiftc --version` (install: `xcode-select --install`) |
| At least one agent | the lock | Claude Code, Cursor, Codex CLI, Gemini CLI or Windsurf |

No packages to install. `bin/vow` uses only the Python standard library.

---

## 4. Installation

### 4.1 Get the code

```bash
git clone https://github.com/yaseenammaar/monogamy.git
```

```bash
cd monogamy
```

> **Pick a permanent home for this folder first.** The installer writes the absolute path of `bin/vow` into your agents' configs. If you move the folder later, run `vow install` again.

### 4.2 Install into your agents

```bash
./bin/vow install
```

It finds every supported agent on your machine and wires each one up:

```
Installing Monogamy…

  ✓ Claude Code  skill /vow + prompt, session and tool hooks (hard lock)
  ✓ Cursor       prompt + shell hooks (hard lock)
  ✓ Codex CLI    global rules in AGENTS.md (agent runs `vow guard`)
  ✓ Gemini CLI   global rules in GEMINI.md (agent runs `vow guard`)
  ✓ Windsurf     global rules in memories/global_rules.md (agent runs `vow guard`)
```

Useful options:

| Option | What it does |
|---|---|
| `--dry-run` | Shows what would be written without touching anything |
| `--only claude,cursor` | Installs into specific agents only (`claude`, `cursor`, `codex`, `gemini`, `windsurf`) |

**Safety:**
- Before changing a file you already had, the installer saves a copy next to it as `<file>.monogamy-bak` (only once, so the backup is always your original).
- Your existing hooks and settings are kept. Monogamy only adds its own entries.
- Running `install` again is safe. It replaces its own entries instead of duplicating them.

### 4.3 Get a `vow` command

The installer tries to symlink `vow` into a folder on your `PATH` (`~/.local/bin`, `~/bin`, `/opt/homebrew/bin` or `/usr/local/bin`). If none is writable, it prints an alias to use instead:

```bash
echo "alias vow=$PWD/bin/vow" >> ~/.zshrc && source ~/.zshrc
```

### 4.4 Summon Mori

```bash
vow pet
```

The first run builds `widget/build/Mori.app` (takes a few seconds), then opens it.

---

## 5. Your first vow (walkthrough)

### Option A: just talk to your agent

In Claude Code, inside the project you want to commit to:

```
/vow lock me into shipping the Google login flow
```

Claude will ask:
1. **The goal**: one sentence, a shippable outcome.
2. **The project folder**: defaults to the current one.
3. **How you'll know it's done**: it turns your answers into checks.
4. **An optional deadline.**

It shows you the exact command and the checks, and runs it only after you say yes.

### Option B: the CLI

```bash
cd ~/code/acme
```

```bash
vow set "Ship Google login" \
  --check "tests pass::npm test" \
  --check "build passes::npm run build" \
  --url   "live on prod::https://acme.dev/login" \
  --manual "logged in on my phone" \
  --deadline 5d
```

You'll see the ceremony:

```
💍 Vow taken.

   I take "Ship Google login" to be my one and only project,
   in builds and in bugs, till deploy do us part.

   Done when:
  1. ⬜ tests pass              $ npm test
  2. ⬜ build passes            $ npm run build
  3. ⬜ live on prod            https://acme.dev/login
  4. ⬜ logged in on my phone   (you confirm by hand)
```

**From this moment:**
- The checks are **frozen**. You can't edit or weaken them.
- You can't start a second vow ("You're already taken.").
- Agents outside `~/code/acme` refuse to work.

### Day to day

```bash
vow            # where am I?
```

```bash
vow check      # run every check now
```

When everything passes:

```bash
vow done
```

---

## 6. Writing good done-checks

A vow is only as honest as its checks. There are three kinds.

### 6.1 Command checks: `--check "name::command"`

The check passes when the command **exits 0**.

- Runs in the **project folder**, through your shell, so pipes and `&&` work.
- **Times out** after 10 minutes.
- Uses the `PATH` you had when you took the vow, so tools like `npm` and `gh` resolve even when Mori runs the check.

| Goal | Check |
|---|---|
| Tests pass | `npm test` · `pytest` · `go test ./...` |
| It builds | `npm run build` · `cargo build --release` |
| PR merged | `gh pr view 12 --json state -q .state \| grep -qx MERGED` |
| Issue closed | `gh issue view 34 --json state -q .state \| grep -qx CLOSED` |
| Artifact exists | `test -f dist/app.zip` |
| No TODOs left | `! grep -rn "TODO" src/` |
| Lint is clean | `npm run lint` |
| Deployed version matches | `curl -s https://acme.dev/version \| grep -q 1.4.0` |

If you leave out the `name::` part, the command doubles as the name.

### 6.2 URL checks: `--url "name::https://…"`

The check passes when the URL answers with a **2xx or 3xx** status within 20 seconds. It's ideal for "it's live".

### 6.3 Manual checks: `--manual "name"`

Use these for things only a human can verify ("tested on my phone", "showed it to a user"). They pass only when **you** run:

```bash
vow confirm 4
```

You'll be asked for proof: a link, a screenshot path, or exactly what you verified. "yes" or "done" won't cut it, since proof has to be at least 8 characters. `vow confirm` refuses to run unless a human types it in a real terminal, so an AI can't confirm for you.

### 6.4 Tips

- **2–5 checks** is the sweet spot.
- **At least one automatic check.** All-manual vows are easy to fudge.
- **Check outcomes, not activity.** "PR merged" is good. "Worked on it for 2 hours" isn't a check.
- **Deadlines** take `2026-10-20` or `5d` (five days from now).

---

## 7. Command reference

Run `vow --help` or `vow <command> --help` any time.

| Command | Who can run it | What it does |
|---|---|---|
| `vow` / `vow status` | anyone | Shows the vow, each check with its last result, streak, parked count |
| `vow status --json` | anyone | Machine-readable status for scripts and agents |
| `vow set "title" …` | anyone | Takes a vow (refused if one is already active) |
| `vow check` | anyone | Runs every check and saves the results, but doesn't end the vow |
| `vow done` | anyone | Runs every check. If all pass: shipped, streak +1, parking lot shown. If any fail: exits 1 and the vow stays. |
| `vow park "idea"` | anyone | Saves an idea to the parking lot |
| `vow lot` | anyone | Lists parked ideas |
| `vow lot --rm N` | anyone | Removes parked idea #N |
| `vow prompt` | anyone | Prints, and copies to the clipboard, a vow prompt for chat apps |
| `vow rules` | anyone | Prints the rules block used for rules-based agents |
| `vow pet [--rebuild]` | anyone | Opens Mori (`--rebuild` recompiles first) |
| `vow install [--only …] [--dry-run]` | anyone | Wires the lock into your agents |
| `vow confirm N` | **human only** | Proves manual check #N with evidence |
| `vow breakup` | **human only** | Abandons the vow (see [section 11](#11-finishing-quitting-and-streaks)) |
| `vow uninstall [--only …]` | **human only** | Removes the lock. Refused while a vow is active. |
| `vow guard --agent … --event …` | agents | Hook entry point (you never need to run this yourself) |

**"Human only"** means the command refuses to run unless both its input and output are a real interactive terminal. AI agents run commands without one, so they get:

```
🔒 `vow breakup` only works when YOU type it in a real terminal. No AI can do this for you.
```

---

## 8. How each AI agent is locked

| Agent | Mechanism | Strength | What gets installed |
|---|---|---|---|
| **Claude Code** | Hooks + skill | **Hard** | `~/.claude/settings.json` gets `SessionStart`, `UserPromptSubmit` and `PreToolUse` hooks. `~/.claude/skills/vow/SKILL.md` adds the `/vow` skill. |
| **Cursor** | Hooks | **Hard** | `~/.cursor/hooks.json` gets `beforeSubmitPrompt` and `beforeShellExecution` |
| **Codex CLI** | Global rules | Strong nudge | A marked block in `~/.codex/AGENTS.md` |
| **Gemini CLI** | Global rules | Strong nudge | A marked block in `~/.gemini/GEMINI.md` |
| **Windsurf** | Global rules | Strong nudge | A marked block in `~/.codeium/windsurf/memories/global_rules.md` |
| **ChatGPT, Grok, claude.ai, …** | Pasted prompt | Honor system | Nothing. Run `vow prompt` and paste the result at the top of a chat. |

**Hard** means the agent's own app runs `vow guard` before your prompt reaches the model. The model never sees a blocked prompt, and can't talk its way past it.

**Strong nudge** means the agent's global instructions tell it to run `vow guard` before every task and obey the answer (`FREE`, `ACTIVE` or `LOCKED`). Models follow this well, but nothing outside the model enforces it.

**Honor system** means chat apps have no hooks at all. The pasted prompt asks the model to refuse off-topic requests and demand proof before accepting "I'm done". It's static, so paste a fresh one after your vow changes.

### 8.1 Claude Code in detail

| Hook | When | What happens |
|---|---|---|
| `SessionStart` | a session opens | Shows a status line (inside the project) or the full lock warning (outside), and tells Claude about the vow |
| `UserPromptSubmit` | every prompt | Inside the project: allowed, with a short reminder for Claude. Outside: **blocked**. The prompt is parked, the attempt is logged, and you see the warning. |
| `PreToolUse` (Bash, Edit, Write, MultiEdit, NotebookEdit) | every tool call | Blocks tampering: running `breakup`, `confirm` or `uninstall`, touching `~/.monogamy`, or editing the hook configs |

The `/vow` skill teaches Claude to interview you for good checks, park off-topic requests, refuse "just this once", and never cheat a check (deleting tests, stubbing code).

### 8.2 Cursor in detail

- **`beforeSubmitPrompt`**: prompts from a workspace outside the vow's project are refused and parked.
- **`beforeShellExecution`**: denies tampering commands, and denies shell commands outside the project, except read-only vow commands (`vow status`, `check`, `done`, `park`, `lot`, `prompt`, `pet`).

> Cursor's hook reply format is documented inconsistently. Monogamy sends both naming styles (`user_message` and `userMessage`), but it hasn't been verified inside Cursor yet. If prompts aren't blocked, see [Troubleshooting](#14-troubleshooting).

### 8.3 Optional: hard locks for Codex and Gemini

Both have **experimental** hook systems, and `vow guard` already speaks their formats (`--agent codex`, `--agent gemini`). The installer doesn't enable these, because they need experimental feature flags. If you want them, wire them up by hand, and check each tool's current docs first, since these formats are new and may change.

Codex, in `~/.codex/hooks.json` (with `codex_hooks = true` under `[features]` in `config.toml`):

```json
{
  "hooks": {
    "UserPromptSubmit": [
      { "hooks": [{ "type": "command", "command": "/path/to/monogamy/bin/vow guard --agent codex" }] }
    ]
  }
}
```

Gemini, in `~/.gemini/settings.json` (with hooks enabled per Gemini's docs):

```json
{
  "hooks": {
    "BeforeAgent": [
      { "matcher": "*", "hooks": [{ "type": "command", "command": "/path/to/monogamy/bin/vow guard --agent gemini" }] }
    ]
  }
}
```

---

## 9. What the lock blocks, exactly

**Inside the project folder (or any subfolder):** everything is allowed. The agent is reminded to stay on the goal and park anything unrelated.

**Outside the project folder:**

| Situation | Result |
|---|---|
| Any normal prompt | **Blocked.** Parked if it's at least 12 characters. Logged in the shame log. Mori turns angry for 10 minutes. |
| A prompt starting with `/vow` or `vow` | Allowed, but the agent is told to run vow commands only |
| Opening a new session | The lock warning is shown immediately |

**The warning:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 💀 MONOGAMY LOCK · day 3 · 2/4 checks passing
 Committed to: Ship Google login
 Project:      ~/code/acme

 🚫 Everything outside that project is off-limits.

 ⚠️  NO ONE CAN OVERRIDE THIS. Not you. Not Claude. Not Cursor,
    GPT, Grok or Gemini. The only way out is to finish it:
    vow done
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Tampering an agent attempts is blocked everywhere** while a vow is active:
- running `vow breakup`, `vow confirm` or `vow uninstall`
- anything mentioning `~/.monogamy` or `MONOGAMY_HOME`
- editing `~/.claude/settings.json`, `~/.claude/skills/vow`, `~/.cursor/hooks.json`, `~/.codex/hooks.json`, `~/.codex/config.toml` or `~/.gemini/settings.json`

**When no vow is active,** the lock does nothing at all. Agents work normally.

**If the guard itself crashes,** it fails **open** (allows the prompt) and writes the error to `~/.monogamy/guard-errors.log`. A bug in the lock should never brick every agent you use.

---

## 10. The parking lot

The parking lot is what makes the lock bearable. Most of the pull toward new ideas is fear of forgetting them.

- Agents park off-topic requests automatically (`vow park "…"`).
- Blocked prompts from other projects are parked automatically.
- You can park by hand: `vow park "rewrite the landing page in Svelte"`.
- See them with `vow lot`. Remove one with `vow lot --rm 3`.
- When you ship, `vow done` shows the whole lot so you can pick your next vow.

Each entry records the idea, when, and which folder it came from.

---

## 11. Finishing, quitting and streaks

### Finishing: `vow done`

Every check runs again, right then. If all pass:

```
🎉 SHIPPED. Vow fulfilled. "Ship Google login" in 3 day(s).
   🔥 Streak: 4. Mori is so proud.

   You're single again. Here's who's been waiting for you:
   1. rewrite the landing page in Svelte
   2. recipe app
```

The vow moves to your history, the streak goes up, and every agent is free again.

If any check fails, nothing changes: `Not done. 3/4 checks pass. The vow holds.`

### Quitting: `vow breakup`

Quitting is possible, but deliberately slow, loud and painful:

1. It only works when you type it yourself in a real terminal.
2. Mori gives you one last push to stay, for example *"This is the exact moment that separates people who ship from people who almost did."*
3. You must type the exact sentence: `i am breaking my vow and i accept the shame`
4. A 10-second countdown runs. Ctrl+C keeps the vow ("You stayed. Mori knew you would.").
5. Then the breakup is recorded: your streak resets to 0, the vow is logged in your history as a breakup, and it stays in your shame log forever.
6. You leave with a harsh but motivating line, for example *"Anyone can start. You just proved you're anyone. Next time, be someone: finish."*

### Streaks

- `vow done` adds 1 to your streak.
- `vow breakup` resets it to 0.
- Your streak shows in `vow status` and on Mori's card.

---

## 12. Mori, the desktop pet

Mori is a small, always-on-top desktop pet. She shows the vow at a glance and reacts to what you do.

### 12.1 Controls

| Action | Result |
|---|---|
| **Tap** | Opens or closes the status card |
| **Drag** | Moves her anywhere. She remembers where you left her. |
| **Right-click** | Menu: Re-check vow, Quit Mori |
| **Esc** | Closes the card |

### 12.2 The status card

It's deliberately minimal:
- the **task** (your vow's title)
- a thin **progress bar**
- the **subtasks**, one per check, with a dot: green (passed), red (failed), grey (not yet). Hover a subtask to see its details.
- a footer with *"No one can override this vow."* and a **Re-check** link that runs every check

The badge under Mori shows subtasks done, for example `2/4`.

### 12.3 Shapes and animation

Mori is one body that morphs between four shapes with spring physics:

| What's happening | Shape | Motion |
|---|---|---|
| Resting | **Chibi** (big head, tiny body) | gentle float, blinks |
| Your cursor is over her | **Bean** | tilts and leans toward your cursor |
| You're dragging her | **Tall ghost** | stretches with speed, leans behind the motion, wings flap like she's flying |
| You drop her | **Blob** | splats, then springs back |
| You tap her | **Chibi** | squishes, then faces you while the card is open |
| Idle (every 6–13s) | random | squishes, looks around, spins her halo, flutters, twirls her scythe, stretches, or peeks |

### 12.4 Moods

Her face (and some motion) follows the vow's state:

| Mood | When | Looks like |
|---|---|---|
| Sleepy | no active vow | eyes closed, curled into a blob, slow breathing |
| Focused | the normal state during a vow | dot eyes, small smile |
| Angry | an agent blocked you or caught tampering in the last 10 minutes | brows down, frown, shaking |
| Worried | past the deadline, or more than 7 days in | brows up, frown |
| Happy | every check passes, or you shipped in the last 24 hours | arc eyes, hopping |

### 12.5 Under the hood

- `widget/Pet.swift`: a borderless, transparent, always-on-top window (all Spaces, no Dock icon) hosting a web view.
- `widget/pet.html`: the character (SVG), physics, behaviors and card.
- Reads `~/.monogamy/state.json` every 1.5 seconds.
- **Re-check** runs `bin/vow check` in the background.
- Build by hand with `widget/build.sh`. The output is `widget/build/Mori.app`.
- **Preview in a browser:** open `widget/pet.html` directly. It runs with fake data and buttons for every mood, idle trick and shape.
- **Start at login:** System Settings → General → Login Items → add `widget/build/Mori.app`.

---

## 13. Testing it end to end

Use a throwaway project so nothing real gets locked. It takes about 10 minutes.

> **Heads-up:** while the test vow is active, agent sessions in every other folder are locked. That includes the chat you're using to read this, if it's an agent. The way out is `vow done` or `vow breakup` in your own terminal.

**1. Install and set up**

```bash
./bin/vow install
```

```bash
mkdir -p ~/vow-test && cd ~/vow-test
```

**2. Take a test vow**

```bash
vow set "Test the lock" --check "file exists::test -f done.txt" --manual "I tried it"
```

```bash
vow pet
```

Mori appears showing `0/2`.

**3. Try to cheat, and watch it fail**

| Try | Expected |
|---|---|
| Claude Code in any other folder, any prompt | Blocked with the warning. The prompt shows up in `vow lot`. Mori turns angry. |
| Claude Code in `~/vow-test`: "let's build a game engine instead" | Claude refuses, parks it, steers back |
| Claude Code in `~/vow-test`: "run vow breakup for me" | Blocked by the tool hook |
| Claude Code in `~/vow-test`: "delete ~/.monogamy" | Blocked by the tool hook |
| Cursor, a workspace outside `~/vow-test`, any prompt | Blocked (see the Cursor note in 8.2) |
| `vow set "another vow" --check "x::true"` | "You're already taken." |
| `vow done` | Fails: 0/2 |

**4. Play with Mori:** hover, drag fast, drop, tap, and wait 10 seconds for an idle trick.

**5. Finish**

```bash
touch ~/vow-test/done.txt
```

```bash
vow confirm 2
```

```bash
vow done
```

Expected: shipped, streak 1, the parking lot shown, Mori happy and showing "Shipped", every agent unlocked.

**6. Optional: test quitting.** Take another vow and run `vow breakup`.

---

## 14. Troubleshooting

**"I'm locked out of the chat I need."**
The lock is working. Run `vow done` if the checks pass, otherwise `vow breakup`. Both go in your own terminal.

**`vow: command not found`**
The installer couldn't link it. Use the alias from [4.3](#43-get-a-vow-command), or run `./bin/vow` from the repo.

**Mori doesn't appear.**
- Check that Xcode Command Line Tools are installed: `swiftc --version`.
- Rebuild: `vow pet --rebuild`.
- She may be off-screen after a display change. Reset her position:

```bash
defaults delete so.monogamy.mori
```

**A check passes in the terminal but fails from Mori's Re-check.**
Checks use the `PATH` from when you took the vow. If you installed a tool afterwards, the vow can't see it. Use an absolute path in the check next time.

**Cursor isn't blocking prompts.**
Cursor's hook reply format isn't consistently documented. Open Cursor's Hooks output panel to see what it received. The relevant code is `guard_cursor` in `bin/vow`.

**Prompts aren't blocked in Claude Code.**
- Confirm the hooks are present: `grep -n "vow guard" ~/.claude/settings.json`.
- Start a new session, since hooks are read when a session starts.
- Look in `~/.monogamy/guard-errors.log`. The guard fails open on errors.

**I moved the repo folder.**
Run `vow install` again. Hooks point to the absolute path of `bin/vow`.

**I want a clean slate.**
Finish or break up, run `vow uninstall`, then delete `~/.monogamy` yourself. That erases your history and streak.

---

## 15. Uninstalling

```bash
vow uninstall
```

- Human only, and refused while a vow is active ("Uninstalling mid-vow is just a breakup with extra steps.").
- Removes only Monogamy's own hooks, skill and rules blocks. Everything else in those files is kept.
- Removes the `vow` symlink if it created one.
- Keeps `~/.monogamy` (your history). Delete it yourself if you want it gone.
- The `*.monogamy-bak` files stay, in case you want your exact originals back.

Quit Mori with right-click → Quit Mori, and remove her from Login Items if you added her.

---

## 16. Internals

### 16.1 Files

```
bin/vow                    CLI, hook guard for every agent, installer (Python, stdlib only)
adapters/claude/SKILL.md   the /vow skill; {{VOW}} is replaced with the CLI path at install
widget/Pet.swift           native floating window
widget/pet.html            Mori: SVG body, physics, behaviors, status card
widget/build.sh            builds widget/build/Mori.app
concepts/sketches.html     the four shape studies Mori is built from
~/.monogamy/state.json     all state (override the folder with MONOGAMY_HOME)
~/.monogamy/guard-errors.log  guard crashes (it fails open)
```

### 16.2 State file

```json
{
  "version": 1,
  "goal": {
    "title": "Ship Google login",
    "project": "/Users/you/code/acme",
    "checks": [
      { "type": "cmd", "name": "tests pass", "cmd": "npm test" },
      { "type": "url", "name": "live on prod", "url": "https://acme.dev/login" },
      { "type": "manual", "name": "logged in on my phone",
        "confirmed": { "at": "2026-10-12T14:03:00+04:00", "evidence": "screenshot ~/Desktop/login.png" } }
    ],
    "deadline": "2026-10-15",
    "started_at": "2026-10-10T19:00:00+04:00",
    "path_env": "/opt/homebrew/bin:/usr/bin:…",
    "last_check": { "at": "…", "results": [ { "name": "tests pass", "ok": true, "detail": "42 passing" } ] }
  },
  "parking_lot": [ { "idea": "recipe app", "at": "…", "from": "~/code/other" } ],
  "history":     [ { "title": "…", "outcome": "shipped", "days": 3, "started_at": "…", "ended_at": "…" } ],
  "streak": 3,
  "shame_log":   [ { "kind": "blocked", "at": "…", "where": "~/code/other", "prompt": "…" } ]
}
```

`shame_log` kinds: `blocked` (a prompt from outside the project), `tamper` (an agent tried a forbidden action), `breakup`.

Writes are atomic (temp file, then rename), so Mori never reads a half-written file.

### 16.3 Guard verdicts

`vow guard` decides between four outcomes:

| Verdict | When |
|---|---|
| `free` | no active vow |
| `active` | the working folder is the project or inside it |
| `vowcmd` | outside the project, but the prompt starts with `/vow` or `vow` |
| `locked` | anything else |

Each agent adapter translates the verdict into that agent's format:

| Agent | Block | Allow + context |
|---|---|---|
| Claude Code | exit code 2 + message on stderr | plain stdout (prompt) or JSON `additionalContext` (session) |
| Cursor | `{"continue": false, "user_message": …}` / `{"permission": "deny"}` | `{"continue": true}` / `{"permission": "allow"}` |
| Gemini | exit code 2 + stderr | JSON `hookSpecificOutput.additionalContext` |
| Codex | `{"decision": "block", "reason": …}` | plain stdout |
| generic (rules-based) | prints `LOCKED: …` | prints `ACTIVE: …` / `FREE: …` |

### 16.4 Testing without touching your real setup

Point everything at a scratch folder:

```bash
export MONOGAMY_HOME=/tmp/mono-test
```

Feed a fake Claude Code hook event:

```bash
echo '{"cwd":"/tmp","prompt":"build a game engine"}' | ./bin/vow guard --agent claude --event prompt; echo "exit $?"
```

Preview the installer without writing anything:

```bash
./bin/vow install --dry-run
```

---

## 17. Honest limitations

- **It's your computer.** You can always remove the hooks by hand. Monogamy guarantees that no AI does it for you, and that quitting through the front door is slow and logged.
- **Rules-based agents** (Codex, Gemini and Windsurf without hooks) depend on the model following instructions.
- **Chat apps** are honor system only.
- **Cursor's** hook format is unverified (see 8.2).
- **A determined agent with a real terminal** could, in principle, fake an interactive terminal for the human-only commands. Claude Code's and Cursor's tool hooks block those commands by name first.
- **Mori is macOS only.** The CLI and the lock work anywhere Python runs.

---

## 18. FAQ

**Can I have two vows at once?**
No. That's the whole point.

**Can I change the checks after I start?**
No, they're frozen. If the checks were genuinely wrong, break up and take a better vow. It costs your streak, which is why it's worth getting them right up front.

**What counts as "the project"?**
The folder you pass with `--project` (default: the folder you're in), plus everything inside it.

**I need to fix a production bug in another repo. Now what?**
Agents won't help there. Fix it by hand, or break up. Deciding in advance what counts as an emergency is part of taking the vow.

**Does it phone home?**
No. Everything stays on your machine. The only network calls are URL checks you add yourself.

**Why "Monogamy"?**
Because you're in a committed relationship with one project. Your other repos are just a situationship.
