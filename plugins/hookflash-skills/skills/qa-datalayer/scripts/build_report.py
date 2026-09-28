#!/usr/bin/env python3
"""Build the qa-datalayer report: the team's dataLayer QA checklist, filled in.

Usage:  python build_report.py events.json <screenshots_dir> <out.xlsx>

Keep <out.xlsx> SHORT and generic (e.g. dl_qa.xlsx). The session output directory is
already ~200 chars; a long filename breaks the Windows 259-char path limit and the
workbook will not open. Put the client inside the workbook, not in the name.

The workbook is the QA checklist layout (qa_checklist.py, the same builder Tapa's
DataLayer Doc Creator exports with): a Summary tab, a QA Checklist tab with one block
per event tested and a row per expected parameter, and a third tab, Captured pushes,
holding each push verbatim with a screenshot of what triggered it.

events.json:
{
  "client": "Example Store", "batch": "Batch 2",        # batch optional
  "source": "Example Store DataLayer Guide",            # where the expected params came from
  "site": "example-store.test", "tested": "2026-09-28",
  "events": [                                           # one per event TESTED, funnel order
    {
      "category": "Ecom",                               # Ecom | Non-Ecom | Recurring
      "event": "add_to_cart", "variant": "Mini-bag",    # variant: which trigger, "" if one
      "trigger": "Clicked + on the mini-bag line (qty 1 to 2).",   # what you did
      "note": "value is the cart total, not the item added",       # findings, fragments
      "source": "Top frame",                            # Top frame | Web pixel | Not fired
      "push": { ... captured object, verbatim ... },    # or null (then push_note)
      "push_note": "Fires at page load, before any hook.",
      "name_seen": "add_to_cart",                       # only when the event name rides
                                                        # beside the payload (gtag, utag,
                                                        # Shopify.analytics.publish)
      "location_image": "atc_minibag.png",              # file in screenshots_dir, ideally a
                                                        # tight zoom crop; location_bbox
                                                        # [x,y,w,h] + viewport_w crops a
                                                        # full shot as a fallback
      "params": [                                       # the spec's params for this event
        {"name": "event", "type": "String", "required": "Yes", "expected": "add_to_cart"},
        {"name": "value", "type": "Number", "required": "Yes", "expected": "129.99",
         "value_ok": "Fail", "notes": "cart total, not the item added"}
      ]
    }
  ]
}

What this script decides, so you do not have to (you can still override any of it by
giving present / value_ok yourself):
- Present / fired?  Pass when the key is in the push: top level, under ecommerce, or on
  EVERY entry of items[] (Fail, with a note, when some items lack it). Missing: Fail if
  Required is Yes, N/A otherwise. Event "Not fired": every row Fail.
- Value correct?  Fail when the value's JSON type contradicts the Type column. Pass when
  it equals the expected value exactly. N/A when the key is absent. Everything else is
  left for you to judge, and listed at the end of the run until you do.
- Notes: "Seen: <value>" from the push whenever it differs from the expected value, then
  your note.

Rules baked in: the push is dumped VERBATIM (json.dumps indent=2); em/en dashes are
stripped from prose you wrote (never from values or the push); images are fitted to the
screenshot column.
"""
import json
import os
import sys

from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Border, Font, Side
from openpyxl.worksheet.hyperlink import Hyperlink

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qa_checklist as Q  # noqa: E402

try:
    from PIL import Image as PILImage
    HAVE_PIL = True
except Exception:
    HAVE_PIL = False

DASHES = {"—": "-", "–": "-", "‒": "-", "―": "-", "−": "-"}
UNREADABLE = "(can't read values in web pixel)"
PUSHES_SHEET = "Captured pushes"
PUSH_WIDTHS = {"A": 5, "B": 24, "C": 12, "D": 34, "E": 62, "F": 54}
IMG_W = 350                        # px, narrower than column F
MAX_ROW_PT = 409                   # Excel's ceiling for a row height
NOTE_BUDGET, EVENT_NOTE_BUDGET = 90, 220


def nodash(s):
    if s is None:
        return None
    s = str(s)
    for k, v in DASHES.items():
        s = s.replace(k, v)
    return s


