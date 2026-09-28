# Dos Margaritas Salsa — Team Tools

## 🔗 [Open the live site](https://maxmoon23.github.io/dosmargarita_ORG/)

That link above is the actual website. This page you're looking at right
now is just the code storage — there's no "open" button here because
this isn't the site itself.

---

An internal site for Michael and Maggie to run the store network: SOPs,
file links, and small helper tools.

## What's inside

- **`index.html`** — the landing page (the 8-bit factory).
- **`employee-tools.html`** — the latitude/longitude finder. Type in an
  address (or a store name + city), and it looks up the coordinates
  using OpenStreetMap's free, no-key-needed search. Built for pasting
  the result straight into Shopify's "Map pin" block when adding a
  store to the site.
- **`factory-agent/`** — a separate, optional Python tool: a real AI agent
  (built on the Claude API) you run yourself from a terminal to log
  customer interactions/orders, track tasks/reminders, and get quick
  reports/segmentation over the Master Store List. Needs your own
  Anthropic API key and costs a small amount per use — see
  `factory-agent/README.md` for setup, cost, and how it works. Your real
  data stays local on your computer (gitignored on purpose) — it never
  gets committed to this public repo.

## How to run the website without the internet

Double-click `index.html` (or open it in a browser) — works completely
offline too, no install, no setup.

For the rules this project is built around (durability, privacy,
never touching Shopify), see `CLAUDE.md` in this repo.
