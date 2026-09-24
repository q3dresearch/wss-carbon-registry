#!/usr/bin/env python3
"""What predicts whether a listed Gold Standard project ever certifies.

    python3 certification_model.py [--out ../public/certification-<date>.json]

**The buyer's question.** A project sits at LISTED. Will it reach
GOLD_STANDARD_CERTIFIED_PROJECT, or stall? The registry publishes no status
history and no terminal state, so the only way to ask is to compare projects of
matched age and see which ones got there.

**Two traps, both paid for here.**

1. `created_at` IS NOT A LISTING DATE FOR 42% OF THE REGISTRY. 1,615 of 4,207
   records were created on 2019-03-27 alone, with a median five-year gap to their
   own crediting-period start: a migration, not a listing event. From 2020 the
   median gap is 0-1 years. Everything below is restricted to `created_at >= 2020`.

2. AGE IS THE WHOLE CONFOUND. A project listed last year has not had time to
   certify -- 0.0% of the youngest decile has. Any comparison that does not hold
   age constant is measuring the calendar.

**Scores are LEAVE-ONE-OUT and backward-looking.** A project's developer score is
the certification rate of that developer's OTHER projects that are AT LEAST AS OLD
as it. A project never contributes to its own score, and no score uses information
from the future relative to the project it grades. In-sample scoring inflates any
grouping variable by rewarding cardinality; 761 developers over 2,433 projects
would have been flattered enormously.
"""
from __future__ import annotations
import argparse, collections, datetime as dt, glob, gzip, json, math, os, pathlib, random
import numpy as np

OBS = dt.date(2026, 9, 22)
CUTOFF = dt.date(2020, 1, 1)
CERT = "GOLD_STANDARD_CERTIFIED_PROJECT"


def load(repo: pathlib.Path):
    rows = []
    for f in sorted((repo / "raw").rglob("*.gz")):
        rows += json.loads(gzip.decompress(f.read_bytes()))
    return rows


def logit(X, y, it=300):
    X = np.asarray(X, float); y = np.asarray(y, float); b = np.zeros(X.shape[1])
    for _ in range(it):
        p = 1 / (1 + np.exp(-X @ b)); W = np.clip(p * (1 - p), 1e-9, None)
        b += np.linalg.solve(X.T @ (X * W[:, None]) + 1e-6 * np.eye(X.shape[1]), X.T @ (y - p))
    p = 1 / (1 + np.exp(-X @ b)); W = np.clip(p * (1 - p), 1e-9, None)
    se = np.sqrt(np.diag(np.linalg.inv(X.T @ (X * W[:, None]) + 1e-6 * np.eye(X.shape[1]))))
    return b, se


def auc(score, y):
    pos = [s for s, t in zip(score, y) if t == 1]
    neg = [s for s, t in zip(score, y) if t == 0]
    if not pos or not neg:
        return float("nan")
    return sum((p > n) + 0.5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg))