# ------------------------------------------------------------------ reading a push
def _find_items(obj, depth=0):
    """The first items[] list of dicts in the push (ecommerce.items, items, ...)."""
    if depth > 4 or not isinstance(obj, dict):
        return None
    for key in ("items", "products"):
        v = obj.get(key)
        if isinstance(v, list) and v and all(isinstance(x, dict) for x in v):
            return v
    for v in obj.values():
        if isinstance(v, dict):
            found = _find_items(v, depth + 1)
            if found is not None:
                return found
    return None


def _find_key(obj, key, depth=0):
    """(True, value) for the shallowest dict holding `key`, not looking inside
    lists; (False, None) when it is nowhere."""
    if depth > 4 or not isinstance(obj, dict):
        return False, None
    if key in obj:
        return True, obj[key]
    for v in obj.values():
        if isinstance(v, dict):
            hit = _find_key(v, key, depth + 1)
            if hit[0]:
                return hit
    return False, None


def lookup(push, key):
    """Where `key` sits in the push: {"values": [...], "items": n, "missing": k}.
    values is empty when the key is absent. An item-level key is looked up on
    every entry of items[]; missing counts the entries without it."""
    found, value = _find_key(push, key)
    if found:
        return {"values": [value], "items": 0, "missing": 0}
    items = _find_items(push) or []
    values = [it[key] for it in items if key in it]
    return {"values": values, "items": len(items), "missing": len(items) - len(values) if values else 0}


def _type_ok(value, declared):
    t = (declared or "").strip().lower()
    if value is None or t not in ("string", "number", "double", "float", "integer", "int",
                                  "boolean", "array", "object"):
        return True                 # null, or a type we do not police: yours to judge
    if t == "string":
        return isinstance(value, str)
    if t == "boolean":
        return isinstance(value, bool)
    if t == "array":
        return isinstance(value, list)
    if t == "object":
        return isinstance(value, dict)
    if isinstance(value, bool):
        return False
    if t in ("integer", "int"):
        return isinstance(value, int)
    return isinstance(value, (int, float))


def _json_type(value):
    return {bool: "boolean", int: "number", float: "number", str: "string",
            list: "array", dict: "object"}.get(type(value), "null")


def _same(value, expected):
    if expected is None or str(expected) == "":
        return False
    if isinstance(value, bool):
        return str(expected).strip().lower() == ("true" if value else "false")
    if isinstance(value, (int, float)):
        try:
            return float(expected) == float(value)
        except ValueError:
            return False
    return isinstance(value, str) and value == str(expected)


def _show(value):
    if isinstance(value, str):
        v = value if len(value) <= 70 else value[:67] + "..."
        return "'" + v + "'"
    if isinstance(value, list):
        return f"[{len(value)} entries]"
    if isinstance(value, dict):
        return "{object}"
    return json.dumps(value)


def _joined(*parts):
    return "; ".join(x for x in parts if x)


