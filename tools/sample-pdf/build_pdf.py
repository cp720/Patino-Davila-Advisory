# -*- coding: utf-8 -*-
#
# Generates the sample deliverable PDF at patinodavila.com/sample-deliverable.pdf
# (linked from the "Download a full sample month" button in the Deliverables section).
#
# The numbers/copy below are transcribed from source-data.xlsx (Dashboard, 13-Week
# Cash Flow, Commentary tabs) -- they are NOT read live from that file. To update
# the sample: edit source-data.xlsx, manually copy the changed values into this
# script (KPI tiles, chart data, table rows, commentary text below), then:
#   pip install reportlab
#   python build_pdf.py
# and copy the resulting sample.pdf over the repo's sample-deliverable.pdf.
#
# Requires reportlab (`pip install reportlab`); no LibreOffice/Excel needed.
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

# ---- brand palette (from patinodavila.com CSS custom properties) ----
PAPER = HexColor('#F4F6F3')
PAPER2 = HexColor('#EAEEE8')
CARD = HexColor('#FFFFFF')
INK = HexColor('#173029')
INK_SOFT = HexColor('#4C5C55')
LINE = HexColor('#D7DDD4')
TEAL = HexColor('#2F7D72')
AMBER = HexColor('#C0812A')
WHITE = HexColor('#FFFFFF')

FONT = 'Helvetica'
FONT_B = 'Helvetica-Bold'
MONO = 'Courier'
MONO_B = 'Courier-Bold'

OUT = 'sample.pdf'

LAND_W, LAND_H = landscape(letter)  # 792 x 612
PORT_W, PORT_H = letter             # 612 x 792


def rounded_card(c, x, y, w, h, r=10, fill=CARD, stroke=LINE, lw=1):
    c.saveState()
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(lw)
    c.roundRect(x, y, w, h, r, fill=1, stroke=1)
    c.restoreState()


def eyebrow(c, x, y, text, color=AMBER, size=8):
    c.setFont(MONO_B, size)
    c.setFillColor(color)
    c.drawString(x, y, text.upper())


def wrapped(c, x, y, text, font=FONT, size=9, color=INK_SOFT, max_width=200, leading=12):
    c.setFont(font, size)
    c.setFillColor(color)
    lines = simpleSplit(text, font, size, max_width)
    for i, line in enumerate(lines):
        c.drawString(x, y - i * leading, line)
    return y - len(lines) * leading


