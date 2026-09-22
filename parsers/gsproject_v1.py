"""Parser for schema_id `gsproject.v1` — the Gold Standard carbon registry.

WHAT MOVES HERE IS A PROJECT LEAVING

Across all 4,207 projects the status vocabulary is exactly three values and
every one is a PROGRESSION step: LISTED, GOLD_STANDARD_CERTIFIED_DESIGN,
GOLD_STANDARD_CERTIFIED_PROJECT. There is no withdrawn, cancelled, expired or
suspended. A project that loses certification has nowhere to be marked as
having lost it, so it must either freeze at its last progression step or leave
the register altogether.

So `listed` is emitted once per project per capture and ITS ABSENCE LATER IS
THE FINDING. `updated_at` is the registry's own edit stamp and is what makes
the other case -- a silent in-place edit -- visible and datable.

TWO TRAPS, BOTH MEASURED

`created_at` puts 1,774 of 4,207 projects in 2019: 42% in one year against 321
the next. That is a platform migration timestamp, not a founding date, and
anything keyed on it reads a migration as a boom. It is emitted because it is
what the publisher says, and the name is left alone so nobody mistakes it for
a founding date it was never claiming to be.

`sustainable_development_goals` IS A SET SERVED IN ARBITRARY ORDER. Refetching
page 1 hours apart, all 25 records carried an identical set of goals and 24 of
the 25 came back reordered. A "primary SDG" taken from the first element is
noise, so the goals are SORTED before being emitted and the count is emitted
beside them.

THE ENTITY IS THE SUSTAINCERT ID, not the platform `id`. It is the one that
appears in sustaincert_url and is therefore the identifier anything outside
this registry can be joined on. The platform id is carried as its own metric
so a change in the mapping is visible rather than silent.
"""
import json

from wss import derive

PARSER_VERSION = "1"
SCHEMA_ID = "gsproject.v1"

# Straight passthrough fields -> metric name. Strings, kept as strings.
TEXT = {
    "updated_at": "updated_at",
    "created_at": "created_at",
    "status": "status",
    "type": "project_type",
    "size": "size",
    "country": "country",
    "country_code": "country_code",
    "methodology": "methodology",
    "carbon_stream": "carbon_stream",
    "project_developer": "project_developer",
    "gsf_standards_version": "standards_version",
    "programme_of_activities": "programme_of_activities",
    "crediting_period_start_date": "crediting_period_start",
    "crediting_period_end_date": "crediting_period_end",
    "name": "name",
}


def parse(body: bytes, ctx: derive.ParseContext):
    records = json.loads(body)
    if not isinstance(records, list):
        return                      # the last page is a bare [] once the walk runs past the end
    for r in records:
        if not isinstance(r, dict):
            continue
        key = r.get("sustaincert_id") or r.get("id")
        if key in (None, ""):
            continue
        entity = str(key)

        yield derive.Observation(entity_id=entity, metric="listed", value=1, unit="count")

        credits = r.get("estimated_annual_credits")
        if isinstance(credits, (int, float)) and not isinstance(credits, bool):
            yield derive.Observation(entity_id=entity, metric="estimated_annual_credits",
                                     value=int(credits), unit="credits/yr")

        for field, metric in TEXT.items():
            v = r.get(field)
            if v not in (None, ""):
                yield derive.Observation(entity_id=entity, metric=metric, value=str(v))

        pid = r.get("id")
        if pid not in (None, ""):
            yield derive.Observation(entity_id=entity, metric="platform_id", value=str(pid))

        # Sorted, because the publisher's order is arbitrary and changes between
        # fetches. Unsorted this metric would report a change on every capture.
        goals = r.get("sustainable_development_goals") or []
        names = sorted(str(g.get("name")) for g in goals
                       if isinstance(g, dict) and g.get("name"))
        if names:
            yield derive.Observation(entity_id=entity, metric="sdg_count",
                                     value=len(names), unit="count")
            yield derive.Observation(entity_id=entity, metric="sdgs", value="; ".join(names))


derive.register(SCHEMA_ID, parse, PARSER_VERSION)
