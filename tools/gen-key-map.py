#!/usr/bin/env python3
"""Generate an SVG visualization of Saylor's karabiner rules."""

# Layout: ANSI 60% with annotated rows
# Key positions are (col, row, width_units). 1 unit = 60px, gap = 6px.
U = 60
G = 6
PAD = 28
ROWS = 5
COLS = 15  # widest row in units
# Extra vertical gap added AFTER row index, to make room for chord bands underneath.
EXTRA_GAP_AFTER = {0: 0, 1: 60, 2: 56, 3: 8, 4: 0}
TOP_OFFSET = 180  # room above row 0 for triple-chord brackets and title

# Each row: list of (label, width_units, key_id_or_None)
# key_id is a stable identifier we use to look up annotations.
rows = [
    # Row 0 - numbers
    [("`", 1, "grave"), ("1", 1, "1"), ("2", 1, "2"), ("3", 1, "3"), ("4", 1, "4"),
     ("5", 1, "5"), ("6", 1, "6"), ("7", 1, "7"), ("8", 1, "8"), ("9", 1, "9"),
     ("0", 1, "0"), ("-", 1, "hyphen"), ("=", 1, "equal"), ("delete", 2, "backspace")],
    # Row 1 - QWERTY top
    [("tab", 1.5, "tab"), ("Q", 1, "q"), ("W", 1, "w"), ("E", 1, "e"), ("R", 1, "r"),
     ("T", 1, "t"), ("Y", 1, "y"), ("U", 1, "u"), ("I", 1, "i"), ("O", 1, "o"),
     ("P", 1, "p"), ("[", 1, "lbracket"), ("]", 1, "rbracket"), ("\\", 1.5, "backslash")],
    # Row 2 - home row
    [("caps", 1.75, "caps"), ("A", 1, "a"), ("S", 1, "s"), ("D", 1, "d"), ("F", 1, "f"),
     ("G", 1, "g"), ("H", 1, "h"), ("J", 1, "j"), ("K", 1, "k"), ("L", 1, "l"),
     (";", 1, "semi"), ("'", 1, "quote"), ("return", 2.25, "return")],
    # Row 3 - bottom alpha
    [("shift", 2.25, "lshift"), ("Z", 1, "z"), ("X", 1, "x"), ("C", 1, "c"), ("V", 1, "v"),
     ("B", 1, "b"), ("N", 1, "n"), ("M", 1, "m"), (",", 1, "comma"), (".", 1, "period"),
     ("/", 1, "slash"), ("shift", 2.75, "rshift")],
    # Row 4 - modifiers + space
    [("ctrl", 1.25, "lctrl"), ("opt", 1.25, "lopt"), ("cmd", 1.25, "lcmd"),
     ("space", 6.25, "space"), ("cmd", 1.25, "rcmd"), ("opt", 1.25, "ropt"),
     ("ctrl", 1.25, "rctrl")],
]

# Annotations for each key.
# Format: dict[key_id] = {
#   "hyper": text shown when Hyper modifier is held (small text bottom of key)
#   "chord": list of (partner_key_id, output, label_for_pair)  -- chord/simultaneous press
#   "tap": text shown for tap-vs-hold (caps lock)
#   "fill": override key fill color
# }
ann = {
    "caps": {"tap": "esc", "hyper_self": "HYPER", "fill": "#fde68a"},
    # Hyper layer outputs
    "h": {"hyper": "← word", "hyper_shift": "shift+← word"},
    "j": {"hyper": "←", "hyper_shift": "shift+←"},
    "k": {"hyper": "↑", "hyper_shift": "shift+↑"},
    "l": {"hyper": "↓", "hyper_shift": "shift+↓"},
    "semi": {"hyper": "→", "hyper_shift": "shift+→"},
    "quote": {"hyper": "→ word", "hyper_shift": "shift+→ word"},
    "u": {"hyper": "{", "hyper_shift": "}"},
    "i": {"hyper": "(", "hyper_shift": ")"},
    "o": {"hyper": "[", "hyper_shift": "]"},
    "p": {"hyper": "-", "hyper_shift": "_"},
    "w": {"hyper": "`"},
    "e": {"hyper": "="},
    "r": {"hyper": ">"},
    "s": {"hyper": "/"},
    "d": {"hyper": "?"},
    "f": {"hyper": "$"},
    "space": {"hyper": "space"},
}

# Chords (simultaneous keypresses).
# Each entry: (id_a, id_b, label, color)
chords_pair = [
    ("s", "d", "delete", "#fca5a5"),
    ("d", "f", "fwd delete", "#fca5a5"),
    ("x", "c", "enter", "#86efac"),
    ("k", "l", "enter*", "#86efac"),       # editor-only (Atom/VS Code)
    ("l", "semi", "tab / →", "#93c5fd"),   # tab and hyper-context: cmd+→
    ("j", "k", "shift+tab / ←", "#93c5fd"),
]
# Three-key chords -- drawn as a labeled box around three keys.
chords_triple = [
    (["k", "s", "d"], "delete word", "#fca5a5"),
    (["k", "d", "f"], "fwd delete word", "#fca5a5"),
    (["j", "s", "d"], "delete line", "#f87171"),
]

