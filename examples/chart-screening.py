#!/usr/bin/env python3
"""What a buyer gets by screening listed projects on the developer's record."""
import json, pathlib, sys
import plate
from plate import INK, INK2, MUTED, RULE, GRID, FAINT

W = 880
# Validated, not chosen by eye: OKLab dE on normal vision 23/18/35 (floor 15) and
# 14.8 under the worse of deuteranopia and protanopia (target 8). An earlier blue
# sat at 10.0 against the green and would have failed full-colour readers.
DEV, TYP, AGE = "#2f6f5e", "#c08a3e", "#3f3f8f"
SERIES = (("age+type+developer", DEV, "+ who develops it"),
          ("age+type",           TYP, "+ what kind of project"),
          ("age",                AGE, "age of the listing alone"))
FLOOR = 0.05          # below this the screened set is under 25 projects


def main():
    here = pathlib.Path(__file__).resolve()
    src = (sys.argv[1] if len(sys.argv) > 1 else
           str(sorted((here.parents[1] / "public").glob("certification-*.json"))[-1]))
    d = json.load(open(src))
    n = d["holdout_n"]; base = d["holdout_base"]

    PL, PR = 76, W - 188
    # The y-axis starts at 40, not 0. Every curve ends at the 47.3% base rate and
    # none goes below it, so a zero baseline spends 40% of the plot on empty space.
    # The dashed base-rate rule is drawn so the truncation cannot mislead: the
    # reader can see where "no screen at all" sits.
    Y0, PH = 0.40, 300
    s = plate.open_svg(W, 10,
        "Screen on who develops it, and 96% of what you pick certifies.",
        subtitle=f"Held-out test of {n} listed projects. Rank them by each model, take the best "
                 f"share, and read off how many of those reached full certification.")
    f, y = plate.frame(W, 88,
        who="Someone buying forward credits from a project that is only LISTED",
        decide="Which listed projects to shortlist, and what to rank them on",
        wrong="The three curves converge — then ranking adds nothing over taking projects at random")
    s += f
    top = y + 28
    bot = top + PH
    X = lambda p: PL + (PR - PL) * (p - FLOOR) / (1 - FLOOR)
    Y = lambda v: bot - PH * (v - Y0) / (1 - Y0)

    for v in range(40, 101, 10):
        s.append(f'<line x1="{PL}" y1="{Y(v/100):.1f}" x2="{PR}" y2="{Y(v/100):.1f}" stroke="{GRID}"/>')
        s.append(plate.txt(PL - 10, Y(v/100) + 3.5, v, size=10, fill=MUTED, anchor="end"))
    for p in (0.05, 0.2, 0.4, 0.6, 0.8, 1.0):
        s.append(f'<line x1="{X(p):.1f}" y1="{top}" x2="{X(p):.1f}" y2="{bot+5:.1f}" stroke="{GRID}"/>')
        s.append(plate.txt(X(p), bot + 20, int(p*100), size=10, fill=MUTED, anchor="middle"))
    s.append(f'<line x1="{PL}" y1="{top}" x2="{PL}" y2="{bot}" stroke="{RULE}"/>')
    s.append(f'<line x1="{PL}" y1="{bot}" x2="{PR}" y2="{bot}" stroke="{RULE}"/>')
    s.append(plate.txt(PL, top - 12, "% OF THE SHORTLIST THAT CERTIFIED", size=8.5, fill=MUTED,
                       weight="700", spacing="0.9"))
    s.append(plate.txt(PR, bot + 36, "% OF LISTED PROJECTS SHORTLISTED", size=8.5, fill=MUTED,
                       anchor="end", weight="700", spacing="0.9"))

    # no screen at all: the base rate. Every curve must end here at 100%.
    s.append(f'<line x1="{PL}" y1="{Y(base):.1f}" x2="{PR}" y2="{Y(base):.1f}" '
             f'stroke="{MUTED}" stroke-width="1.3" stroke-dasharray="5 4"/>')
    s += plate.halo(PL + 6, Y(base) - 8, f"no screen — {base*100:.1f}% of all listed projects certify",
                    size=10, fill=MUTED)

    ends = []
    for key, col, lab in SERIES:
        pts = [(X(k/n), Y(v)) for k, v in enumerate(d["lift"][key], 1) if k/n >= FLOOR]
        s.append(f'<polyline fill="none" stroke="{col}" stroke-width="2" stroke-linejoin="round" '
                 f'points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}"/>')
        k20 = max(1, int(n * 0.20)) - 1
        v20 = d["lift"][key][k20]
        s.append(f'<circle cx="{X(0.2):.1f}" cy="{Y(v20):.1f}" r="5" fill="{col}" '
                 f'stroke="{plate.SURFACE}" stroke-width="1.8"/>')
        ends.append((Y(v20), col, lab, v20))

    # Direct labels at the 20% mark, nudged apart. Identity is never colour alone.
    ends.sort()
    for i in range(1, len(ends)):
        if ends[i][0] - ends[i-1][0] < 30:
            ends[i] = (ends[i-1][0] + 30,) + ends[i][1:]
    for yy, col, lab, v in ends:
        s.append(f'<line x1="{X(0.2)+7:.1f}" y1="{Y(v):.1f}" x2="{PR+14:.1f}" y2="{yy:.1f}" '
                 f'stroke="{FAINT}" stroke-width="1"/>')
        s += plate.halo(PR + 20, yy - 2, f"{v*100:.0f}%", size=13, fill=col, weight="700")
        s += plate.wrap(PR + 20, yy + 12, lab, size=9.5, fill=MUTED, chars=22, leading=11)

    sy = bot + 58
    d20 = d["lift"]["age+type+developer"][max(1, int(n*0.20))-1]
    a20 = d["lift"]["age"][max(1, int(n*0.20))-1]
    s += plate.halo(28, sy, "The developer's record is worth more than the project type and the "
                            "listing's age put together.", size=12.5, fill=INK)
    body = plate.wrap(28, sy + 19,
        f"Shortlisting the best fifth on age alone gives {a20*100:.0f}% certified; adding what kind of "
        f"project it is gives {d['lift']['age+type'][max(1,int(n*0.20))-1]*100:.0f}%; adding the "
        f"developer's own record gives {d20*100:.0f}%, against {base*100:.1f}% with no screen at all. "
        f"Held out, the three rank projects at "
        + ", ".join(f"{d['auc'][k]:.3f}" for k, _, _ in reversed(SERIES))
        + " area under ROC, where 0.500 is a coin flip. Project SIZE is absent from all of this "
          "because it does not predict: estimated annual credits entered the model at z=+1.17 and "
          "its square at z=-1.48, both null, and the apparent hump in a six-bin view of credits was "
          "the binning.",
        size=10.5, fill=MUTED, chars=126, leading=13)
    s += body

    # Budget the canvas from the WRAPPED text, never by eyeballing. The first
    # version fixed H and the footnote ran off the bottom of the page.
    fy = sy + 19 + len(body) * 13 + 30
    foot = plate.wrap(28, fy + 16,
        f"Gold Standard registry, {d['registry_total']:,} projects captured {d['observed']}. "
        f"{d['excluded_pre_cutoff']:,} are EXCLUDED: they carry a created_at before {d['cutoff'][:4]}, "
        f"and {d['migration_day'][1]:,} of them were created on {d['migration_day'][0]} alone with a "
        f"median five-year gap to their own crediting start — a migration, not a listing. Of the "
        f"{d['population']:,} that remain, {d['scored']:,} have a developer and a type with at least "
        f"three siblings to score against. EVERY SCORE IS LEAVE-ONE-OUT AND BACKWARD-LOOKING: a "
        f"project is graded only by siblings AT LEAST AS OLD as itself and never by itself, because "
        f"an in-sample rate rewards a grouping variable for having many small groups, and there are "
        f"761 developers here. The curves below 5% of the shortlist are not drawn — fewer than 25 "
        f"projects, where a single outcome moves the line four points.",
        size=10, fill=MUTED, chars=134, leading=13)
    s.append(f'<line x1="28" y1="{fy:.1f}" x2="{W-28}" y2="{fy:.1f}" stroke="{RULE}"/>')
    s += foot
    H = int(fy + 16 + len(foot) * 13 + 14)
    s.append("</svg>")
    svg = ("\n".join(s).replace('height="10"', f'height="{H}"')
                       .replace(f'viewBox="0 0 {W} 10"', f'viewBox="0 0 {W} {H}"'))
    assert 'height="10"' not in svg
    out = here.parent / "charts" / "screening.svg"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg, encoding="utf-8")
    print(f"  wrote {out.name}  base={base:.3f} top20%={d20:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
