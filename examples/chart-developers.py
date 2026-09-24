#!/usr/bin/env python3
"""Why the screen works: developers of the same age and kind land far apart."""
import json, math, pathlib, sys
import plate
from plate import INK, INK2, MUTED, RULE, GRID, FAINT

W = 880
COOK, AR, OTHER = "#2f6f5e", "#c08a3e", "#3f3f8f"
KINDS = (("Energy Efficiency - Domestic", COOK, "cookstoves & domestic efficiency"),
         ("A/R", AR, "afforestation / reforestation"),
         (None, OTHER, "everything else"))


def main():
    here = pathlib.Path(__file__).resolve()
    src = (sys.argv[1] if len(sys.argv) > 1 else
           str(sorted((here.parents[1] / "public").glob("certification-*.json"))[-1]))
    d = json.load(open(src))
    D = [x for x in d["developers"] if x["n"] >= 5]
    floor = [x for x in D if x["rate"] == 0]

    PL, PR, PH = 76, W - 232, 330
    s = plate.open_svg(W, 10,
        f"{len(floor)} of these {len(D)} developers have never certified anything.",
        # open_svg does not wrap the subtitle; an earlier one ran off the canvas.
        subtitle=f"One developer per mark, {len(D)} with five or more projects. Age across, "
                 f"share of the portfolio certified up, portfolio size as area.")
    f, y = plate.frame(W, 88,
        who="A buyer deciding how much weight to put on the developer rather than the project",
        decide="Whether to treat two projects of the same kind and vintage as interchangeable",
        wrong="The marks form a tight band at each age — then the developer carries no information "
              "that age does not already give")
    s += f
    top = y + 28; bot = top + PH
    ages = [x["median_age"] for x in D]
    ax0, ax1 = 0, max(ages) * 1.06
    X = lambda v: PL + (PR - PL) * (v - ax0) / (ax1 - ax0)
    Y = lambda v: bot - PH * v

    for v in range(0, 101, 20):
        s.append(f'<line x1="{PL}" y1="{Y(v/100):.1f}" x2="{PR}" y2="{Y(v/100):.1f}" stroke="{GRID}"/>')
        s.append(plate.txt(PL - 10, Y(v/100) + 3.5, v, size=10, fill=MUTED, anchor="end"))
    yr = 0
    while yr <= ax1:
        s.append(f'<line x1="{X(yr):.1f}" y1="{top}" x2="{X(yr):.1f}" y2="{bot+5:.1f}" stroke="{GRID}"/>')
        s.append(plate.txt(X(yr), bot + 20, yr, size=10, fill=MUTED, anchor="middle"))
        yr += 1
    s.append(f'<line x1="{PL}" y1="{top}" x2="{PL}" y2="{bot}" stroke="{RULE}"/>')
    s.append(f'<line x1="{PL}" y1="{bot}" x2="{PR}" y2="{bot}" stroke="{RULE}"/>')
    s.append(plate.txt(PL, top - 12, "% OF THE DEVELOPER'S PORTFOLIO CERTIFIED", size=8.5,
                       fill=MUTED, weight="700", spacing="0.9"))
    s.append(plate.txt(PR, bot + 36, "MEDIAN AGE OF THEIR PROJECTS, YEARS", size=8.5, fill=MUTED,
                       anchor="end", weight="700", spacing="0.9"))

    # Area, not radius, carries the portfolio size: radius would overstate a large
    # portfolio by the square of its lead.
    nmax = max(x["n"] for x in D)
    rad = lambda n: 4.0 + 13.0 * math.sqrt(n / nmax)
    kind = lambda t: next(c for k, c, _ in KINDS if k is None or k == t)
    for x in sorted(D, key=lambda x: -x["n"]):
        s.append(f'<circle cx="{X(x["median_age"]):.1f}" cy="{Y(x["rate"]):.1f}" '
                 f'r="{rad(x["n"]):.1f}" fill="{kind(x["top_type"])}" fill-opacity="0.55" '
                 f'stroke="{plate.SURFACE}" stroke-width="2"/>')

    lx = PR + 26
    s.append(plate.txt(lx, top + 2, "DOMINANT PROJECT KIND", size=8.5, fill=MUTED,
                       weight="700", spacing="0.9"))
    for i, (_, col, lab) in enumerate(KINDS):
        yy = top + 24 + i * 34
        s.append(f'<circle cx="{lx+7:.1f}" cy="{yy:.1f}" r="7" fill="{col}" fill-opacity="0.55" '
                 f'stroke="{plate.SURFACE}" stroke-width="2"/>')
        s += plate.wrap(lx + 20, yy + 4, lab, size=9.5, fill=MUTED, chars=20, leading=11)
    ly = top + 24 + 3 * 34 + 16
    s.append(plate.txt(lx, ly, "PORTFOLIO SIZE", size=8.5, fill=MUTED, weight="700", spacing="0.9"))
    for i, n in enumerate((5, 40, nmax)):
        yy = ly + 26 + i * 30
        s.append(f'<circle cx="{lx+18:.1f}" cy="{yy:.1f}" r="{rad(n):.1f}" fill="none" '
                 f'stroke="{MUTED}" stroke-width="1.2"/>')
        s += plate.halo(lx + 42, yy + 4, f"{n} projects", size=9.5, fill=MUTED)

    s.append(f'<line x1="{PL}" y1="{Y(0):.1f}" x2="{PR}" y2="{Y(0):.1f}" stroke="{AR}" '
             f'stroke-width="1.4" stroke-dasharray="5 4" opacity="0.8"/>')
    s += plate.halo(PL + 8, Y(0) - 10, f"{len(floor)} developers sit on this line", size=10, fill=AR)

    sy = bot + 56
    s += plate.halo(28, sy, "At every age, the spread runs the full height of the chart.",
                    size=12.5, fill=INK)
    body = plate.wrap(28, sy + 19,
        f"That vertical spread is what the screen is reading. It is not the project kind — the "
        f"colours are mixed at every height — and it is not portfolio size, which correlates with "
        f"the certification rate at only r=+0.26. Median project AGE is the real confound at "
        f"r=+0.54, which is why it is on the horizontal axis and why every score in this repo is "
        f"matched on it. What is left after age is the developer, and it is worth more than the "
        f"project type and the age put together. Estimated annual credits are drawn nowhere here: "
        f"against the certification rate they sit at r=-0.02.",
        size=10.5, fill=MUTED, chars=126, leading=13)
    s += body
    fy = sy + 19 + len(body) * 13 + 30
    foot = plate.wrap(28, fy + 16,
        f"Gold Standard registry, captured {d['observed']}; developers with at least five projects "
        f"listed on or after {d['cutoff'][:4]}. Unlike the screening plate, the rates here are PLAIN "
        f"PORTFOLIO RATES and include the developer's own projects — this plate describes the spread "
        f"that exists, it does not score anything, and nothing downstream reads it. The leave-one-out "
        f"scores are built in certification_model.py and used only there. A developer at exactly 0% "
        f"or exactly 100% with five projects is a small sample, which is why the mark carries the "
        f"portfolio size and why {len(floor)} on the floor is reported as a count rather than a rate.",
        size=10, fill=MUTED, chars=134, leading=13)
    s.append(f'<line x1="28" y1="{fy:.1f}" x2="{W-28}" y2="{fy:.1f}" stroke="{RULE}"/>')
    s += foot
    H = int(fy + 16 + len(foot) * 13 + 14)
    s.append("</svg>")
    svg = ("\n".join(s).replace('height="10"', f'height="{H}"')
                       .replace(f'viewBox="0 0 {W} 10"', f'viewBox="0 0 {W} {H}"'))
    assert 'height="10"' not in svg
    out = here.parent / "charts" / "developers.svg"
    out.write_text(svg, encoding="utf-8")
    print(f"  wrote {out.name}  {len(D)} developers, {len(floor)} at zero")
    return 0


if __name__ == "__main__":
    sys.exit(main())