def judge(ev):
    """Fill the checks the push answers by itself. Returns the params, and the
    names whose Value correct? is still yours to decide."""
    source = (ev.get("source") or "").strip().lower()
    push = ev.get("push")
    if isinstance(push, list) and len(push) == 1 and isinstance(push[0], dict):
        push = push[0]                 # a builder's single argument
    out, open_values = [], []
    for raw in ev["params"]:
        p = Q.norm_param(raw)
        mine = nodash(p["notes"]) if p["notes"] else ""
        seen = ""
        if source == "not fired":
            p["present"] = p["present"] or "Fail"
            p["value_ok"] = p["value_ok"] or "N/A"
        elif isinstance(push, dict):
            hit = lookup(push, p["name"])
            if p["name"] == "event" and not hit["values"] and ev.get("name_seen"):
                # gtag / Tealium / a pub-sub bus carry the event name beside
                # the payload, not in it.
                hit = {"values": [ev["name_seen"]], "items": 0, "missing": 0}
            values = hit["values"]
            if not p["present"]:
                if not values:
                    p["present"] = "Fail" if p["required"] == "Yes" else "N/A"
                elif hit["missing"]:
                    p["present"] = "Fail"
                    mine = _joined(f"missing on {hit['missing']} of {hit['items']} items", mine)
                else:
                    p["present"] = "Pass"
            unreadable = any(isinstance(v, str) and v.strip().lower() == UNREADABLE for v in values)
            if values and not unreadable and not all(_same(v, p["expected"]) for v in values):
                seen = "Seen: " + _show(values[0])
                if hit["items"] > 1:
                    seen += f" (item 1 of {hit['items']})"
            if not p["value_ok"]:
                wrong = [v for v in values if not _type_ok(v, p["type"])]
                if not values:
                    p["value_ok"] = "N/A"
                elif unreadable:
                    mine = mine or "value unreadable in the web pixel sandbox"
                elif wrong:
                    p["value_ok"] = "Fail"
                    seen = ""
                    mine = _joined(f"sent as {_json_type(wrong[0])} {_show(wrong[0])}, spec says {p['type']}",
                                   mine)
                elif all(_same(v, p["expected"]) for v in values):
                    p["value_ok"] = "Pass"
            if p["present"] == "Pass" and not p["value_ok"] and not unreadable:
                open_values.append(p["name"])
        p["notes"] = _joined(seen, mine) or None
        out.append(p)
    return out, open_values


# ------------------------------------------------------------------ the evidence tab
def build_pushes(wb, events, blocks, shots_dir):
    thin = Side(style="thin", color=Q.LINE)
    box = Border(left=thin, right=thin, top=thin, bottom=thin)
    top = Alignment(horizontal="left", vertical="top", wrap_text=True)
    ws = wb.create_sheet(PUSHES_SHEET)
    for k, v in PUSH_WIDTHS.items():
        ws.column_dimensions[k].width = v
    headers = ["#", "Event", "Source", "Conditions tested", "dataLayer push (verbatim JSON)",
               "Location screenshot"]
    for c, h in enumerate(headers, 1):
        cell = ws.cell(1, c, h)
        cell.font = Font(name=Q.F, sz=10, bold=True, color=Q.WHITE)
        cell.fill = Q.fill(Q.SLATE)
        cell.border = box
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[1].height = 24
    rows = {}
    for i, (ev, (_scell, header, _first, _last)) in enumerate(zip(events, blocks), 1):
        r = i + 1
        rows[i] = r
        push = ev.get("push")
        js = (json.dumps(push, indent=2, ensure_ascii=False) if push is not None
              else nodash(ev.get("push_note") or "(no push captured)"))
        variant = (ev.get("variant") or "").strip()
        label = ev["event"] + (f" · {variant}" if variant else "")
        vals = [i, label, nodash(ev.get("source") or ""), nodash(ev.get("trigger") or ""), js, None]
        for c, v in enumerate(vals, 1):
            cell = Q.put(ws, r, c, v)
            cell.alignment = top
            cell.border = box
            cell.font = Font(name="Consolas" if c == 5 else Q.F, sz=9 if c == 5 else 10, bold=c in (1, 2))
        link = ws.cell(r, 1)
        link.hyperlink = Hyperlink(ref=link.coordinate, location=f"'{Q.CHECK_SHEET}'!A{header}")
        link.font = Font(name=Q.F, sz=10, bold=True, color=Q.SLATE, underline="single")

        img_h = 0
        name = ev.get("location_image")
        path = os.path.join(shots_dir, name) if name else None
        if path and os.path.exists(path) and HAVE_PIL:
            if ev.get("location_bbox"):
                # Fallback for a full screenshot: crop to the element's box,
                # [x, y, w, h] in a viewport `viewport_w` wide. A tight zoom
                # crop needs none of this.
                x, y, w, h = ev["location_bbox"]
                try:
                    with PILImage.open(path) as im:
                        sx = im.width / ev.get("viewport_w", im.width)
                        crop = im.crop((int(x * sx), int(y * sx), int((x + w) * sx), int((y + h) * sx)))
                        crop.save(path + ".crop.png")
                    path = path + ".crop.png"
                except Exception:
                    pass
            with PILImage.open(path) as im:
                w0, h0 = im.size
            img = XLImage(path)
            img.width, img.height = IMG_W, int(IMG_W * h0 / w0)
            ws.add_image(img, f"F{r}")
            img_h = img.height
        js_pts = (js.count("\n") + 1) * 12
        text_pts = max(Q.lines_for(vals[3], PUSH_WIDTHS["D"], 10), Q.lines_for(label, PUSH_WIDTHS["B"], 10)) * 14
        ws.row_dimensions[r].height = min(MAX_ROW_PT, max(js_pts, text_pts, img_h * 0.75 + 14, 60))
    ws.freeze_panes = "A2"
    ws.sheet_view.showGridLines = False
    return rows


