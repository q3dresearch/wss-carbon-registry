# Data shape

*Generated 2026-09-24T23:05:04Z by `wss schema` from the derived rows. Do not hand-edit — regenerate after any derive.*

**You should not need to download anything to read this.**

- **82,326 observations** across 1 partition(s), in **1 series**
  - `goldstandard.registry.projects` — 82,326 rows, **4207 entities**
- Raw: 338 file(s), 10,668,610 bytes on disk, 1 capture date(s), 2026-09-22 → 2026-09-22

## Sources

| source | cadence | endpoints | storage | personal data | licence |
| --- | --- | ---: | --- | --- | --- |
| `goldstandard.registry.projects` | monthly | 169 | git | none | NOT ESTABLISHED (checked 2026-09-22). robots.txt on public-a |

## Columns

```
series_id, entity_id, observed_at, captured_at, metric, value, unit, source_id, raw_ref, parser_version
```

`entity_id` looks like: **goldstandard.registry.projects** `1000`, `1001`, `1003`

## Metrics

| metric | series | rows | entities | type | unit | distinct | range / samples |
| --- | --- | ---: | ---: | --- | --- | ---: | --- |
| `carbon_stream` | goldstandard.registry.projects | 4,206 | 4206 | text |  | 6 | `GS CER`, `GS_CER`, `GS_VER` |
| `country` | goldstandard.registry.projects | 4,207 | 4207 | text |  | 120 | `Angola`, `Argentina`, `Armenia` |
| `country_code` | goldstandard.registry.projects | 4,207 | 4207 | text |  | 120 | `AE`, `AM`, `AO` |
| `created_at` | goldstandard.registry.projects | 4,207 | 4207 | date |  | 2833 | `2019-03-27T13:49:25Z` … `2026-08-12T05:08:03Z` |
| `crediting_period_end` | goldstandard.registry.projects | 4,207 | 4207 | date |  | 1973 | `2006-12-31` … `2077-07-01` |
| `crediting_period_start` | goldstandard.registry.projects | 4,207 | 4207 | date |  | 1855 | `1995-01-01` … `2029-03-15` |
| `estimated_annual_credits` | goldstandard.registry.projects | 4,207 | 4207 | number | credits/yr | 2251 | `0` … `26686332` |
| `listed` | goldstandard.registry.projects | 4,207 | 4207 | bool | count | 1 | `1` |
| `methodology` | goldstandard.registry.projects | 2,416 | 2416 | text |  | 78 | `ACM0001 Flaring or use o`, `ACM0002 Grid-connected e`, `ACM0006 Electricity and ` |
| `name` | goldstandard.registry.projects | 4,207 | 4207 | text |  | 4189 | ` 10 MW Solar Photovoltai`, ` 13.3 MW grid connected `, ` 9.6 MW Wind Energy Proj` |
| `platform_id` | goldstandard.registry.projects | 4,207 | 4207 | number |  | 4207 | `1` … `5744` |
| `programme_of_activities` | goldstandard.registry.projects | 4,187 | 4187 | text |  | 4 | `No POA`, `POA`, `Standalone` |
| `project_developer` | goldstandard.registry.projects | 4,207 | 4207 | text |  | 761 | `3M Enerji ve Elektrik Ur`, `4Life Solutions ApS`, `ABK Enerji Elektrik reti` |
| `project_type` | goldstandard.registry.projects | 4,207 | 4207 | text |  | 20 | `A/R`, `Biogas - Cogeneration`, `Biogas - Electricity` |
| `sdg_count` | goldstandard.registry.projects | 4,206 | 4206 | number | count | 13 | `1` … `17` |
| `sdgs` | goldstandard.registry.projects | 4,206 | 4206 | text |  | 388 | `Goal 10: Reduced Inequal`, `Goal 10: Reduced Inequal`, `Goal 10: Reduced Inequal` |
| `size` | goldstandard.registry.projects | 4,207 | 4207 | text |  | 6 | `Large Scale`, `Large scale`, `Micro Scale` |
| `standards_version` | goldstandard.registry.projects | 4,207 | 4207 | text |  | 11 | `1.0`, `2.0`, `2.1` |
| `status` | goldstandard.registry.projects | 4,207 | 4207 | text |  | 3 | `GOLD_STANDARD_CERTIFIED_`, `GOLD_STANDARD_CERTIFIED_`, `LISTED` |
| `updated_at` | goldstandard.registry.projects | 4,207 | 4207 | date |  | 3463 | `2020-05-07T18:17:52Z` … `2026-09-22T15:44:13Z` |

## Partitions

- `derived/observations/2026-09.csv.gz`
