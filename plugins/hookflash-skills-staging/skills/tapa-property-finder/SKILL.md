---
name: tapa-property-finder
description: Identify a GA4 property from an ID with Tapa's GA4 Property Finder via the Tether MCP — resolves a numeric Property ID or a G-/AW- Measurement ID to its Account → Property (→ Data Stream) chain with a direct GA4 link. Use when the user runs /tapa-property-finder, pastes a GA4/measurement ID asking whose it is or where it lives, or asks which account a property belongs to.
---

# Tapa GA4 Property Finder

Resolve a GA4 **Property ID** (numeric) or **Measurement ID** (`G-…` / `AW-…`) to the
account, property and data stream it belongs to, plus a direct GA4 deep link. A quick
lookup — no file, no charts, no polling.

## Prerequisites (read first)

- **Use your Tether MCP connector.** The `tapa_pf_*` tools are limited to a small allow-list of
  test users while Tapa skills are in testing.
  - If NO Tether tools are available at all, the Tether connector isn't connected or enabled for
    this session — tell the user to reconnect/enable it, then retry.
  - If other Tether tools are available but the `tapa_pf_*` tools are missing, the user is not on
    the allow-list: explain that Tapa skills are still in testing and access is limited to a small
    test group for now — Connor Jennings (AI Ops) can add them.
- **If a `tapa_pf_*` call fails with an authentication or authorisation error from Tapa**, the
  user hasn't authenticated the Tapa app yet: direct them to https://tapa.hookflash.co.uk/connect
  and explain they need to sign in there to authenticate the app, then retry.
- Tool under the Tether MCP: `tapa_pf_find`.
- **Works in normal claude.ai chat.** The lookup runs as **your own GA4 access** — it can only
  find properties your Google account can see.

## Step 1 — The ID (REQUIRED — ask if missing; never guess)

One critical input: `ga4_property_id` — either a **numeric property ID** (e.g. `123456789`)
or a **measurement ID** (`G-XXXXXXX` / `AW-XXXXXXX`). If the user gave neither, ask for it.

Optional: `ga4_account_id` — only useful for measurement-ID lookups, to search one account
instead of all accessible accounts. Don't ask for it; use it only if the user offered it (or
if an all-accounts search came back slow/empty and they know the account).

## Step 2 — Look it up and report

Call `tapa_pf_find`. Report the returned `result_text` chain verbatim (Account → Property →
Stream) and include `ga4_link` as a clickable link ("Open in GA4"). No visualisation needed.

If the tool returns an error (not found / no access), relay it plainly — the usual causes are
a typo'd ID or a property the user's Google account can't see. Suggest checking the ID, or
connecting the right Google account in Tapa.

## Guardrails

- Never guess which property an ID belongs to — the answer comes from the tool only.
- A "not found" is a real answer: say the ID wasn't visible to their access, don't speculate.
