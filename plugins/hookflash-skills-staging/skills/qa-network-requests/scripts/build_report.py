#!/usr/bin/env python3
"""Build the qa-network-requests .xlsx report (two sheets).

Usage:  python build_report.py events.json consent.json <screenshots_dir> <out.xlsx>

consent.json may be the literal string "none" if there was nothing to report, but
prefer a one-row file saying consent was already granted, so the reader knows the
check ran.

Keep <out.xlsx> SHORT and generic (e.g. CB_NQA.xlsx). The session output directory is
already ~200 chars; a long filename breaks the Windows 259-char path limit and the
workbook will not open. Put the descriptive title inside the workbook, not in the name.

events.json = list of objects, one per HIT, in funnel order:
{
  "event": "add_to_cart",                  # the name the SPEC uses
  "vendor": "GA4",                         # GA4 | Meta | TikTok | Google Ads | ...
  "sent": true,                            # false -> "No request observed" in the request cell
  "method": "POST",
  "endpoint": "metrics.example.com/g/collect",   # host + path only, keeps the column readable
  "url": "https://metrics.example.com/g/collect?v=2&tid=G-XXX&en=add_to_cart...",  # VERBATIM
  "body": "en=add_to_cart&epn.value=29.99",      # verbatim body, or null
  "payload": { "en": "add_to_cart", "epn.value": 29.99, "items": [ ... ] },
  "count": 2,                              # optional; rendered only when > 1 (duplicate tagging)
  "conditions": "Clicked 'Add to basket' on the PDP.",
  "location_image": "atc_button.png",      # filename inside screenshots_dir
  "verdict": "fail",                       # pass | fail | warn | na
  "notes": ["- Matches spec on event name", "- epn.value is the cart total"]
}

consent.json = list of objects, one per vendor, optionally preceded by {"state": ...}:
{
  "vendor": "Meta",
  "before": "No hits observed",
  "signal": "n/a (no consent parameter)",
  "after": "1 hit (PageView)",
  "observation": "No Meta requests were observed before consent was granted.",
  "location_image": "banner.png"           # optional
}

Design rules baked in here:
- "url", "body" and "payload" are rendered VERBATIM (payload via json.dumps(indent=2)).
  Never pre-format or tidy them.
- The Consent sheet has NO pass/fail column, deliberately. Consent behaviour is
  reported, not graded. Do not add one.
- Em/en dashes are stripped from prose cells (never from URLs, bodies or payloads).
- Images are auto-fit to the screenshot column so they never overhang, and each row
  is sized to its image.
"""
import json, os, sys
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.drawing.image import Image as XLImage
try:
    from PIL import Image as PILImage
    HAVE_PIL = True
except Exception:
    HAVE_PIL = False

DASHES = {"—": "-", "–": "-", "‒": "-", "―": "-", "−": "-"}


def nodash(s):
    if not isinstance(s, str):
        s = str(s)
    for k, v in DASHES.items():
        s = s.replace(k, v)
    return s


FONT, MONO = "Arial", "Consolas"
HDR = PatternFill("solid", fgColor="1F2A44")
FILLS = {"pass": PatternFill("solid", fgColor="D6EAD6"),
         "fail": PatternFill("solid", fgColor="F7D6D6"),
         "warn": PatternFill("solid", fgColor="FCEFC7"),
         "na":   PatternFill("solid", fgColor="E6E6E6")}
# One colour per vendor so a reader can scan by vendor down the sheet.
VENDOR_FILLS = {"ga4": "DCE7F5", "meta": "D9E3F7", "facebook": "D9E3F7",
                "tiktok": "EADCF5", "google ads": "FBE3D6", "floodlight": "FBE3D6",
                "microsoft uet": "DCF0EE", "pinterest": "F7D9DE",
                "linkedin": "D9E9F7", "snapchat": "FCF4C7", "segment": "E4EEDC"}
THIN = Side(style="thin", color="BBBBBB")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
TOP = Alignment(horizontal="left", vertical="top", wrap_text=True)
IMG_W = 350


LINE_PT = 1.35          # Excel line height as a multiple of font size
IMG_PAD_PT = 14


