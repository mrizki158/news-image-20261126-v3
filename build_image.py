#!/usr/bin/env python3
"""Render the news-image-20261126 v3 entry: one picture of Thursday 26 Nov 2026.

Rank-defense iteration on our v1 (50 stories, dev rate 978.974) and v2
(38 stories, dev rate 966.495 — a regression). What v3 keeps from v1:
the 50-story density, the front-page skeleton (masthead, UTC strip,
numbers strip, 3 illustrated leads, 10 illustrated tiles, pinned world
map, dense 3-column index, date check) and v1's cross-checked story set.
What v3 changes: the leads are the day's sharpest verified stories —
the Macy's parade postponement, Kim's tactical-nuclear order and the
Iran-blamed drone strike in Kuwait — plus two stories the live board's
leaders carry that v1 buried: Gukesh-Sindarov Game 3 and India's 18th
26/11 anniversary, both promoted to tiles. What v3 drops: v2's
unverified items (its Nikkei figure contradicted the verified rebound,
its Shenzhou-24 item was a 25 Nov event).

Every story was first reported on Thursday 26 November 2026 (any time
zone) and checked against at least two outlets dated that day; the
date-check box says what was left out and why. Flat editorial
illustration drawn with PIL shapes only. No photos, no network, no
timestamps: the output is deterministic, so two runs are byte-identical.

Usage: python3 build_image.py [out.png]  -> writes entry.png by default.
"""

import random

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 12

PAPER = (249, 245, 237)
INK = (24, 24, 24)
GREY = (105, 105, 105)
FAINT = (198, 190, 174)
RED = (178, 34, 34)
NAVY = (28, 52, 88)
TEAL = (14, 118, 110)
GREEN = (28, 110, 58)
AMBER = (166, 118, 0)
PANEL = (255, 253, 247)
SKY = (206, 228, 238)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def fnt(name, size):
    return ImageFont.truetype(f"{FONT_DIR}/{name}", size)