def main() -> int:
    here = pathlib.Path(__file__).resolve()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(here.parents[1] / "public" /
                                         f"certification-{OBS.isoformat()}.json"))
    a = ap.parse_args()
    raw = load(here.parents[1])
    d = lambda s: dt.date.fromisoformat(s[:10])

    migrated = collections.Counter(r["created_at"][:10] for r in raw
                                   if r.get("created_at") and d(r["created_at"]) < CUTOFF)
    pop = []
    for r in raw:
        if not r.get("created_at") or d(r["created_at"]) < CUTOFF:
            continue
        c = r.get("estimated_annual_credits")
        pop.append(dict(id=r["id"], age=(OBS - d(r["created_at"])).days / 365.25,
                        cert=1.0 if r["status"] == CERT else 0.0,
                        typ=r.get("type") or "unknown", dev=r.get("project_developer") or "unknown",
                        credits=c if isinstance(c, (int, float)) and c > 0 else None,
                        country=r.get("country") or "unknown"))

    bydev, bytyp = collections.defaultdict(list), collections.defaultdict(list)
    for p in pop:
        bydev[p["dev"]].append(p); bytyp[p["typ"]].append(p)
    scored = []
    for p in pop:
        sib = [q for q in bydev[p["dev"]] if q["id"] != p["id"] and q["age"] >= p["age"]]
        tsi = [q for q in bytyp[p["typ"]] if q["id"] != p["id"] and q["age"] >= p["age"]]
        if len(sib) >= 3 and len(tsi) >= 3:
            p["devr"] = sum(q["cert"] for q in sib) / len(sib); p["ndev"] = len(sib)
            p["typr"] = sum(q["cert"] for q in tsi) / len(tsi)
            scored.append(p)

    age = np.array([p["age"] for p in scored]); y = np.array([p["cert"] for p in scored])
    dv = np.array([p["devr"] for p in scored]); tp = np.array([p["typr"] for p in scored])
    z = lambda v: (v - v.mean()) / v.std()
    models = {"age": [z(age), z(age) ** 2],
              "age+type": [z(age), z(age) ** 2, z(tp)],
              "age+type+developer": [z(age), z(age) ** 2, z(tp), z(dv)]}
    coef = {}
    for name, cols in models.items():
        b, se = logit(np.c_[np.ones(len(scored)), *cols], y)
        coef[name] = [{"term": t, "beta": round(float(bb), 4), "z": round(float(bb / ss), 2)}
                      for t, bb, ss in zip(["const", "age", "age2", "type_rate", "developer_rate"],
                                           b, se)]

    random.seed(20260925)
    idx = list(range(len(scored))); random.shuffle(idx)
    cut = int(0.7 * len(idx)); tr, te = idx[:cut], idx[cut:]
    held, lift = {}, {}
    for name, cols in models.items():
        X = np.c_[np.ones(len(scored)), *cols]
        b, _ = logit(X[tr], y[tr]); s = X[te] @ b
        held[name] = round(float(auc(s, y[te])), 4)
        order = sorted(range(len(te)), key=lambda i: -s[i])
        cum, run = [], 0.0
        for k, i in enumerate(order, 1):
            run += y[te][i]; cum.append(round(run / k, 5))
        lift[name] = cum
    base = float(y[te].mean())

    # the age curve, continuous and exposure-matched, split by whether the type is A/R
    curve = []
    srt = sorted(scored, key=lambda p: p["age"]); k = max(1, len(srt) // 14)
    for i in range(14):
        g = srt[i * k:(i + 1) * k] if i < 13 else srt[13 * k:]
        if len(g) < 10: continue
        ar = [p for p in g if p["typ"] == "A/R"]
        curve.append(dict(age_lo=round(g[0]["age"], 2), age_hi=round(g[-1]["age"], 2),
                          age_mid=round(sum(p["age"] for p in g) / len(g), 2), n=len(g),
                          rate=round(sum(p["cert"] for p in g) / len(g), 4),
                          n_ar=len(ar),
                          rate_ar=round(sum(p["cert"] for p in ar) / len(ar), 4) if len(ar) >= 5 else None))

    band = [p for p in scored if 3 <= p["age"] < 6]
    bt = collections.defaultdict(list)
    for p in band: bt[p["typ"]].append(p["cert"])
    types = sorted(({"type": t, "n": len(v), "rate": round(sum(v) / len(v), 4)}
                    for t, v in bt.items() if len(v) >= 15), key=lambda r: -r["rate"])

    devs = []
    for dname, ps in bydev.items():
        if len(ps) < 5 or dname == "unknown": continue
        cr = [p["credits"] for p in ps if p["credits"]]
        devs.append(dict(dev=dname, n=len(ps),
                         rate=round(sum(p["cert"] for p in ps) / len(ps), 4),
                         median_age=round(float(np.median([p["age"] for p in ps])), 2),
                         median_credits=int(np.median(cr)) if cr else None,
                         top_type=collections.Counter(p["typ"] for p in ps).most_common(1)[0][0]))
    devs.sort(key=lambda r: -r["n"])

    out = dict(
        observed=OBS.isoformat(), cutoff=CUTOFF.isoformat(),
        registry_total=len(raw), population=len(pop), scored=len(scored),
        migration_day=migrated.most_common(1)[0] if migrated else None,
        excluded_pre_cutoff=sum(migrated.values()),
        base_rate=round(float(np.mean([p["cert"] for p in pop])), 4),
        holdout_base=round(base, 4), holdout_n=len(te),
        auc=held, lift=lift, coefficients=coef,
        age_curve=curve, types_matched_3_6y=types, developers=devs)
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1))
    print(f"  {len(raw)} records -> {len(pop)} listed 2020+ -> {len(scored)} scored")
    print(f"  excluded {sum(migrated.values())} pre-{CUTOFF.year} (migration day {out['migration_day']})")
    print(f"  held-out AUC: " + "  ".join(f"{k}={v:.3f}" for k, v in held.items()))
    print(f"  wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