def link_blocks(wb, blocks, rows):
    """A 'Push' link beside each block's status, to its row on Captured pushes."""
    ws = wb[Q.CHECK_SHEET]
    for i, (_scell, header, _first, _last) in enumerate(blocks, 1):
        c = ws.cell(header, 7, "Push ›")
        c.hyperlink = Hyperlink(ref=c.coordinate, location=f"'{PUSHES_SHEET}'!A{rows[i]}")
        c.font = Font(name=Q.F, sz=9, bold=True, color=Q.SLATE, underline="single")
        c.alignment = Alignment(horizontal="left", vertical="center")


# ------------------------------------------------------------------ main
def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    events_path, shots_dir, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(events_path, encoding="utf-8") as fh:
        spec = json.load(fh)

    open_values, warnings = [], []
    events = []
    for ev in spec.get("events") or []:
        ev = dict(ev)
        ev["params"], pending = judge(ev)
        source = (ev.get("source") or "").strip().lower()
        lead = {"not fired": "Did not fire", "web pixel": "Fires in the web pixel sandbox"}.get(source)
        ev["trigger"] = nodash(ev.get("trigger") or "")
        ev["note"] = nodash(_joined(lead, ev.get("note"))) or None
        label = ev.get("event", "?") + (f" ({ev['variant']})" if ev.get("variant") else "")
        if pending:
            open_values.append(f"{label}: {', '.join(pending)}")
        if ev["note"] and len(ev["note"]) > EVENT_NOTE_BUDGET:
            warnings.append(f"{label}: event note is {len(ev['note'])} chars, keep it under {EVENT_NOTE_BUDGET}")
        for p in ev["params"]:
            if p["notes"] and len(p["notes"]) > NOTE_BUDGET + 80:
                warnings.append(f"{label}: {p['name']} note is long ({len(p['notes'])} chars), trim it to fragments")
        events.append(ev)

    tested = " on ".join(x for x in (spec.get("tested"), spec.get("site")) if x)
    report = dict(spec, events=events)
    report.setdefault("instructions", "Checks filled from the pushes captured" +
                      (f" {tested}" if tested else "") + ". Change any you disagree with; "
                      "event status rolls up automatically.")
    report.setdefault("steps", [
        "0.  Filled in by /qa-datalayer from the pushes it captured" + (f" ({tested})" if tested else "") +
        ". Each block's Push link opens the push, verbatim, with a screenshot of what triggered it."])

    try:
        wb, cached, blocks = Q.build(report)
    except ValueError as exc:
        sys.exit(str(exc))
    rows = build_pushes(wb, events, blocks, shots_dir)
    link_blocks(wb, blocks, rows)
    Q.save(wb, cached, out_path)

    statuses = [cached[Q.CHECK_SHEET][scell] for scell, *_ in blocks]
    print(f"saved {out_path}: {len(events)} events, "
          f"{sum(s == 'Pass' for s in statuses)} Pass, {sum(s == 'Fail' for s in statuses)} Fail, "
          f"{sum(s == 'In progress' for s in statuses)} In progress")
    if open_values:
        print("\nVALUE CHECKS STILL YOURS TO JUDGE (present, not an exact match; set value_ok):")
        for line in open_values:
            print("  " + line)
    for w in warnings:
        print("WARNING: " + w)
    if len(os.path.abspath(out_path)) >= 259:
        print("WARNING: output path is >= 259 chars, Windows Excel may refuse to open it. Use a shorter filename.")


if __name__ == "__main__":
    main()
