# Monster-Lineup-Generator-by-XP-Budget

Python tools for building D&D 5e monster lineups that respect experience budgets and difficulty guidelines.

## What it does
- Translate party member levels into easy, medium, hard, and deadly XP thresholds using Dungeon Master's Guide tables.
- Enumerate unique monster combinations that stay within a chosen XP budget, with optional min/max lineup sizes.
- Sample encounter budgets from a bell curve to diversify a session plan while keeping results near your desired difficulty.
- Ships with SRD 2014 CR 1 or lower monsters and XP values so you can start experimenting immediately.

## Requirements
- Python 3.10+ (CPython)
- `numpy` for random sampling
- `collections`
- `typing`

Install the dependency with:

```
python -m pip install numpy
```

## Quick start
```
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS / Linux
python -m pip install numpy
python main.py
```

`main.py` prints a sample set of diversified encounters. Adjust the party, difficulty, and diversification settings to mirror your table.

## Core modules
- `generator.py` exposes `generate_monster_lineup(...)` and `combos_under_budget_no_dupes(...)` for enumerating all lineups under a single XP budget.
  - `party_comp` — list of PC levels, e.g. `[3, 3, 4, 4]`
  - `difficulty` — one of `easy`, `medium`, `hard`, or `deadly`
  - `max_lineups`, `min_lineups`, and `random` — trim, filter, or shuffle the results
- `diversifier.py` exposes `diversified_lineups(...)`, which samples XP budgets and returns a list of `{budget, label, lineups}` dictionaries.
  - `encounters`, `mean_difficulty`, `stddev` — shape the normal curve
  - `min_fill` — discard lineups that fall too far below the target budget
  - `max_lineups_per_bucket` — limit how many unique lineups you keep per budget
  - `diversity_score` — optional callable to prioritise certain monster mixes

### Example: generate quick easy encounters
```python
from generator import generate_monster_lineup

party_comp = [4, 4, 4, 4]
generate_monster_lineup(
    party_comp,
    difficulty="easy",
    max_lineups=10,
    random=True,
)
```

### Example: build a diversified session plan
```python
from diversifier import diversified_lineups

encounters = diversified_lineups(
    party_comp=[5, 5, 5, 5],
    encounters=12,
    mean_difficulty="medium",
    stddev=0.4,
    min_fill=0.8,
    max_lineups_per_bucket=4,
    random_state=123,
)

for encounter in encounters:
    print(encounter["label"], encounter["budget"])
    for lineup in encounter["lineups"]:
        print("  ", lineup)
```

## Customising the monster list
`monsters.py` defines `SRD_2014_MONSTERS_CR1_OR_LOWER`, a dictionary mapping monster names to XP. Edit it to include creatures from your campaign, then pass the updated dictionary into `diversified_lineups(..., monsters=...)` or `combos_under_budget_no_dupes(...)`.

## Data source
Monster data originates from the 2014 SRD monster JSON maintained by https://github.com/5e-bits/5e-database. Review their licence and attribution guidelines before redistributing modified datasets.