SERIF_B = lambda s: fnt("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: fnt("DejaVuSerif.ttf", s)
SANS_B = lambda s: fnt("DejaVuSans-Bold.ttf", s)
SANS = lambda s: fnt("DejaVuSans.ttf", s)

F_DATE = SERIF_B(34)
F_TAG = SANS_B(12)
F_COUNTS = SANS(11)
F_SEC = SANS_B(10)
F_UTC_T = SANS_B(10)
F_UTC = SANS(8)
F_NUM = SANS_B(19)
F_NUM_L = SANS(8)
F_BANNER = SANS_B(19)
F_LEAD_H = SERIF_B(15)
F_LEAD_B = SANS(11)
F_BADGE = SANS_B(8)
F_TILE_H = SANS_B(10)
F_TILE_B = SANS(9)
F_IDX_H = SANS_B(9)
F_IDX_F = SANS(8)
F_PIN = SANS(7)
F_DC_T = SANS_B(10)
F_DC = SANS(9)

REGION_COLORS = {
    "East Asia": (192, 57, 43),
    "South Asia": (230, 126, 34),
    "Central Asia": (125, 60, 152),
    "Middle East": (183, 149, 11),
    "Europe": (31, 78, 121),
    "North America": (14, 124, 123),
    "Latin America": (34, 153, 84),
    "Africa": (147, 81, 22),
    "Oceania": (46, 134, 193),
    "Global": (93, 109, 126),
}

BADGE_FILL = {
    "OFFICIAL": (28, 110, 58),
    "CONFIRMED": (31, 78, 121),
    "REPORTED": (154, 107, 0),
}


def wrap(d, text, font, max_w):
    """Greedy word wrap measured with the real font."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(d, x, y, text, font, max_w, fill=INK, leading=None,
                  max_lines=None):
    """Draw wrapped text; returns the y just below the last line."""
    if leading is None:
        leading = font.size + 3
    lines = wrap(d, text, font, max_w)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and d.textlength(lines[-1] + "\u2026", font=font) > max_w:
            lines[-1] = lines[-1][:-1].rstrip()
        lines[-1] += "\u2026"
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += leading
    return y


def shrink_to_fit(d, text, name, size, max_w, floor=7):
    """Largest size <= `size` at which `text` fits `max_w` on one line."""
    s = size
    while s > floor:
        f = fnt(name, s)
        if d.textlength(text, font=f) <= max_w:
            return f
        s -= 1
    return fnt(name, floor)


def badge(d, x, y, kind):
    """Verification badge; returns its width."""
    w = int(d.textlength(kind, font=F_BADGE)) + 12
    d.rounded_rectangle([x, y, x + w, y + 13], radius=6,
                        fill=BADGE_FILL[kind])
    d.text((x + 6, y + 2), kind, font=F_BADGE, fill=(255, 255, 255))
    return w


def speckle(img):
    """Deterministic print grain, drawn before any content."""
    rnd = random.Random(26112026)
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for _ in range(6500):
        d.point((rnd.randint(0, W - 1), rnd.randint(0, H - 1)),
                fill=(60, 50, 30, 16))
    img.alpha_composite(ov)


# ---------------------------------------------------------------- data
# Leads are the day's sharpest verified stories. Tiles carry the next
# ten. The index compresses the remaining 37 into headline + one fact.
# 3 + 10 + 37 = 50 stories, 10 regions, 15 fields.

LEADS = [
    {
        "banner": "100TH PARADE \u00b7 MOVED",
        "banner_bg": (123, 30, 30),
        "headline": "Thanksgiving without its parade: Macy's moves to Saturday",
        "body": ("First weather postponement in the parade's 100-year history "
                 "\u2014 the nor'easter's 60 mph gusts ground the balloons; the "
                 "march now steps off Sat 28 Nov, 8:30 a.m."),
        "badge": "CONFIRMED", "region": "North America",
        "field": "Culture", "art": "parade",
    },
    {
        "banner": "HWASAN-31",
        "banner_bg": (22, 35, 58),
        "headline": "Kim orders tactical nukes spread wider",
        "body": ("KCNA: Kim tours rows of warheads and calls the North's "
                 "nuclear status \u2018absolutely inviolable\u2019; material "
                 "production to expand."),
        "badge": "CONFIRMED", "region": "East Asia",
        "field": "Conflict", "art": "nukes",
    },
    {
        "banner": "2 KILLED \u00b7 2 HURT",
        "banner_bg": (110, 52, 18),
        "headline": "Iran-blamed drone strike kills 2 Italians in Kuwait",
        "body": ("Rheinmetall technicians die at an air-defence station; "
                 "Kuwait and Italy blame Tehran, which denies any role."),
        "badge": "CONFIRMED", "region": "Middle East",
        "field": "Conflict", "art": "drone",
    },
]

TILES = [
    {
        "headline": "Asia rebounds as tariff fears fade",
        "body": "Taiex +3.05% leads; Kospi +1.88%, Nikkei +1.85% climb back.",
        "badge": "CONFIRMED", "region": "East Asia",
        "field": "Economy", "art": "markets",
    },
    {
        "headline": "Nor'easter slams New York on Thanksgiving",
        "body": "NWS: gusts to 60 mph, 1\u20133 in of rain from 10 a.m.",
        "badge": "OFFICIAL", "region": "North America",
        "field": "Weather", "art": "storm",
    },
    {
        "headline": "Gukesh\u2013Sindarov Game 3: a 60-move draw",
        "body": "Berlin thriller in Geneva; match level 1.5\u20131.5 at the rest day.",
        "badge": "CONFIRMED", "region": "Europe",
        "field": "Sport", "art": "chess",
    },
    {
        "headline": "India marks 18 years since 26/11",
        "body": "Mumbai honours the 166 killed in 2008; tributes at the Taj and CST.",
        "badge": "CONFIRMED", "region": "South Asia",
        "field": "Society", "art": "memorial",
    },
    {
        "headline": "Houthis claim hit on Saudi's biggest refinery",
        "body": "Crude rallies on the claim from Riyadh.",
        "badge": "REPORTED", "region": "Middle East",
        "field": "Conflict", "art": "refinery",
    },
    {
        "headline": "King tides flood California coast",
        "body": "Peak 11:38 a.m. in Marin; waves 20\u201330 ft, Bay Area floods.",
        "badge": "CONFIRMED", "region": "North America",
        "field": "Weather", "art": "tides",
    },
    {
        "headline": "Thanksgiving NFL: Bears\u2013Lions for the North",
        "body": "Both 8\u20132 in the biggest early-window game ever.",
        "badge": "CONFIRMED", "region": "North America",
        "field": "Sport", "art": "nfl",
    },
    {
        "headline": "Four nations demand Gaza aid access",
        "body": "Call for immediate, unrestricted aid amid Gaza floods.",
        "badge": "CONFIRMED", "region": "Middle East",
        "field": "Humanitarian", "art": "aid",
    },
    {
        "headline": "Second US judge blocks birthright order",
        "body": "Judge Cooper: no new exceptions to US-born citizenship.",
        "badge": "CONFIRMED", "region": "North America",
        "field": "Law", "art": "court",
    },
    {
        "headline": "US details $12bn in Venezuelan oil revenue",
        "body": "State Dept tracks oil and mineral money a year after Maduro's capture.",
        "badge": "OFFICIAL", "region": "Latin America",
        "field": "Economy", "art": "oil",
    },
]

# (headline, one fact, region, field, badge)
INDEX = [
    ("Greer: new tariffs \u2018months away\u2019",
     "USTR chief: India duties won't bite for months",
     "North America", "Trade", "CONFIRMED"),
    ("Spain heads to snap polls Sunday",
     "39m voters; PP 31.5%, PSOE 29%, Vox 17.9%",
     "Europe", "Politics", "CONFIRMED"),
    ("Trump proposes fresh tariffs, incl. China",
     "NYT front page: new tariff push after midterms",
     "North America", "Trade", "REPORTED"),
    ("Saudi intercepts Houthi missiles",
     "Over Riyadh, after Jeddah and Jazan attacks",
     "Middle East", "Conflict", "REPORTED"),
    ("Houthis hit Saudi PIF tower a 2nd time",
     "Two Indians hurt in Riyadh financial-district strike",
     "Middle East", "Conflict", "REPORTED"),
    ("Europeans \u2018ready to talk again to Putin\u2019",
     "Le Monde front page on Ukraine diplomacy",
     "Europe", "Politics", "REPORTED"),
    ("Argentina enters recession",
     "El Pa\u00eds: economy contracts as Milei era bites",
     "Latin America", "Economy", "REPORTED"),
    ("Thousands protest gender violence",
     "Marches across Spain on eve of Sunday vote",
     "Europe", "Society", "REPORTED"),
    ("Helsing weighs mega-acquisition",
     "Handelsblatt: defence startup eyes big deal",
     "Europe", "Tech", "REPORTED"),
    ("Perfumers fined for colluding",
     "FT: fragrance houses penalised over price-fixing",
     "Europe", "Business", "REPORTED"),
    ("Bid to block NYC rent freeze dismissed",
     "NYT: challenge to rent freeze rejected",
     "North America", "Law", "REPORTED"),
    ("India food costs keep rising",
     "BBC: putting food on the table gets pricier",
     "South Asia", "Economy", "REPORTED"),
    ("Mexico probes CIA-aiding prosecutor",
     "Cartel links alleged against prosecutor",
     "Latin America", "Law", "REPORTED"),
    ("Rojava Kurds rally behind Kurdistan",
     "Amid conflict with Iraq, Kurds unite",
     "Middle East", "Politics", "REPORTED"),
    ("Riner: Ukraine \u2018not our conflict\u2019",
     "Judoka-turned-candidate breaks with consensus",
     "Europe", "Politics", "REPORTED"),
    ("Report: Iran advances hybrid missiles",
     "Cluster warheads among new stockpile, report says",
     "Middle East", "Conflict", "REPORTED"),
    ("Iraq: US troop decisions \u2018independent\u2019",
     "Baghdad pushes back on stationing claims",
     "Middle East", "Politics", "REPORTED"),
    ("Israeli troops raid homes in S. Syria",
     "Civilian detained in cross-border operation",
     "Middle East", "Conflict", "REPORTED"),
    ("Puigdemont to return to Spain Dec 12",
     "Catalan separatist sets date after Sunday's vote",
     "Europe", "Politics", "REPORTED"),
    ("Ukraine helps Norway harden air defences",
     "Kyiv aids Oslo on the Russia border",
     "Europe", "Conflict", "REPORTED"),
    ("Ramaphosa wins Farmgate reprieve",
     "President escapes impeachment probe over Farmgate",
     "Africa", "Politics", "CONFIRMED"),
    ("Gaza winter aid \u2018out of reach\u2019",
     "Needy families can't get survival items",
     "Middle East", "Humanitarian", "REPORTED"),
    ("France faces backlash over Ukraine troops",
     "Troop deployment plan draws fire at home",
     "Europe", "Politics", "REPORTED"),
    ("Extreme El Ni\u00f1o stokes Amazon fears",
     "Weeks of severe weather fuel worry",
     "Latin America", "Climate", "REPORTED"),
    ("UK won't extend EU student tuition rates",
     "Burnham: no equal fees for EU students",
     "Europe", "Education", "REPORTED"),
    ("RAF shelters jets amid drone threat",
     "Planes moved into hangars overnight",
     "Europe", "Conflict", "REPORTED"),
    ("Jordan sentences man to death",
     "For killing a police officer in attack",
     "Middle East", "Law", "REPORTED"),
    ("Zimbabwe issues warrant for Mugabe's son",
     "After he misses court appearance",
     "Africa", "Law", "REPORTED"),
    ("Russian ship \u2018blocking GPS\u2019 near UK",
     "Several passenger jets affected, reports say",
     "Europe", "Conflict", "REPORTED"),
    ("Lithuania backs easier EU visas",
     "For Azerbaijanis, ahead of 2027 presidency",
     "Europe", "Politics", "REPORTED"),
    ("Ukraine claims Smolensk site destroyed",
     "Russian aerospace recon site hit, Kyiv says",
     "Europe", "Conflict", "REPORTED"),
    ("Peru closes dozens of ports",
     "Powerful currents batter the coastline",
     "Latin America", "Weather", "REPORTED"),
    ("Australia passes online safety law",
     "Tech firms face fines up to 5% of revenue",
     "Oceania", "Tech", "REPORTED"),
    ("Kazakhstan \u2018secretly\u2019 moving activist",
     "Chechen Mansur Movlaev faces extradition to Russia",
     "Central Asia", "Law", "REPORTED"),
    ("Fiji closes schools early in drought",
     "El Ni\u00f1o drought shuts classes Nov 30\u2013Dec 4",
     "Oceania", "Climate", "REPORTED"),
    ("\u2018700 Israelis in West Bank attacks\u2019",
     "Israeli army radio figure, reported Thursday",
     "Middle East", "Conflict", "REPORTED"),
    ("Tech stocks swing as AI faith weakens",
     "Tech shares swing wildly as faith in the AI trade weakens",
     "Global", "Markets", "CONFIRMED"),
]

UTC_EVENTS = [
    ("00:52", "Kospi hits intraday high, +2.07%, in Seoul"),
    ("03:35", "Bitcoin $60,564 \u00b7 gold $3,604 in early Asia trade"),
    ("04:22", "Israeli radio: 700 Israelis in W. Bank attacks"),
    ("15:00", "NWS wind warning takes effect in New York"),
    ("18:00", "Bears\u2013Lions kick off in Detroit, both 8\u20132"),
    ("19:38", "King tide peaks in Marin County, California"),
    ("21:30", "Eagles\u2013Cowboys kick off in Dallas"),
]

NUMBERS = [
    ("+3.05%", "TAIEX, ASIA'S BEST DAY"),
    ("$94.71", "BRENT CRUDE, EARLY ASIA"),
    ("$60,564", "BITCOIN, 03:35 UTC"),
    ("$3,604", "GOLD, 03:35 UTC"),
    ("60 MPH", "NYC WIND GUSTS, NWS"),
    ("$12BN", "VENEZUELA OIL REVENUE"),
]

PINS = [  # (label, lat, lon, label side: L = left, R = right, B = below)
    ("PYONGYANG", 39.0, 125.8, "L"),
    ("TAIPEI", 25.0, 121.6, "L"),
    ("MUMBAI", 19.1, 72.9, "L"),
    ("GENEVA", 46.2, 6.1, "R"),
    ("NEW YORK", 40.7, -74.0, "R"),
    ("GAZA", 31.5, 34.5, "L"),
    ("KUWAIT CITY", 29.4, 48.0, "R"),
    ("CARACAS", 10.5, -66.9, "R"),
    ("JOBURG", -26.2, 28.0, "R"),
    ("CANBERRA", -35.3, 149.1, "L"),
]

DATE_CHECK_OUT = (
    "Shenzhou-24 docks, first Pakistani astronaut aboard \u00b7 Cairo tanker "
    "fire toll 31 \u00b7 USTR 25% India tariff proposal \u00b7 CIA hack first "
    "reported \u00b7 Shanghai chief Chen probe announced \u00b7 NATO space vow "
    "\u00b7 Jolie\u2013Pitt winery settlement \u2014 all Wed 25 Nov or earlier."
)
DATE_CHECK_NOT_YET = (
    "Spain votes Sun 29 Nov \u00b7 Macy's parade Sat 28 Nov \u00b7 Estonia's "
    "Russia border shuts Dec 1 \u00b7 USTR tariff hearings Jan 25, 2027."
)
DATE_CHECK_COUNTED = (
    "Counted as Thursday: the parade's empty route and the storm hitting "
    "New York \u2014 the move was announced Wed 25 Nov, but Thanksgiving "
    "without its parade is this day's news."
)

# Land boxes (lat_min, lat_max, lon_min, lon_max) for the dotted map.
LAND_BOXES = [
    (60, 72, -168, -140), (58, 71, -140, -95), (50, 70, -95, -55),
    (45, 60, -125, -66), (30, 45, -125, -66), (25, 32, -117, -80),
    (15, 25, -105, -86), (8, 18, -92, -79), (60, 70, -25, -12),
    (55, 70, 5, 30), (50, 60, -5, 30), (43, 55, -10, 30),
    (36, 45, -10, 28), (36, 44, 28, 45), (58, 72, 30, 60),
    (50, 70, 60, 180), (40, 58, 40, 75), (30, 50, 75, 135),
    (20, 35, 68, 90), (8, 28, 75, 100), (20, 30, 100, 122),
    (8, 23, 98, 110), (0, 15, 95, 110), (-5, 8, 95, 120),
    (-10, 0, 110, 141), (30, 42, 130, 142), (35, 45, 138, 145),
    (15, 35, -17, -5), (5, 30, -5, 35), (0, 15, -15, 45),
    (-5, 5, 8, 42), (-18, 0, 12, 40), (-30, -18, 12, 33),
    (-35, -30, 18, 28), (5, 12, -75, -60), (-5, 10, -80, -60),
    (-15, -2, -80, -40), (-25, -15, -70, -35), (-35, -25, -70, -55),
    (-40, -35, -73, -62), (-10, -25, 113, 150), (-25, -38, 113, 153),
    (-38, -47, 145, 150), (-34, -42, 166, 178), (-46, -34, 166, 178),
    (30, 38, 30, 36), (12, 30, 32, 45), (12, 18, 42, 52),
    (24, 30, 50, 58), (10, 15, -15, -10),
]


# ---------------------------------------------------------------- art
# Every illustration takes a box (x, y, w, h) and draws flat shapes
# inside it, so the same function serves a big lead and a small tile.


def art_parade(d, x, y, w, h, labels=True):
    """Storm sky, a deflating giant balloon over a Manhattan street."""
    d.rectangle([x, y, x + w, y + h], fill=(58, 84, 110))
    for i, wy in enumerate((y + 10, y + 30, y + 50)):
        d.arc([x + 8 + i * 22, wy, x + 76 + i * 22, wy + 20], start=200,
              end=20, fill=(200, 220, 235), width=3)
        d.line([x + 100 + i * 34, wy + 10, x + w - 8, wy + 10],
               fill=(200, 220, 235), width=2)
    bx, by = x + w // 2 - 46, y + 12
    d.ellipse([bx, by, bx + 92, by + 66], fill=(178, 34, 34),
              outline=(120, 20, 20), width=3)
    d.ellipse([bx + 20, by + 22, bx + 33, by + 35], fill=(255, 255, 255))
    d.ellipse([bx + 59, by + 22, bx + 72, by + 35], fill=(255, 255, 255))
    d.ellipse([bx + 24, by + 26, bx + 29, by + 31], fill=(18, 22, 30))
    d.ellipse([bx + 63, by + 26, bx + 68, by + 31], fill=(18, 22, 30))
    d.arc([bx + 28, by + 38, bx + 64, by + 58], start=10, end=170,
          fill=(255, 255, 255), width=3)
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(40, 48, 60))
    d.rectangle([x + 6, y + h - 52, x + 38, y + h - 26], fill=(70, 80, 96))
    d.rectangle([x + w - 44, y + h - 58, x + w - 8, y + h - 26],
                fill=(70, 80, 96))
    for wy in range(y + h - 46, y + h - 28, 10):
        d.rectangle([x + 12, wy, x + 32, wy + 5], fill=(250, 220, 160))
        d.rectangle([x + w - 38, wy, x + w - 14, wy + 5], fill=(250, 220, 160))
    if labels:
        d.text((x + 8, y + h - 16), "SAT 28 NOV \u00b7 8:30 A.M.",
               font=SANS_B(8), fill=(255, 255, 255))


def art_nukes(d, x, y, w, h, labels=True):
    """Night sky, rows of warhead silhouettes, red moon."""
    d.rectangle([x, y, x + w, y + h], fill=(22, 35, 58))
    d.ellipse([x + w - 72, y + 6, x + w - 14, y + 64], fill=(178, 34, 34))
    for sx, sy in [(24, 18), (96, 12), (170, 20), (240, 14), (70, 28),
                   (210, 30)]:
        d.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2],
                  fill=(200, 210, 230))
    d.polygon([(x, y + h), (x + 52, y + h - 34), (x + 104, y + h),
               (x + 156, y + h - 24), (x + 208, y + h), (x + w, y + h - 14),
               (x + w, y + h), (x, y + h)], fill=(12, 20, 34))
    for i in range(7):
        mx = x + 18 + i * 40
        mh = 52 + (i % 3) * 10
        my = y + h - 22 - mh
        d.rectangle([mx, my + 12, mx + 11, y + h - 22],
                    fill=(220, 222, 226))
        d.polygon([(mx, my + 14), (mx + 5, my), (mx + 11, my + 14)],
                  fill=(220, 222, 226))
        d.rectangle([mx - 3, y + h - 26, mx + 14, y + h - 20],
                    fill=(90, 96, 104))
        d.ellipse([mx + 3, my + 20, mx + 8, my + 25], fill=(178, 34, 34))
    if labels:
        d.text((x + 10, y + 6), "HWASAN-31 \u00b7 TACTICAL WARHEADS",
               font=SANS_B(8), fill=(255, 255, 255))


def art_drone(d, x, y, w, h, labels=True):
    """Dusk over a Gulf skyline: blast burst, drone silhouette."""
    d.rectangle([x, y, x + w, y + h], fill=(214, 138, 74))
    d.rectangle([x, y, x + w, y + 30], fill=(232, 178, 120))
    d.ellipse([x + w - 62, y + 4, x + w - 14, y + 52], fill=(250, 220, 160))
    base = y + h - 16
    for i, (bw, bh) in enumerate([(24, 46), (16, 66), (28, 40), (14, 56),
                                  (22, 34)]):
        bx = x + 10 + i * 54
        d.rectangle([bx, base - bh, bx + bw, base], fill=(90, 52, 44))
        for wy in range(base - bh + 8, base - 6, 12):
            d.rectangle([bx + 4, wy, bx + bw - 4, wy + 5],
                        fill=(250, 220, 160))
    d.rectangle([x, base, x + w, y + h], fill=(70, 40, 36))
    cx, cy = x + 56, y + 26
    import math
    for r, col in ((24, (255, 200, 60)), (16, (255, 120, 30)),
                   (9, (255, 240, 200))):
        pts = []
        for k in range(12):
            a = math.radians(k * 30)
            rr = r if k % 2 == 0 else r * 0.55
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        d.polygon(pts, fill=col)
    dx, dy = x + w - 88, y + 66
    d.ellipse([dx - 20, dy - 4, dx + 20, dy + 4], fill=(30, 30, 30))
    d.rectangle([dx - 5, dy - 8, dx + 5, dy + 8], fill=(30, 30, 30))
    d.ellipse([dx - 28, dy - 8, dx - 11, dy - 2], outline=(30, 30, 30),
              width=2)
    d.ellipse([dx + 11, dy - 8, dx + 28, dy - 2], outline=(30, 30, 30),
              width=2)


def art_markets(d, x, y, w, h, labels=True):
    """Green bars climbing, red line falling away beneath them."""
    d.rectangle([x, y, x + w, y + h], fill=(214, 240, 222))
    for gy in range(5):
        yy = y + 10 + gy * (h - 20) // 4
        d.line([x + 6, yy, x + w - 6, yy], fill=(190, 215, 198), width=1)
    bars = [(26, 30), (62, 46), (98, 40), (134, 66), (170, 58), (206, 86),
            (242, 78)]
    for bx, bh in bars:
        d.rectangle([x + bx, y + h - 12 - bh, x + bx + 24, y + h - 12],
                    fill=(20, 120, 70) if bh > 56 else (46, 160, 100))
    d.line([(x + 26, y + h - 42), (x + 88, y + h - 58),
            (x + 140, y + h - 76), (x + 200, y + h - 84),
            (x + 260, y + h - 100)], fill=(123, 30, 30), width=3)
    d.polygon([(x + 260, y + h - 100), (x + 249, y + h - 94),
               (x + 257, y + h - 86)], fill=(123, 30, 30))
    if labels:
        d.text((x + 10, y + 6),
               "KOSPI +1.88%  \u00b7  NIKKEI +1.85%  \u00b7  TAIEX +3.05%",
               font=SANS_B(8), fill=(20, 90, 50))


def art_storm(d, x, y, w, h, labels=True):
    """Dark clouds, city rooftops, slanted rain, wind arc."""
    d.rectangle([x, y, x + w, y + h], fill=(52, 74, 96))
    d.ellipse([x + 14, y + 4, x + 104, y + 40], fill=(38, 54, 72))
    d.ellipse([x + 70, y, x + 160, y + 34], fill=(44, 62, 82))
    d.ellipse([x + 130, y + 8, x + 220, y + 42], fill=(38, 54, 72))
    d.ellipse([x + 200, y + 2, x + 280, y + 36], fill=(44, 62, 82))
    for bx, bw, bh in [(8, 30, 52), (42, 22, 74), (68, 26, 58),
                       (98, 20, 80), (122, 32, 50), (158, 22, 68),
                       (184, 26, 56), (214, 24, 76), (242, 30, 48)]:
        d.rectangle([x + bx, y + h - bh, x + bx + bw, y + h],
                    fill=(24, 34, 46))
    for wx in (52, 104, 156, 208, 260):
        for wy in (50, 72, 94):
            d.line([x + wx, y + wy, x + wx - 7, y + wy + 12],
                   fill=(180, 200, 220), width=2)
    d.arc([x + w - 60, y + h - 46, x + w - 6, y + h - 2], 200, 340,
          fill=(255, 255, 255), width=3)


def art_chess(d, x, y, w, h, labels=True):
    """Chessboard corner, two kings facing off, clock running down."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 220, 196))
    sq = min(w, h) // 8
    ox, oy = x + (w - sq * 8) // 2, y + (h - sq * 8) // 2
    for r in range(8):
        for c in range(8):
            if (r + c) % 2:
                d.rectangle([ox + c * sq, oy + r * sq,
                             ox + (c + 1) * sq, oy + (r + 1) * sq],
                            fill=(120, 90, 60))
    d.rectangle([ox, oy, ox + sq * 8, oy + sq * 8], outline=(60, 45, 30),
                width=2)
    # white king on d4, black king on f6 (schematic crowns)
    for kx, ky, col in ((ox + 3 * sq, oy + 4 * sq, (255, 255, 255)),
                        (ox + 5 * sq, oy + 2 * sq, (30, 30, 30))):
        d.polygon([(kx + 3, ky + sq - 4), (kx + 3, ky + 6),
                   (kx + sq // 2, ky + 12), (kx + sq - 3, ky + 6),
                   (kx + sq - 3, ky + sq - 4)], fill=col,
                  outline=(60, 45, 30))
        d.ellipse([kx + sq // 2 - 2, ky + 2, kx + sq // 2 + 2, ky + 6],
                  fill=col, outline=(60, 45, 30))
    if labels:
        d.text((x + 8, y + h - 14), "1.5 \u2013 1.5 \u00b7 60 MOVES",
               font=SANS_B(8), fill=(24, 24, 24))


def art_memorial(d, x, y, w, h, labels=True):
    """Candles and marigolds before a dark memorial wall."""
    d.rectangle([x, y, x + w, y + h], fill=(40, 44, 60))
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(24, 26, 36))
    for i, cx in enumerate((34, 96, 158, 220, 268)):
        d.rectangle([x + cx - 5, y + h - 52, x + cx + 5, y + h - 14],
                    fill=(240, 236, 220))
        d.ellipse([x + cx - 6, y + h - 64, x + cx + 6, y + h - 50],
                  fill=(255, 200, 60))
        d.ellipse([x + cx - 3, y + h - 61, x + cx + 3, y + h - 53],
                  fill=(255, 240, 180))
    for fx in (60, 130, 200, 250):
        d.ellipse([x + fx - 7, y + h - 26, x + fx + 7, y + h - 12],
                  fill=(230, 126, 34))
        d.ellipse([x + fx - 3, y + h - 22, x + fx + 3, y + h - 16],
                  fill=(255, 200, 60))
    if labels:
        d.text((x + 8, y + 6), "MUMBAI \u00b7 18 YEARS \u00b7 166 LIVES",
               font=SANS_B(8), fill=(255, 255, 255))


def art_refinery(d, x, y, w, h, labels=True):
    """Refinery stacks at dusk, flame on the far stack."""
    d.rectangle([x, y, x + w, y + h], fill=(248, 196, 120))
    d.rectangle([x, y + h - 10, x + w, y + h], fill=(90, 60, 30))
    for tx, th in [(14, 18), (46, 14), (78, 22), (110, 16), (140, 20)]:
        top = y + h - 10 - th
        d.rectangle([x + tx, top, x + tx + 14, y + h - 10],
                    fill=(70, 70, 78))
        d.rectangle([x + tx + 4, top - 5, x + tx + 10, top],
                    fill=(70, 70, 78))
        d.ellipse([x + tx + 2, top - 12, x + tx + 12, top - 2],
                  fill=(230, 230, 230))
    d.polygon([(x + w - 30, y + 6), (x + w - 19, y + 20),
               (x + w - 8, y + 6), (x + w - 14, y + 26),
               (x + w - 26, y + 26)], fill=(230, 120, 20))
    d.polygon([(x + w - 25, y + 22), (x + w - 19, y + 34),
               (x + w - 13, y + 22)], fill=(255, 200, 40))


def art_tides(d, x, y, w, h, labels=True):
    """Breaking waves over a pier, red-roofed houses behind."""
    d.rectangle([x, y, x + w, y + h], fill=(183, 219, 238))
    d.rectangle([x, y, x + w, y + 14], fill=(240, 244, 248))
    d.polygon([(x, y + h), (x + 52, y + 16), (x + 114, y + h)],
              fill=(46, 134, 193))
    d.polygon([(x + 52, y + h), (x + 114, y + 16), (x + 170, y + h)],
              fill=(31, 110, 170))
    d.arc([x + 84, y + 8, x + 132, y + 34], 180, 360, fill=(255, 255, 255),
          width=3)
    d.rectangle([x + 12, y + 22, x + 48, y + 34], fill=(140, 90, 50))
    d.polygon([(x + 8, y + 22), (x + 30, y + 12), (x + 52, y + 22)],
              fill=(123, 30, 30))
    d.rectangle([x + 132, y + 26, x + 160, y + 36], fill=(140, 90, 50))
    d.polygon([(x + 128, y + 26), (x + 146, y + 16), (x + 164, y + 26)],
              fill=(123, 30, 30))


def art_nfl(d, x, y, w, h, labels=True):
    """Green field, yard lines, a football at midfield."""
    d.rectangle([x, y, x + w, y + h], fill=(46, 139, 87))
    for i in range(5):
        yy = y + 6 + i * (h - 12) // 4
        d.line([x, yy, x + w, yy], fill=(255, 255, 255), width=1)
    d.line([x + 16, y + 4, x + 16, y + h - 4], fill=(255, 214, 0), width=3)
    d.line([x + w - 16, y + 4, x + w - 16, y + h - 4], fill=(255, 214, 0),
           width=3)
    d.ellipse([x + w // 2 - 30, y + h // 2 - 11, x + w // 2 + 30,
               y + h // 2 + 11], fill=(139, 90, 43))
    d.line([x + w // 2 - 21, y + h // 2, x + w // 2 + 21, y + h // 2],
           fill=(255, 255, 255), width=2)
    for lx in (-10, -3, 3, 10):
        d.line([x + w // 2 + lx, y + h // 2 - 4, x + w // 2 + lx,
                y + h // 2 + 4], fill=(255, 255, 255), width=2)


def art_aid(d, x, y, w, h, labels=True):
    """Aid trucks in convoy under a pale sky."""
    d.rectangle([x, y, x + w, y + h], fill=(214, 232, 240))
    for tx in (10, 70, 130):
        d.rectangle([x + tx, y + 18, x + tx + 36, y + 32],
                    fill=(255, 255, 255))
        d.rectangle([x + tx + 36, y + 22, x + tx + 46, y + 32],
                    fill=(220, 222, 226))
        d.rectangle([x + tx + 12, y + 22, x + tx + 24, y + 30],
                    fill=(178, 34, 34))
        d.ellipse([x + tx + 7, y + 32, x + tx + 14, y + 39],
                  fill=(26, 26, 26))
        d.ellipse([x + tx + 32, y + 32, x + tx + 39, y + 39],
                  fill=(26, 26, 26))
    d.polygon([(x + 130, y + h - 4), (x + 150, y + h - 20),
               (x + 170, y + h - 4)], fill=(240, 240, 230))
    d.polygon([(x + 18, y + h - 4), (x + 36, y + h - 16),
               (x + 54, y + h - 4)], fill=(240, 240, 230))
    for rx in (26, 78, 130, 158):
        d.line([x + rx, y + 6, x + rx - 3, y + 14], fill=(100, 140, 180),
               width=2)


def art_court(d, x, y, w, h, labels=True):
    """Courthouse portico: pediment, columns, steps."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 226, 210))
    d.polygon([(x + 18, y + 8), (x + w // 2, y + 2), (x + w - 18, y + 8)],
              fill=(140, 120, 90))
    for cx in (26, 58, 90, 122, 150):
        d.rectangle([x + cx, y + 12, x + cx + 9, y + h - 10],
                    fill=(255, 255, 255))
    d.rectangle([x + 10, y + h - 10, x + w - 10, y + h - 5],
                fill=(140, 120, 90))
    d.rectangle([x + 74, y + 22, x + 86, y + h - 10], fill=(60, 60, 66))


def art_oil(d, x, y, w, h, labels=True):
    """Pumpjack, gold barrels and a drum on sand."""
    d.rectangle([x, y, x + w, y + h], fill=(250, 226, 160))
    d.polygon([(x + 18, y + h - 6), (x + 40, y + 4), (x + 62, y + h - 6)],
              fill=(40, 40, 40))
    d.line([x + 29, y + h - 6, x + 45, y + 10], fill=(40, 40, 40), width=2)
    d.line([x + 51, y + h - 6, x + 34, y + 10], fill=(40, 40, 40), width=2)
    d.ellipse([x + 106, y + h - 36, x + 132, y + h - 26],
              fill=(201, 162, 39))
    d.ellipse([x + 106, y + h - 26, x + 132, y + h - 16],
              fill=(230, 190, 60))
    d.rectangle([x + 140, y + h - 22, x + 162, y + h - 6],
                fill=(60, 60, 66))
    d.rectangle([x + 140, y + h - 28, x + 162, y + h - 22],
                fill=(40, 40, 44))


ARTS = {
    "parade": art_parade, "nukes": art_nukes, "drone": art_drone,
    "markets": art_markets, "storm": art_storm, "chess": art_chess,
    "memorial": art_memorial, "refinery": art_refinery, "tides": art_tides,
    "nfl": art_nfl, "aid": art_aid, "court": art_court, "oil": art_oil,
}


# ---------------------------------------------------------------- map


def on_land(lat, lon):
    for la0, la1, lo0, lo1 in LAND_BOXES:
        if la0 <= lat <= la1 and lo0 <= lon <= lo1:
            return True
    return False


def render_art(name, w, h):
    """Render one illustration into a box of exactly (w, h).

    The art is drawn once at design size (300x120), then scaled to fill
    the box and centre-cropped, so nothing ever spills over the box edge
    the way fixed coordinates would in a short tile. In-art captions are
    left out: the tile's own headline and body carry the story.
    """
    tmp = Image.new("RGB", (300, 120), (255, 255, 255))
    td = ImageDraw.Draw(tmp)
    ARTS[name](td, 0, 0, 300, 120, labels=False)
    scale = max(w / 300, h / 120)
    rw, rh = int(round(300 * scale)), int(round(120 * scale))
    tmp = tmp.resize((rw, rh), Image.LANCZOS)
    ox, oy = (rw - w) // 2, (rh - h) // 2
    return tmp.crop((ox, oy, ox + w, oy + h))


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    cell = 6
    for gy in range(h // cell):
        for gx in range(w // cell):
            lon = -180 + (gx + 0.5) * cell / w * 360
            lat = 90 - (gy + 0.5) * cell / h * 180
            if on_land(lat, lon):
                cx = x + gx * cell + 2
                cy = y + gy * cell + 2
                d.ellipse([cx, cy, cx + 2, cy + 2], fill=(90, 110, 130))
    for name, lat, lon, side in PINS:
        px = x + int((lon + 180) / 360 * w)
        py = y + int((90 - lat) / 180 * h)
        d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=RED,
                  outline=(255, 255, 255))
        d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(255, 255, 255))
        lw = d.textlength(name, font=F_PIN)
        if side == "L":
            lx = max(x + 1, px - 6 - lw)
            ly = py - 9
        elif side == "B":
            lx = px + 6
            ly = py + 6
        else:  # "R"
            lx = px + 6
            ly = py - 9
        d.text((lx, ly), name, font=F_PIN, fill=INK)


# ---------------------------------------------------------------- build


def build():
    img = Image.new("RGBA", (W, H), PAPER + (255,))
    speckle(img)
    d = ImageDraw.Draw(img)
    mx = MARGIN
    cw = W - 2 * mx

    # ---- masthead
    date = "THURSDAY 26 NOVEMBER 2026"
    dw = d.textlength(date, font=F_DATE)
    d.text(((W - dw) / 2, 8), date, font=F_DATE, fill=INK)
    tag = "ONE DAY OF WORLD NEWS, ONE PICTURE"
    tw = d.textlength(tag, font=F_TAG)
    d.line([mx + 40, 56, (W - tw) / 2 - 14, 56], fill=RED, width=2)
    d.line([(W + tw) / 2 + 14, 56, W - mx - 40, 56], fill=RED, width=2)
    d.text(((W - tw) / 2, 48), tag, font=F_TAG, fill=RED)
    regions = sorted({s["region"] for s in LEADS + TILES} |
                     {r for _, _, r, _, _ in INDEX})
    fields = sorted({s["field"] for s in LEADS + TILES} |
                    {f for _, _, _, f, _ in INDEX})
    total = len(LEADS) + len(TILES) + len(INDEX)
    counts = (f"{total} STORIES \u00b7 {len(regions)} REGIONS \u00b7 "
              f"{len(fields)} FIELDS \u00b7 EVERY ONE FROM THIS THURSDAY")
    cwdt = d.textlength(counts, font=F_COUNTS)
    d.text(((W - cwdt) / 2, 66), counts, font=F_COUNTS, fill=INK)
    d.line([mx, 82, W - mx, 82], fill=INK, width=2)

    # ---- UTC strip
    y = 88
    d.text((mx, y), "THE DAY IN UTC", font=F_SEC, fill=RED)
    y += 14
    col_w = (cw - 6 * 6) / 7
    for i, (t, ev) in enumerate(UTC_EVENTS):
        cx = mx + i * (col_w + 6)
        d.text((cx, y), t, font=F_UTC_T, fill=NAVY)
        draw_wrapped(d, cx, y + 12, ev, F_UTC, col_w, leading=10)
        if i < 6:
            d.line([cx + col_w + 3, y, cx + col_w + 3, y + 34],
                   fill=FAINT, width=1)
    d.line([mx, 132, W - mx, 132], fill=FAINT, width=1)

    # ---- numbers strip
    y = 138
    d.text((mx, y), "THE DAY IN NUMBERS", font=F_SEC, fill=RED)
    y += 14
    cell_w = (cw - 5 * 6) / 6
    for i, (num, lab) in enumerate(NUMBERS):
        cx = mx + i * (cell_w + 6)
        nf = shrink_to_fit(d, num, "DejaVuSans-Bold.ttf", 19, cell_w,
                           floor=13)
        d.text((cx, y), num, font=nf, fill=NAVY)
        draw_wrapped(d, cx, y + 22, lab, F_NUM_L, cell_w, fill=GREY,
                     leading=10)
    d.line([mx, 176, W - mx, 176], fill=INK, width=2)

    # ---- leads
    y0 = 184
    lead_w = (cw - 2 * 10) / 3
    illo_h = 122
    for i, lead in enumerate(LEADS):
        lx = mx + i * (lead_w + 10)
        d.rectangle([lx, y0, lx + lead_w, y0 + 30], fill=lead["banner_bg"])
        bf = shrink_to_fit(d, lead["banner"], "DejaVuSans-Bold.ttf", 19,
                           lead_w - 12, floor=12)
        bw = d.textlength(lead["banner"], font=bf)
        d.text((lx + (lead_w - bw) / 2, y0 + 5), lead["banner"], font=bf,
               fill=(255, 255, 255))
        iy = y0 + 30
        ARTS[lead["art"]](d, int(lx), iy, int(lead_w), illo_h)
        hy = iy + illo_h + 8
        hy = draw_wrapped(d, int(lx), hy, lead["headline"], F_LEAD_H,
                          lead_w, leading=18)
        hy += 2
        draw_wrapped(d, int(lx), hy, lead["body"], F_LEAD_B, lead_w,
                     leading=14, max_lines=3)
        by = y0 + 30 + illo_h + 8 + 36 + 56
        bw2 = badge(d, int(lx), int(by), lead["badge"])
        reg = f"{lead['region'].upper()} \u00b7 {lead['field'].upper()}"
        d.text((lx + bw2 + 8, by + 2), reg, font=F_BADGE, fill=GREY)
    leads_bottom = y0 + 30 + illo_h + 8 + 36 + 56 + 13

    # ---- tiles (5 x 2)
    ty0 = leads_bottom + 6
    tile_w = (cw - 4 * 8) / 5
    tile_h = 116
    for i, tile in enumerate(TILES):
        row, col = divmod(i, 5)
        tx = mx + col * (tile_w + 8)
        ty = ty0 + row * (tile_h + 6)
        img.paste(render_art(tile["art"], int(tile_w), 50),
                  (int(tx), int(ty)))
        hy = draw_wrapped(d, int(tx), int(ty + 54), tile["headline"],
                          F_TILE_H, tile_w, leading=12, max_lines=2)
        draw_wrapped(d, int(tx), int(hy + 2), tile["body"], F_TILE_B,
                     tile_w, fill=(60, 60, 60), leading=11, max_lines=2)
        badge(d, int(tx), int(ty + tile_h - 13), tile["badge"])
    tiles_bottom = ty0 + 2 * tile_h + 6

    # ---- bottom band: map + index
    by0 = tiles_bottom + 6
    d.line([mx, by0 - 4, W - mx, by0 - 4], fill=INK, width=2)
    map_w = 286
    map_x = mx
    idx_x = mx + map_w + 8
    idx_w = W - mx - idx_x
    d.text((map_x, by0), "WHERE IT HAPPENED", font=F_SEC, fill=RED)
    d.text((idx_x, by0),
           f"THE DAY IN BRIEF \u2014 {len(INDEX)} MORE STORIES",
           font=F_SEC, fill=RED)
    my = by0 + 16
    map_h = 956 - my
    draw_map(d, map_x, my, map_w, map_h)
    cols = 3
    per_col = (len(INDEX) + cols - 1) // cols
    col_w = (idx_w - 2 * 10) / cols
    row_h = (956 - (by0 + 16)) / per_col
    for ci in range(cols):
        cx = idx_x + ci * (col_w + 10)
        for ri in range(per_col):
            k = ci * per_col + ri
            if k >= len(INDEX):
                break
            head, fact, region, field, bdg = INDEX[k]
            ry = by0 + 16 + ri * row_h
            d.ellipse([cx, ry + 2, cx + 6, ry + 8],
                      fill=REGION_COLORS[region])
            tx = cx + 10
            hf = shrink_to_fit(d, head, "DejaVuSans-Bold.ttf", 9,
                               col_w - 10, floor=7)
            d.text((tx, ry), head, font=hf, fill=INK)
            ff = shrink_to_fit(d, fact, "DejaVuSans.ttf", 8, col_w - 10,
                               floor=7)
            d.text((tx, ry + 9), fact, font=ff, fill=GREY)

    # ---- date check
    dy = 962
    d.rectangle([mx, dy, W - mx, 1018], outline=INK, width=1, fill=PANEL)
    d.text((mx + 10, dy + 6),
           "DATE CHECK \u2014 WHAT WE LEFT OUT, AND WHAT HAS NOT HAPPENED YET",
           font=F_DC_T, fill=RED)
    ty = dy + 20
    ty = draw_wrapped(d, mx + 10, ty, "NOT THIS DAY: " + DATE_CHECK_OUT,
                      F_DC, W - 2 * mx - 20, leading=11)
    ty = draw_wrapped(d, mx + 10, ty + 1, "NOT YET: " + DATE_CHECK_NOT_YET,
                      F_DC, W - 2 * mx - 20, leading=11)
    draw_wrapped(d, mx + 10, ty + 1, DATE_CHECK_COUNTED, F_DC,
                 W - 2 * mx - 20, leading=11)

    return img.convert("RGB")


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    build().save(out, "PNG", optimize=True)
    print("saved", out)