# Build geometry: for each row, compute x-positions of each key based on cumulative widths.
def key_positions():
    positions = {}  # key_id -> (x, y, w_units)
    for ridx, row in enumerate(rows):
        x = 0.0
        for label, w, kid in row:
            if kid:
                positions[kid] = (x, ridx, w)
            x += w
    return positions

positions = key_positions()

def row_y(ridx):
    y = PAD + TOP_OFFSET
    for i in range(ridx):
        y += U + G + EXTRA_GAP_AFTER.get(i, 0)
    return y

def key_xy(kid):
    x_units, ridx, w = positions[kid]
    x = PAD + x_units * (U + G)
    y = row_y(ridx)
    return x, y, w * U + (w - 1) * G if w > 1 else w * U

# Compute SVG canvas size
canvas_w = PAD * 2 + COLS * U + (COLS - 1) * G
last_row_y = row_y(ROWS - 1) + U
canvas_h = last_row_y + 240  # extra for legend

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

svg = []
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {canvas_w} {canvas_h}" font-family="Inter, -apple-system, system-ui, sans-serif">')
svg.append(f'<rect width="100%" height="100%" fill="#0f172a"/>')

# Title block
svg.append(f'<text x="{PAD}" y="48" fill="#f8fafc" font-size="28" font-weight="700">Karabiner personal rules</text>')
svg.append(f'<text x="{PAD}" y="76" fill="#94a3b8" font-size="14">caps lock is the heart of this layout. tap = esc, hold = HYPER (⌃⌥⌘⇧).</text>')
svg.append(f'<text x="{PAD}" y="96" fill="#94a3b8" font-size="14">letters in blue are remapped under HYPER. red/green badges connect simultaneous-press chords.</text>')

# Draw chord bands FIRST (under keys) for pairs. Stagger when keys overlap.
def draw_chord_pair(a, b, label, color, level=0):
    ax, ay, aw = key_xy(a)
    bx, by, bw = key_xy(b)
    if ay != by:
        return
    x1 = min(ax, bx)
    x2 = max(ax + aw, bx + bw)
    band_y = ay + U + 8 + level * 24
    svg.append(
        f'<path d="M {x1+8} {band_y} L {x2-8} {band_y}" stroke="{color}" stroke-width="3" stroke-linecap="round"/>'
    )
    badge_w = max(76, len(label)*7 + 12)
    svg.append(
        f'<rect x="{(x1+x2)/2 - badge_w/2}" y="{band_y+4}" width="{badge_w}" height="18" rx="4" fill="{color}"/>'
    )
    svg.append(
        f'<text x="{(x1+x2)/2}" y="{band_y+18}" fill="#0f172a" font-size="11" font-weight="700" text-anchor="middle">{esc(label)}</text>'
    )

# Triple chord: bracket above three keys with label, stacked by level to avoid overlap
def draw_chord_triple(keys, label, color, level=0):
    xs = [key_xy(k) for k in keys]
    rows_y = set(p[1] for p in xs)
    base_y = min(p[1] for p in xs)  # top of topmost key
    # stack offset: each level adds 26px upward
    y = base_y - 14 - level * 28
    left = min(p[0] for p in xs)
    right = max(p[0]+p[2] for p in xs)
    # drop-down connector lines to each key top
    for p in xs:
        kx_center = p[0] + p[2]/2
        svg.append(f'<line x1="{kx_center}" y1="{y}" x2="{kx_center}" y2="{p[1]}" stroke="{color}" stroke-width="1.5" stroke-dasharray="2,2" opacity="0.7"/>')
    # horizontal bar
    svg.append(f'<line x1="{left}" y1="{y}" x2="{right}" y2="{y}" stroke="{color}" stroke-width="2.5"/>')
    # label badge
    lbl = f"{label} ({'+'.join(keys)})"
    badge_w = max(140, len(lbl) * 7)
    cx = (left+right)/2
    svg.append(f'<rect x="{cx - badge_w/2}" y="{y-16}" width="{badge_w}" height="16" rx="3" fill="{color}"/>')
    svg.append(f'<text x="{cx}" y="{y-4}" fill="#0f172a" font-size="11" font-weight="700" text-anchor="middle">{esc(lbl)}</text>')

# Draw triple chords above keys -- stagger levels so labels don't collide
for level, (keys, label, color) in enumerate(chords_triple):
    draw_chord_triple(keys, label, color, level=level)