def sample_badge(c, x, y):
    c.saveState()
    c.setFillColor(AMBER)
    c.roundRect(x, y, 62, 16, 8, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont(MONO_B, 7.5)
    c.drawCentredString(x + 31, y + 5, 'SAMPLE')
    c.restoreState()


def kpi_tile(c, x, y, w, h, label, value, sub, warn=False):
    rounded_card(c, x, y, w, h, r=8)
    c.setFont(MONO_B, 7.2)
    c.setFillColor(TEAL)
    c.drawString(x + 14, y + h - 20, label.upper())
    c.setFont(FONT_B, 20)
    c.setFillColor(AMBER if warn else INK)
    c.drawString(x + 14, y + h - 44, value)
    c.setFont(FONT, 8.5)
    c.setFillColor(INK_SOFT)
    c.drawString(x + 14, y + 12, sub)


def line_chart(c, x, y, w, h, labels, values, min_line=None, low_idx=None, low_label=None,
               value_fmt=lambda v: f'{v:,.0f}'):
    """Draws a simple line chart in the box (x,y,w,h) with axis labels."""
    pad_l, pad_r, pad_t, pad_b = 6, 6, 10, 18
    plot_x = x + pad_l
    plot_y = y + pad_b
    plot_w = w - pad_l - pad_r
    plot_h = h - pad_t - pad_b

    all_vals = list(values) + ([min_line] if min_line else [])
    vmin, vmax = min(all_vals), max(all_vals)
    if vmax == vmin:
        vmax = vmin + 1
    vpad = (vmax - vmin) * 0.15
    vmin -= vpad
    vmax += vpad

    def px(i):
        return plot_x + (i / (len(values) - 1)) * plot_w if len(values) > 1 else plot_x

    def py(v):
        return plot_y + ((v - vmin) / (vmax - vmin)) * plot_h

    if min_line is not None:
        c.saveState()
        c.setStrokeColor(AMBER)
        c.setLineWidth(1.2)
        c.setDash(4, 3)
        yline = py(min_line)
        c.line(plot_x, yline, plot_x + plot_w, yline)
        c.restoreState()
        c.setFont(MONO, 6.5)
        c.setFillColor(INK_SOFT)
        c.drawString(plot_x, yline + 3, f'min ${min_line:,.0f}')

    c.saveState()
    c.setStrokeColor(TEAL)
    c.setLineWidth(2.2)
    p = c.beginPath()
    p.moveTo(px(0), py(values[0]))
    for i in range(1, len(values)):
        p.lineTo(px(i), py(values[i]))
    c.drawPath(p, stroke=1, fill=0)
    c.restoreState()

    if low_idx is not None:
        lx, ly = px(low_idx), py(values[low_idx])
        c.setFillColor(AMBER)
        c.circle(lx, ly, 3.3, fill=1, stroke=0)
        if low_label:
            c.setFont(MONO_B, 6.8)
            c.setFillColor(INK)
            label_y = ly - 14 if (ly - 14) > plot_y else ly + 14
            c.drawCentredString(lx, label_y, low_label)

    c.setFont(MONO, 6.3)
    c.setFillColor(INK_SOFT)
    step = max(1, len(labels) // 7)
    for i, lab in enumerate(labels):
        if i % step == 0 or i == len(labels) - 1:
            c.drawCentredString(px(i), y, lab)


def chip(c, x, y, text, w=None):
    c.setFont(FONT, 8)
    tw = c.stringWidth(text, FONT, 8)
    w = w or (tw + 16)
    c.saveState()
    c.setStrokeColor(LINE)
    c.setFillColor(CARD)
    c.roundRect(x, y, w, 16, 8, fill=1, stroke=1)
    c.setFillColor(INK)
    c.drawCentredString(x + w / 2, y + 5, text)
    c.restoreState()
    return w


# =========================================================
# PAGE 1 — DASHBOARD (landscape)
# =========================================================
c = canvas.Canvas(OUT, pagesize=landscape(letter))
c.setFillColor(PAPER)
c.rect(0, 0, LAND_W, LAND_H, fill=1, stroke=0)

M = 36
sample_badge(c, LAND_W - M - 62, LAND_H - M - 4)

c.setFont(FONT_B, 18)
c.setFillColor(INK)
c.drawString(M, LAND_H - M, 'SUMMIT RIDGE CONSTRUCTION LLC')
c.setFont(FONT, 10)
c.setFillColor(INK_SOFT)
c.drawString(M, LAND_H - M - 18, 'Monthly Financial Brief  —  Reporting Period: July 2026  —  Prepared by Patino Davila Advisory')

tile_y = LAND_H - M - 110
tile_w = (LAND_W - 2 * M - 2 * 14) / 3
tile_h = 68
kpi_tile(c, M, tile_y, tile_w, tile_h, 'Revenue (Jul)', '$218,400', '+9.7% vs Jun')
kpi_tile(c, M + tile_w + 14, tile_y, tile_w, tile_h, 'Gross Margin', '27.5%', '6-mo avg 27.7%')
kpi_tile(c, M + 2 * (tile_w + 14), tile_y, tile_w, tile_h, 'Net Income (Jul)', '$25,600', '11.7% net margin')

tile_y2 = tile_y - tile_h - 14
kpi_tile(c, M, tile_y2, tile_w, tile_h, 'Cash on Hand', '$142,000', 'as of Jul 31')
kpi_tile(c, M + tile_w + 14, tile_y2, tile_w, tile_h, '13-Week Low Cash', '$1,100', 'week of Oct 6 — action needed', warn=True)
kpi_tile(c, M + 2 * (tile_w + 14), tile_y2, tile_w, tile_h, 'Signed Backlog', '$1,815,000', '~8.3 months coverage')

panel_y = M
panel_h = tile_y2 - 14 - panel_y
panel_w = (LAND_W - 2 * M - 14) / 2

rounded_card(c, M, panel_y, panel_w, panel_h)
eyebrow(c, M + 16, panel_y + panel_h - 20, 'Revenue — Trailing 6 Months')
months = ['Feb-26', 'Mar-26', 'Apr-26', 'May-26', 'Jun-26', 'Jul-26']
revenue = [172000, 195000, 208000, 231000, 199000, 218400]
line_chart(c, M + 12, panel_y + 14, panel_w - 24, panel_h - 46, months, revenue)

rp_x = M + panel_w + 14
rounded_card(c, rp_x, panel_y, panel_w, panel_h)
eyebrow(c, rp_x + 16, panel_y + panel_h - 20, 'Working Capital Snapshot')
rows = [
    ('Accounts Receivable', '$312,000'),
    ('   Current (0-30 days)', '$168,000'),
    ('   31-60 days', '$96,000'),
    ('   61+ days', '$48,000'),
    ('Accounts Payable', '$148,000'),
    ('Days Sales Outstanding', '48 days'),
    ('Current Ratio', '1.8'),
]
ry = panel_y + panel_h - 42
for label, val in rows:
    c.setFont(FONT_B if not label.startswith(' ') else FONT, 9)
    c.setFillColor(INK if not label.startswith(' ') else INK_SOFT)
    c.drawString(rp_x + 16, ry, label)
    c.setFont(FONT_B, 9)
    c.setFillColor(INK)
    c.drawRightString(rp_x + panel_w - 16, ry, val)
    ry -= 17

c.setFont(FONT, 8)
c.setFillColor(INK_SOFT)
c.drawString(M, M - 22, 'See the 13-week cash flow and commentary pages for the full forward view.')
c.setFont(FONT, 7.5)
c.drawString(M, M - 34, 'Illustrative sample for a fictional company, for demonstration purposes only.')

c.showPage()

# =========================================================
# PAGE 2 — 13-WEEK CASH FLOW (landscape)
# =========================================================
c.setPageSize(landscape(letter))
c.setFillColor(PAPER)
c.rect(0, 0, LAND_W, LAND_H, fill=1, stroke=0)

sample_badge(c, LAND_W - M - 62, LAND_H - M - 4)
c.setFont(FONT_B, 16)
c.setFillColor(INK)
c.drawString(M, LAND_H - M, '13-Week Rolling Cash Flow Forecast')
c.setFont(FONT, 9.5)
c.setFillColor(INK_SOFT)
c.drawString(M, LAND_H - M - 16, 'Weeks beginning Monday. Operating minimum cash target: $25,000.')

weeks = ['Aug 25', 'Sep 1', 'Sep 8', 'Sep 15', 'Sep 22', 'Sep 29', 'Oct 6', 'Oct 13', 'Oct 20', 'Oct 27', 'Nov 3', 'Nov 10', 'Nov 17']
ending_cash = [131300, 115800, 44300, 20800, 2300, 13600, 1100, 81600, 65100, 66400, 52900, 59400, 46900]
low_idx = ending_cash.index(min(ending_cash))

chart_y = LAND_H - M - 190
chart_h = 140
rounded_card(c, M, chart_y, LAND_W - 2 * M, chart_h)
line_chart(c, M + 16, chart_y + 16, LAND_W - 2 * M - 32, chart_h - 34, weeks, ending_cash,
           min_line=25000, low_idx=low_idx, low_label=f'{weeks[low_idx]} — cash gets tight')

# table
beginning = [142000, 131300, 115800, 44300, 20800, 2300, 13600, 1100, 81600, 65100, 66400, 52900, 59400]
inflows = [52000, 24000, 18000, 28000, 31000, 46000, 38000, 118000, 34000, 41000, 37000, 44000, 39000]
outflows = [62700, 39500, 89500, 51500, 49500, 34700, 50500, 37500, 50500, 39700, 50500, 37500, 51500]
net = [b - a for a, b in zip(outflows, inflows)]
flag = ['OK', 'OK', 'OK', '⚠', '⚠', '⚠', '⚠', 'OK', 'OK', 'OK', 'OK', 'OK', 'OK']

table_y_top = chart_y - 18
row_labels = ['Week beginning', 'Beginning Cash', 'Total Inflows', 'Total Outflows', 'Net Cash Flow', 'Ending Cash', 'Below $25k min?']
row_data = [weeks, beginning, inflows, outflows, net, ending_cash, flag]

col0_w = 108
col_w = (LAND_W - 2 * M - col0_w) / 13
row_h = 16

for r, (rl, rd) in enumerate(zip(row_labels, row_data)):
    ry = table_y_top - r * row_h
    c.setFont(FONT_B, 7.6)
    c.setFillColor(INK)
    c.drawString(M, ry, rl)
    for i, v in enumerate(rd):
        cx = M + col0_w + i * col_w + col_w / 2
        if isinstance(v, (int, float)):
            txt = f'{v:,.0f}'
        else:
            txt = str(v)
        warn = (rl == 'Below $25k min?' and v == '⚠')
        c.setFont(FONT_B if warn else FONT, 7.3)
        c.setFillColor(AMBER if warn else INK_SOFT)
        c.drawCentredString(cx, ry, txt)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.4)
    c.line(M, ry - 4, LAND_W - M, ry - 4)

c.showPage()

# =========================================================
# PAGE 3 — COMMENTARY (portrait)
# =========================================================
c.setPageSize(letter)
c.setFillColor(PAPER)
c.rect(0, 0, PORT_W, PORT_H, fill=1, stroke=0)

sample_badge(c, PORT_W - M - 62, PORT_H - M - 4)
c.setFont(FONT_B, 16)
c.setFillColor(INK)
c.drawString(M, PORT_H - M, 'Summit Ridge Construction LLC')
c.setFont(FONT, 10)
c.setFillColor(INK_SOFT)
c.drawString(M, PORT_H - M - 16, 'Monthly Commentary — July 2026')

y = PORT_H - M - 50
content_w = PORT_W - 2 * M


def section(c, y, heading, body, heading_color=TEAL):
    eyebrow(c, M, y, heading, color=heading_color, size=8.5)
    y -= 16
    y = wrapped(c, M, y, body, font=FONT, size=9.3, color=INK, max_width=content_w, leading=13)
    return y - 16


y = section(c, y, 'The headline',
    'You had another profitable month — $25,600 of net income on $218,400 of revenue (11.7% net margin), right in '
    'line with your six-month trend. Profit is not the problem. Timing is. Our 13-week forecast shows cash dropping to '
    'about $1,100 the week of October 6 — well below the $25,000 you want in the account to run comfortably. This is '
    'fixable, and you have roughly six weeks of runway to act.')

y = section(c, y, "Why cash gets tight (even though you're profitable)",
    'Three things land close together: (1) The Hillcrest final draw ($96,000) slipped — expected the week of Sep 8, '
    'now tracking to Oct 13, five weeks later. (2) Q3 estimated taxes ($18,000) are due Sep 15. (3) The Maple Grove '
    'material order ($52,000) hits Sep 8. Individually, none of these is a problem. Stacked in the same four weeks '
    '— while your big receivable is late — they drain the account faster than collections refill it. Cash stays '
    'under your $25k minimum from the week of Sep 15 through Oct 6.')

y = section(c, y, "What we'd do about it — three options",
    'A. Pull Hillcrest forward: offer a 1% early-payment discount ($960) to release the $96,000 draw in September '
    'instead of October. Highest-leverage move. B. Push the big outflows past the tax date: ask Maple Grove for '
    'net-45 terms on the $52,000 order, and pause owner draws for three weeks (frees ~$12,000). C. Put a safety '
    'net in place now: open a $50,000 line of credit while your numbers look strong — banks approve credit when '
    "you don't need it, not when you do.")

y = section(c, y, 'One thing to watch',
    "Days Sales Outstanding crept to 48 days, up from 41. Your final draws are being paid slowly — that's the same "
    'pattern that created this squeeze. Tightening billing the day a milestone completes (rather than at month-end) '
    'would pull cash in about a week sooner across every project and prevent the next crunch before it starts.')

rounded_card(c, M, y - 60, content_w, 64, fill=INK)
c.setFont(MONO_B, 8, )
c.setFillColor(HexColor('#E7B45E'))
c.drawString(M + 16, y - 20, 'BOTTOM LINE')
wrapped(c, M + 16, y - 36, 'Strong operating month, one avoidable cash pinch on the horizon. Take option A plus a '
        "small piece of B and you sail through October above your minimum. Let's lock the plan on this month's "
        'strategy call.', font=FONT, size=9, color=PAPER, max_width=content_w - 32, leading=12)

c.setFont(FONT, 8)
c.setFillColor(INK_SOFT)
c.drawString(M, M, 'Prepared by Patino Davila Advisory  ·  patinodavilaadvisory@gmail.com / 973-856-0624')
c.setFont(FONT, 7.5)
c.drawRightString(PORT_W - M, M, 'Illustrative sample — fictional company, for demonstration purposes only.')

c.showPage()
c.save()
print('Wrote', OUT)
