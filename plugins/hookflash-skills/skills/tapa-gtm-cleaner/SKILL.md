---
name: tapa-gtm-cleaner
description: Clean a GTM container with Tapa's GTM Cleaner via the Tether MCP — strips Universal Analytics tags and orphaned triggers/variables from a container export and returns the cleaned .json with removed/kept counts. Use when the user runs /tapa-gtm-cleaner, wants UA tags or unused triggers/variables removed from GTM, or asks to clean/tidy a GTM container export.
---

# Tapa GTM Cleaner

Turn a GTM container export into a **cleaned container `.json`**: Universal Analytics tags
removed, then every trigger and variable that nothing references any more. The deliverable is
the file plus the removed/kept counts — this tool has no chart visualisation.

## Prerequisites (read first)

- **Use your Tether MCP connector.** The `tapa_gc_*` tools are limited to a small allow-list of
  test users while Tapa skills are in testing.
  - If NO Tether tools are available at all, the Tether connector isn't connected or enabled for
    this session — tell the user to reconnect/enable it, then retry.
  - If other Tether tools are available but the `tapa_gc_*` tools are missing, the user is not on
    the allow-list: explain that Tapa skills are still in testing and access is limited to a small
    test group for now — Connor Jennings (AI Ops) can add them.
- **If a `tapa_gc_*` call fails with an authentication or authorisation error from Tapa**, the
  user hasn't authenticated the Tapa app yet: direct them to https://tapa.hookflash.co.uk/connect
  and explain they need to sign in there to authenticate the app, then retry.
- Tools under the Tether MCP: `tapa_gc_options`, `tapa_gc_upload`, `tapa_gc_run`.
- **Works in normal claude.ai chat.** The only surface difference is how the file travels
  (step 1). This tool is synchronous — no polling.

## Step 1 — The container export (REQUIRED — ask if missing; never guess)

One input: a **GTM container export** → `container_file_url`. **Only `.json` is accepted** —
decline other types. If the user doesn't have the export: Google Tag Manager → **Admin →
Export Container** → download the `.json`.

**How to stage it** — call `tapa_gc_upload` with the filename:
- A `.json` whose text you can read → pass the full contents as `content_text` (no trimming).
- A local file in Claude Code / Cowork → omit `content_text`, PUT the raw bytes to the
  returned `upload_url` exactly as `how_to_upload` says.
- Either way, pass the returned `file_url` as `container_file_url`.

## Step 2 — Run (synchronous)

Call `tapa_gc_run` with `container_file_url`. The result comes back in the same call: a
**`download_url`** (the cleaned container `.json`) and a **`summary`** with
`tags_removed / triggers_removed / variables_removed` and the kept counts.

## Step 3 — Report the outcome

No charts for this tool — report the summary as a short, clear stat line (e.g. "Removed 4 UA
tags, 6 orphaned triggers and 11 unused variables; 58 tags / 41 triggers / 72 variables
kept"), using **only the counts from `summary`**.

Put the `download_url` as a **plain clickable link in your reply** and mention it expires.
Tell the user the file is ready to import back into GTM (Admin → Import Container) — and to
review in a workspace with Preview before publishing.

## Guardrails

- Never fabricate counts; report exactly what `summary` says.
- Recommend importing into a new GTM workspace and reviewing before publish — the cleaner is
  conservative, but tag setups vary.
- If the user wants to know *what's in* the container rather than clean it, point them at
  `/tapa-gtm-documentation` instead.
