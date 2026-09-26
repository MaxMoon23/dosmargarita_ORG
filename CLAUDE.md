# Rules for Claude in this repository

This repo is Dos Margaritas Salsa job work, owned by Michael and Maggie,
deliberately kept separate from Michael's personal coding repo. Follow
these rules in every session:

## Durability comes first
This site must keep working even if Claude/Anthropic access ever
changes. That's why it's a plain static site (HTML/CSS/JS only) instead
of a Claude Artifact — no server, no login, no dependency on any AI
service staying online. Don't introduce a build step, a framework, or
any dependency that isn't either (a) already in this repo, or (b) a
free CDN/API call with automatic fallback if it's unreachable (like the
Google Font and the OpenStreetMap lookup already in use).

## Never touch Shopify
Nothing in this repo may read from or write to the Shopify store, and
never use Michael's or Maggie's actual login/password for anything.
The latitude/longitude tool only calls OpenStreetMap. If real Shopify
API access is ever added, it must be a scoped, revocable API token that
Maggie creates and approves herself — never assume it, never build
toward it without being asked.

## Adding a store is still manual, on purpose
Maggie asked to add stores to the Shopify map by hand for now and
revisit automation later. Don't build anything that writes to Shopify
or auto-adds stores without being explicitly asked to.

## This repo is public
Needed for free GitHub Pages hosting. That means anyone with the exact
link can view the page — there's no login screen, and nothing here
should assume privacy beyond "not indexed/promoted anywhere." Never
commit real business secrets, personal contact info, or anything from
the private Drive folder into this repo — link out to Drive instead
(Google's own sharing permissions are the real access control for that
content, independent of whatever happens to this repo/site).

## Design direction
Landing page (`index.html`) is an interactive 8-bit/pixel-art scene (a
factory with clickable "doors" for navigation), not a plain business
page — that was a deliberate choice, not a placeholder. Keep new
sections in that visual language unless told otherwise. `employee-tools.html`
can be restyled to match if asked, but hasn't been yet.

## What's still a placeholder
The ACE Hardware Campaign and CRM sections are not built — CRM
especially needs its own conversation about where shared/editable data
should live before building it for real.