def cell_height(text, col_width, font_size):
    """Points needed to show `text` wrapped in a column of col_width at font_size.

    Counting "\\n" alone under-counts badly here: a single verbatim hit URL is one
    logical line but wraps to five, and a row sized off the newline count clips it.
    Excel's width unit is ~1 char of the default 11pt font, so scale by font size.
    Derive the line height from the font size too, rather than hardcoding a number
    per column, so the two cannot drift apart (a hardcoded 12 against a 9pt font
    left the closing brace of a long payload sitting under the row border).
    """
    if not text:
        return LINE_PT * font_size
    chars = max(8, int(col_width * 11.0 / max(font_size, 1)))
    n = 0
    for line in str(text).split("\n"):
        n += max(1, -(-len(line) // chars))     # ceil division
    return n * font_size * LINE_PT


def row_height(cells, img_px=0, floor=0):
    """Tallest of the wrapped cells and the image, with a floor. cells = (text, width, font)."""
    need = [cell_height(t, w, f) for t, w, f in cells]
    need.append(img_px * 0.75 + IMG_PAD_PT)     # px -> pt, so the row fits the image
    need.append(floor)
    return max(need)


def header(ws, headers, widths, height=28):
    for k, v in widths.items():
        ws.column_dimensions[k].width = v
    for c, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=c, value=h)
        cell.font = Font(name=FONT, size=11, bold=True, color="FFFFFF")
        cell.fill = HDR
        cell.border = BORDER
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[1].height = height


def place_image(ws, row, col_letter, shots_dir, img_file):
    """Add an image scaled to the column. Returns its height in px (0 if none)."""
    if not img_file or str(img_file).strip().lower() in ("none", "null", ""):
        return 0
    path = os.path.join(shots_dir, img_file)
    if not (os.path.exists(path) and HAVE_PIL):
        return 0
    with PILImage.open(path) as im:
        w0, h0 = im.size
    img = XLImage(path)
    img.width = IMG_W
    img.height = int(IMG_W * h0 / w0)
    ws.add_image(img, "%s%d" % (col_letter, row))
    return img.height


def request_cell(ev):
    """method + endpoint + the verbatim URL and body. Verbatim, never trimmed."""
    if not ev.get("sent", True):
        return "No request observed"
    parts = ["%s %s" % (ev.get("method", "GET"), ev.get("endpoint", ""))]
    if ev.get("count") and int(ev["count"]) > 1:
        parts.append("fired %d times for this one interaction" % int(ev["count"]))
    if ev.get("url"):
        parts += ["", "URL:", ev["url"]]
    if ev.get("body"):
        parts += ["", "Body:", ev["body"]]
    return "\n".join(parts)


def network_sheet(wb, events, shots_dir):
    ws = wb.active
    ws.title = "Network QA"
    header(ws, ["Event name", "Vendor", "Conditions tested",
                "Request (verbatim)", "Decoded payload",
                "Location screenshot", "Pass / Fail"],
           {"A": 20, "B": 15, "C": 30, "D": 48, "E": 50, "F": 54, "G": 44})

    r = 2
    for ev in events:
        payload = ev.get("payload", None)
        if payload is not None:
            pj = json.dumps(payload, indent=2, ensure_ascii=False)   # verbatim
        else:
            pj = nodash(ev.get("payload_note", "(no payload captured)"))
        req = request_cell(ev)
        notes = ev.get("notes", [])
        # blank line between bullets so findings stay visually separated
        notes_txt = nodash("\n\n".join(notes) if isinstance(notes, list) else str(notes))
        vendor = ev.get("vendor", "")

        ws.cell(row=r, column=1, value=nodash(ev.get("event", ""))).font = Font(name=FONT, size=11, bold=True)
        ws.cell(row=r, column=2, value=nodash(vendor)).font = Font(name=FONT, size=10, bold=True)
        ws.cell(row=r, column=3, value=nodash(ev.get("conditions", ""))).font = Font(name=FONT, size=10)
        ws.cell(row=r, column=4, value=req).font = Font(name=MONO, size=8)
        ws.cell(row=r, column=5, value=pj).font = Font(name=MONO, size=9)
        ws.cell(row=r, column=7, value=notes_txt).font = Font(name=FONT, size=10)
        for c in range(1, 8):
            cc = ws.cell(row=r, column=c)
            cc.alignment = TOP
            cc.border = BORDER

        vfill = FILLS.get(ev.get("verdict", "warn"))
        ws.cell(row=r, column=1).fill = vfill
        ws.cell(row=r, column=7).fill = vfill
        vf = VENDOR_FILLS.get(vendor.strip().lower())
        if vf:
            ws.cell(row=r, column=2).fill = PatternFill("solid", fgColor=vf)

        img_h = place_image(ws, r, "F", shots_dir, ev.get("location_image"))
        # Size to the tallest column once WRAPPING is accounted for, not to "\n" count.
        ws.row_dimensions[r].height = row_height(
            [(req, 48, 8), (pj, 50, 9), (notes_txt, 44, 10),
             (nodash(ev.get("conditions", "")), 30, 10)],
            img_px=img_h, floor=120)
        r += 1
    return r - 2


def consent_sheet(wb, consent, shots_dir):
    """Descriptive only. There is deliberately NO pass/fail column here."""
    ws = wb.create_sheet("Consent")
    header(ws, ["Vendor", "Before consent", "Consent signal", "After consent",
                "Observation (not a verdict)", "Screenshot"],
           {"A": 16, "B": 26, "C": 34, "D": 26, "E": 52, "F": 54})

    rows = [c for c in consent if "vendor" in c]
    state = next((c.get("state") for c in consent if c.get("state")), None)

    r = 2
    if state:
        note = ("Consent was already accepted when the session started, so pre-consent "
                "behaviour was not observed. Re-run in a clean browser profile to see it."
                if state == "already_accepted" else
                "Consent had not been given when the session started, so the rows below "
                "compare behaviour before and after granting it.")
        cell = ws.cell(row=r, column=1, value=nodash(note))
        cell.font = Font(name=FONT, size=10, italic=True)
        cell.alignment = TOP
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
        # merged across all six columns, so measure against their combined width
        ws.row_dimensions[r].height = row_height([(nodash(note), 16 + 26 + 34 + 26 + 52 + 54, 10)],
                                                 floor=30)
        r += 1

    for c in rows:
        vals = [c.get("vendor", ""), c.get("before", ""), c.get("signal", ""),
                c.get("after", ""), c.get("observation", "")]
        for i, v in enumerate(vals, 1):
            cell = ws.cell(row=r, column=i, value=nodash(v))
            cell.font = Font(name=FONT, size=10, bold=(i == 1))
        for i in range(1, 7):
            cc = ws.cell(row=r, column=i)
            cc.alignment = TOP
            cc.border = BORDER
        vf = VENDOR_FILLS.get(str(c.get("vendor", "")).strip().lower())
        if vf:
            ws.cell(row=r, column=1).fill = PatternFill("solid", fgColor=vf)

        img_h = place_image(ws, r, "F", shots_dir, c.get("location_image"))
        widths = [16, 26, 34, 26, 52]
        ws.row_dimensions[r].height = row_height(
            [(nodash(v), w, 10) for v, w in zip(vals, widths)],
            img_px=img_h, floor=60)
        r += 1
    return len(rows)


def main():
    if len(sys.argv) < 5:
        print(__doc__)
        sys.exit(1)
    events_path, consent_path, shots_dir, out_path = sys.argv[1:5]
    with open(events_path, encoding="utf-8") as f:
        events = json.load(f)
    consent = []
    if consent_path.lower() not in ("none", "-", ""):
        with open(consent_path, encoding="utf-8") as f:
            consent = json.load(f)

    wb = openpyxl.Workbook()
    n_events = network_sheet(wb, events, shots_dir)
    n_consent = consent_sheet(wb, consent, shots_dir)
    wb.save(out_path)

    if len(os.path.abspath(out_path)) >= 259:
        print("WARNING: output path is >= 259 chars, Windows Excel may refuse to open it. "
              "Use a shorter filename.")
    print("saved %s | Network QA rows %d | Consent rows %d" % (out_path, n_events, n_consent))


if __name__ == "__main__":
    main()