# Draw keys
def draw_key(kid, label, w_units, x_units, ridx):
    x = PAD + x_units * (U + G)
    y = row_y(ridx)
    w = w_units * U + (w_units - 1) * G if w_units > 1 else U
    a = ann.get(kid, {})
    fill = a.get("fill", "#1e293b")
    stroke = "#475569"
    is_hyper = "hyper" in a or "hyper_self" in a
    if is_hyper and "fill" not in a:
        fill = "#1e3a8a"
        stroke = "#3b82f6"
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{U}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
    # Base label (top-left)
    svg.append(f'<text x="{x+8}" y="{y+20}" fill="#f1f5f9" font-size="13" font-weight="600">{esc(label)}</text>')
    # Tap-vs-hold for caps
    if "tap" in a:
        svg.append(f'<text x="{x+w-8}" y="{y+20}" fill="#92400e" font-size="11" text-anchor="end" font-weight="700">tap: {esc(a["tap"])}</text>')
    if "hyper_self" in a:
        svg.append(f'<text x="{x+w/2}" y="{y+U-12}" fill="#92400e" font-size="14" text-anchor="middle" font-weight="800">{esc(a["hyper_self"])}</text>')
    # Hyper output (centered, bigger)
    if "hyper" in a:
        svg.append(f'<text x="{x+w/2}" y="{y+U-22}" fill="#93c5fd" font-size="14" text-anchor="middle" font-weight="700">{esc(a["hyper"])}</text>')
        if "hyper_shift" in a:
            svg.append(f'<text x="{x+w/2}" y="{y+U-8}" fill="#94a3b8" font-size="9" text-anchor="middle">⇧ {esc(a["hyper_shift"])}</text>')

for ridx, row in enumerate(rows):
    x_units = 0.0
    for label, w, kid in row:
        if kid:
            draw_key(kid, label, w, x_units, ridx)
        else:
            # blank spacer
            x = PAD + x_units * (U + G)
            y = row_y(ridx)
            wpx = w * U + (w - 1) * G if w > 1 else U
            svg.append(f'<rect x="{x}" y="{y}" width="{wpx}" height="{U}" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1"/>')
            svg.append(f'<text x="{x+8}" y="{y+20}" fill="#475569" font-size="12">{esc(label)}</text>')
        x_units += w

# Draw chord pair bands (under-row arcs). Assign levels so overlapping pairs stack.
# Greedy: walk pairs left-to-right; each pair gets the lowest level that doesn't collide.
def pair_extent(a, b):
    ax, _, aw = key_xy(a); bx, _, bw = key_xy(b)
    return (min(ax, bx), max(ax+aw, bx+bw))

assigned = []  # list of (level, x1, x2)
for a, b, label, color in chords_pair:
    x1, x2 = pair_extent(a, b)
    lvl = 0
    while any(l == lvl and not (x2 < ox1 - 4 or x1 > ox2 + 4) for l, ox1, ox2 in assigned):
        lvl += 1
    assigned.append((lvl, x1, x2))
    draw_chord_pair(a, b, label, color, level=lvl)

# Legend
legend_y = last_row_y + 40
svg.append(f'<text x="{PAD}" y="{legend_y}" fill="#f1f5f9" font-size="16" font-weight="700">Legend</text>')
items = [
    ("#1e3a8a", "#3b82f6", "Hyper-mapped key (blue text = output when caps held)"),
    ("#fde68a", "#fbbf24", "caps lock — tap for esc, hold for HYPER"),
    ("#fca5a5", "#ef4444", "delete chord (sd / df / k+sd / k+df / j+sd)"),
    ("#86efac", "#22c55e", "enter chord (xc, or kl in editors)"),
    ("#93c5fd", "#3b82f6", "tab / motion chord (l+; , j+k)"),
]
for i, (fill, stroke, text) in enumerate(items):
    yi = legend_y + 18 + i*22
    svg.append(f'<rect x="{PAD}" y="{yi}" width="18" height="14" rx="3" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
    svg.append(f'<text x="{PAD+26}" y="{yi+12}" fill="#cbd5e1" font-size="12">{esc(text)}</text>')

# Footer notes
fy = legend_y + 18 + len(items)*22 + 14
notes = [
    "Hyper = right ⌃⌥⌘⇧ (held all together via caps lock).",
    "Chords fire when two/three keys are pressed simultaneously (within Karabiner's threshold, default ~50ms).",
    "k+l → enter only inside Atom and VS Code; everywhere else, k+l does nothing special.",
]
for i, n in enumerate(notes):
    svg.append(f'<text x="{PAD}" y="{fy + i*16}" fill="#64748b" font-size="11">• {esc(n)}</text>')

svg.append('</svg>')

out = '\n'.join(svg)
with open('/tmp/karabiner-viz/karabiner-key-map.svg', 'w') as f:
    f.write(out)
print(f"wrote /tmp/karabiner-viz/karabiner-key-map.svg ({len(out)} bytes)")
