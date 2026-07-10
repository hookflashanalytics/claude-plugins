---
name: tapa-content-eeater
description: Audit a blog post end-to-end with Tapa's Content EEATer via the Tether MCP — E-E-A-T content analysis plus optional site-duplication and keyword-cannibalisation checks, visualised in chat with a download link to the results workbook. Use when the user runs /tapa-content-eeater, shares a blog link or document and asks for a content/EEAT audit, or asks to check content for E-E-A-T quality, duplication, or cannibalisation.
---

# Run Content EEATer

Turn a blog post into (1) the Tapa Content EEATer results workbook and (2) an in-chat
visualisation of the audit — E-E-A-T scores, duplication findings, cannibalisation findings.

## Prerequisites (read first)

- **Use your Tether MCP connector, signed in as an allow-listed user.** The `tapa_ce_*` tools are
  gated to allow-listed users during rollout — if you don't see them, reconnect and confirm you're
  on the allow-list.
- Tools under the Tether MCP: `tapa_ce_options`, `tapa_ce_upload`, `tapa_ce_run`, `tapa_ce_result`.
- **Works in normal claude.ai chat.** The only surface difference is how an uploaded blog document
  travels (see step 1): in chat you extract the text yourself; in Claude Code / Cowork you can
  stage the raw file with `tapa_ce_upload`.

## Step 1 — The blog (REQUIRED — ask if missing; never guess)

The audit needs exactly one blog input. If the user gave none, **ask**: "Which blog should I
audit? Share a live link, or upload the draft as a Word doc / PDF."

- **Live link** → pass it as `blog_url`.
- **Uploaded Word doc / PDF, in claude.ai chat** → read the document yourself and pass the full
  text as `blog_text`. Preserve the structure as markdown (headings as `#`/`##`, lists as lists) —
  the analysis uses the document's shape, not just its words. Do not summarise or trim.
- **Local file, in Claude Code / Cowork** → call `tapa_ce_upload` with the filename (no
  `content_text`), PUT the raw file bytes to the returned `upload_url` exactly as its
  `how_to_upload` says, then pass the returned `file_url` as `blog_file_url`. This preserves the
  original document byte-for-byte.

Pass exactly ONE of `blog_url` / `blog_text` / `blog_file_url`.

## Step 2 — Duplication check (OPTIONAL — offer it if not specified)

If the user didn't mention duplication, **ask once**: "Want me to run a duplication check against
the rest of the site? I can either crawl a domain, or use a Screaming Frog export if you have one
— or skip it." Don't push if they decline.

- **Domain crawl** → needs `duplication_domain` AND `crawl_size`. If the user gave a domain but no
  size, call `tapa_ce_options` and offer them **exactly the crawl-size choices it returns** (never
  invent sizes). Then pass both.
- **Screaming Frog export** → stage it with `tapa_ce_upload`: for a file you can read as text
  (CSV), pass its full contents as `content_text`; for a local file in Claude Code / Cowork,
  use the PUT pathway. Pass the returned `file_url` as `duplication_file_url`.
- **Skip** → omit all duplication inputs.

Never set both `duplication_domain` and `duplication_file_url`.

## Step 3 — Cannibalisation check (do NOT ask about this)

Tapa handles cannibalisation automatically using the user's connected Search Console accounts,
and silently skips it when none are available. A manual query×page export is rare (Search Console
doesn't export that shape directly), so **only** set `cannibalisation_file_url` if the user
proactively supplied such an export — stage it via `tapa_ce_upload` like the Screaming Frog file.
Otherwise omit it and say nothing.

## Step 4 — Run and poll

Call `tapa_ce_run` with the gathered inputs. It submits the job and polls briefly:

- If it returns the finished output, continue to step 5.
- If it returns `answer_status: "pending"` with a `job_id`, the run is still going — crawls can
  take several minutes. Tell the user it's running, then poll `tapa_ce_result` with the `job_id`
  until it finishes. Don't abandon a pending job or start a duplicate run.

The finished output is text JSON with a **`results`** object (the audit data, mirroring Tapa's
on-screen panels) and a **`download_url`** (the results workbook).

## Step 5 — Visualise in chat — ALWAYS (do not substitute plain text)

**You must render a visual, not a text summary**, mirroring the panels Tapa's own UI shows.

**How to render it:** if an interactive-widget tool is available (e.g. `show_widget` from a
visualize connector — call its `read_me` first), render through **that**. Only if no widget tool is
available, fall back to a native HTML artifact. Either way the markup is **self-contained**: inline
CSS + inline SVG only, **no external resources** (CDN scripts / chart libs / web fonts get blocked
and the artifact collapses to raw HTML). Keep JS minimal; render charts as static inline SVG/CSS.

Content — one section per section present in `results` (render what's there; skip what isn't):
- **E-E-A-T scores** — the overall and per-category scores/verdicts as a scored breakdown (bars or
  a table with score chips), using the labels and scales from `results` verbatim.
- **Duplication findings** — the matched/similar pages and their similarity figures, worst first.
- **Cannibalisation findings** — the flagged query/page overlaps. If `results` marks the check as
  skipped or unavailable, show that as a quiet note, not an empty chart.
- Header line: blog title/URL · checks run · date.

**Sheet download → a plain text link in the chat message, NOT a widget button.** Widgets run in a
sandboxed iframe that blocks downloads, so put the workbook `download_url` as a normal clickable
link in your reply alongside the visual (it always works, but expires — mention that).

**Avoid these failures (all seen in testing with the sibling results-analysis skill):**
- **Never render with a placeholder URL or placeholder numbers.** Render once, with the real
  values from `results`.
- **Charts must be real data charts** built from the numbers — never decorative shapes or a
  generated image standing in for the data.
- **Never fabricate findings.** Every score, match, and verdict comes from `results`. If a check
  didn't run, say so.

## Visualisation style (Hookflash house standard)

Use these exact values for **every** chart, bar, KPI card and table you render in the
step above, so all Tapa reports look consistent. Keep visuals self-contained — inline
CSS + inline SVG only, no external resources (CDN scripts / chart libs / web fonts are
blocked and the visual collapses to raw HTML).

- **Font:** system sans-serif (`-apple-system, Segoe UI, Roboto, Arial, sans-serif`).
- **Card:** white `#FFFFFF` background, text `#111827`, muted labels `#6B7280`, hairline borders `#E5E7EB`.
- **Bars:** empty track `#F3F4F6`, 2px rounded corners, one consistent bar height, value label at the bar's end.
- **Categorical series (assign in this order):** blue `#2F6BED`, green `#22C55E`, purple `#8B5CF6`, orange `#F97316`, teal `#14B8A6`.
- **Status / bands:** good/pass green `#16A34A`, warning/borderline amber `#F59E0B`, poor/critical red `#DC2626`, neutral/none grey `#9CA3AF`.
- **Deltas (vs a baseline / previous period):** positive green `#16A34A`, negative red `#DC2626`, flat grey `#6B7280`.
- **Single-measure magnitude / score:** one blue ramp light→dark — never a rainbow.
- Pair colour with a text label or icon (never colour alone); sentence case; round every displayed number.

In this skill: E-E-A-T pillar scores → status bands (good green / borderline amber / weak red); duplication & cannibalisation risk → red/amber/grey.
