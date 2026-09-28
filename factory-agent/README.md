# Factory Agent

A little AI assistant you run yourself, from a terminal, that can log
customer interactions and orders, track tasks/reminders, and give you
quick reports over the Master Store List. This is separate from the
factory website (`index.html`) — the website still works with zero cost
and zero setup; this is an extra tool you run only when you want it.

## How it actually works (read this first)

This is **not** a chatbot with secret magic — it's Claude (Anthropic's AI)
plus a short list of plain Python functions ("tools") it's allowed to call:
things like `log_interaction`, `add_task`, `segment_stores`. When you type
something like "log that I dropped samples at Acme Grocery today," here's
what happens:

1. Your message goes to Claude along with the list of tools it's allowed to use.
2. Claude decides "this sounds like `log_interaction`" and says so.
3. **Your own computer** — not Claude, not Anthropic — actually runs that
   Python function and saves it to a file on your machine.
4. The result gets sent back to Claude, which then replies to you in plain English.

Nothing is hidden from you: `agent.py` prints a line every time a tool
actually gets used, so you can always see exactly what it did.

- `storage.py` — reads/writes the data files. No AI involved.
- `tools.py` — the functions Claude is allowed to call. **This is the file
  you'll edit most** if you want to teach the agent something new.
- `agent.py` — the chat loop that ties it together. You shouldn't need to
  touch this much.
- `data/` — where your data actually lives (see "Your data" below).

## Setup (one-time)

1. **Get an Anthropic API key.** This is separate from any Claude.ai
   subscription — it's pay-as-you-go, billed to whoever creates it. Go to
   [console.anthropic.com](https://console.anthropic.com), make an account
   (yours or Maggie's — whoever should own the billing), add a payment
   method, and create a key under **Settings → API Keys**. Treat this key
   like a password — anyone with it can spend money on your account.

2. **Set the key as an environment variable** so the code can find it
   without you ever typing it into a file:

   ```bash
   export ANTHROPIC_API_KEY="the-key-you-just-made"
   ```

   Add that line to your shell's startup file (`~/.zshrc` or `~/.bashrc`)
   so you don't have to retype it every time you open a new terminal.

3. **Install the one dependency:**

   ```bash
   cd factory-agent
   pip install -r requirements.txt
   ```

4. **Run it:**

   ```bash
   python agent.py
   ```

   Type `exit` to quit.

## What it can do right now

Just talk to it normally — you don't need to know the tool names. Some things to try:

- "Log an interaction: I called Acme Grocery today, talked to Jane, she wants to reorder next month."
- "Log an order: Acme Grocery ordered 12 jars mild, 6 jars hot, $84."
- "What's the recent activity with Acme Grocery?"
- "Remind me to follow up with Acme Grocery on the 5th."
- "What tasks do I have open?"
- "Mark task 3 as done."
- "Break down the stores by status." *(needs `data/stores.csv` — see below)*
- "Give me a summary of everything going on."

## Adding the Master Store List (for segmentation/reporting)

The agent doesn't have live access to Google Sheets (that's a bigger,
separate step — see Roadmap below). For now:

1. Open the real Master Store List in Google Sheets.
2. **File → Download → Comma Separated Values (.csv)**
3. Save/move that file to `factory-agent/data/stores.csv` (replacing
   whatever's there).
4. Re-export it whenever the list changes meaningfully. The agent just
   reads whatever's in that file at the moment you ask.

## Your data — where it lives, and what stays private

- Everything you log is saved locally on your computer, in
  `data/activity_log.json`, `data/tasks.json`, and `data/stores.csv`.
- **None of those three files are committed to git** — they're listed in
  `.gitignore` on purpose, because this repo is public. Real customer
  names, order amounts, and the store list itself should never end up on
  GitHub for anyone to see.
- That said: when you ask the agent a question that needs one of those
  files, the *relevant* data gets sent to Anthropic's servers as part of
  that request — same as with any Claude conversation. Don't log anything
  here you wouldn't be comfortable being in a normal AI chat.

## What this costs

This uses your own API key, billed per use — there's no flat subscription.
Using `claude-sonnet-5` (the default model here), a typical message —
your question, the tool descriptions, a short reply — costs a fraction of
a cent. Even chatting with it heavily every single day would very likely
land well under $5–10/month. You can check exact spend anytime at
[console.anthropic.com](https://console.anthropic.com) under **Usage**.

To use a different model, set `FACTORY_AGENT_MODEL` before running, e.g.
`FACTORY_AGENT_MODEL=claude-opus-5 python agent.py` for a smarter-but-pricier
model on something that needs more careful thinking.

One current limitation worth knowing: the conversation history sent to
Claude grows with every message in a session (so it remembers what you
just said), which means a very long single sitting slowly costs a bit more
per message than a fresh one. Starting a new session (just re-running
`python agent.py`) resets that.

## Roadmap / not built yet

- **Live Google Drive/Sheets access** (reading and writing the real Master
  List directly, instead of a manual CSV export) — this needs its own
  Google Cloud setup (OAuth credentials) and is a good next step once
  you're comfortable with how this version works.
- **Shopify** — and it never will touch Shopify directly, on purpose (see
  the root `CLAUDE.md` — no real login/password, ever; only a scoped token
  Maggie approves herself, and even then, reading only).
