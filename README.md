# Dos Margaritas Salsa — Team Tools

An internal site for Michael and Maggie to run the store network: SOPs,
file links, and small helper tools. This repo is dedicated to Dos
Margaritas job work only — kept separate on purpose from Michael's
personal coding/learning repo.

Built to be **durable on purpose** — plain HTML/CSS/JavaScript, no
server, no login, no dependency on any AI service staying online.

## How to run it

Double-click `index.html` (or open it in a browser) — that's it. No
install, no setup.

If GitHub Pages is turned on for this repo (Settings → Pages → Deploy
from branch `main`, folder `/root`), it's also reachable at:
`https://maxmoon23.github.io/dosmargarita_org/`

## What's inside

- **`index.html`** — the landing page with links to every section.
- **`employee-tools.html`** — the latitude/longitude finder. Type in an
  address (or a store name + city), and it looks up the coordinates
  using OpenStreetMap's free, no-key-needed search. Built for pasting
  the result straight into Shopify's "Map pin" block when adding a
  store to the site.

## What's *not* here (on purpose)

The SOPs, business files, and Ace Hardware campaign cards on the
landing page link out to the existing Google Drive files rather than
duplicating that content here — some of it (contact info, etc.) is
private, and copying it into files tracked by git means it never
really goes away, even if deleted later. Google Drive's own sharing
permissions are what actually control who can open those files — that
stays true no matter who can see this repo or this page.

## About visibility

This repo is public (needed for free GitHub Pages hosting). That means
anyone with the exact link can view the page — there's no login screen.
Nothing sensitive lives in these files, and the linked Drive files stay
protected by Google's own permissions regardless. If real shared/editable
business data (a CRM, etc.) ever gets added here, that's the point to
revisit whether a plain public page is still the right setup.

## Never touches Shopify

Nothing in this repo reads from or writes to the Shopify store. The
latitude/longitude tool only talks to OpenStreetMap. Adding a store to
the actual site is still a manual step in the Shopify theme editor,
same as always — this just makes one part of that process (looking up
coordinates) faster.
