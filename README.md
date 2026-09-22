# wss-carbon-registry — the Gold Standard carbon project register

Every project in the Gold Standard registry: name, status, methodology, type,
size, estimated annual credits, crediting period, SustainCert id.
**4,207 projects captured on 2026-09-22.**

**Status: paused, with one full baseline capture.** Read
[registry/goldstandard.registry.projects.yml](registry/goldstandard.registry.projects.yml) first.

## Why this exists

The status vocabulary across all 4,207 projects is **exactly three values, and
every one is a step forward**:

| status | projects |
| --- | ---: |
| `GOLD_STANDARD_CERTIFIED_PROJECT` | 2,279 |
| `LISTED` | 1,061 |
| `GOLD_STANDARD_CERTIFIED_DESIGN` | 867 |

There is no withdrawn, cancelled, expired or suspended. **A project that loses
certification has nowhere in this schema to be marked as having lost it** — so it
either freezes at its last step or leaves the register. Which one happens needs a
second capture, and the baseline for that now exists.

## Nobody else holds this

Measured, not assumed, on 2026-09-22:

- `public-api.goldstandard.org/projects` — **zero** Internet Archive mementos.
- `registry.goldstandard.org/projects` — 68 mementos, 2021 to 2026. Four sampled
  captures are **~2 KB client-rendered shells**, 59 characters of visible text,
  **not one project id between them**. The UI is a JavaScript application and the
  Archive photographed an empty frame 68 times.

So the register as it stood on any past date is not recoverable from anywhere.

## Why it is paused

The API is a bare JSON array, 25 per page, with no total in the response. The
capture is *page until an empty array* — 169 pages today, a different number next
month. `Endpoint` carries a fixed `url`, so expressing this needs either 169
hand-listed endpoints that go stale or a paging primitive the engine does not
have. Same class of limitation as `eudragmdp.gmp.noncompliance`'s session handshake.
The baseline in `raw/` was taken by script.

## One trap, already paid for

`created_at` puts **1,774 of 4,207 projects in 2019** — 42% in a single year,
against 321 the next. That is a platform migration timestamp, not a founding date.
Anything keyed on `created_at` will read a migration as a boom.

## Licence

Code: MIT ([LICENSE](LICENSE)). **The data carries no onward licence from this
repository** — see [LICENSE-DATA](LICENSE-DATA). Gold Standard's terms address
trademarks and event media and say nothing about the registry or its API, so what
they permit is unknown and is recorded as unknown. Attribute the Gold Standard
Foundation, not this repo.
