# the idea behind the diversifier is to create combats which 
# may match a normal distribution of easy, medium, hard, deadly encounters
import numpy as np
from collections import Counter
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from generator import generate_monster_lineup, combos_under_budget_no_dupes, xp_thresholds_by_character_level
from monsters import SRD_2014_MONSTERS_CR1_OR_LOWER

Difficulty = str
Lineup = Sequence[str]
Encounter = Dict[str, object]
DiversityScore = Callable[[Lineup], Tuple[int, int, int]]


def _party_thresholds(party_comp: Sequence[int]) -> Dict[Difficulty, int]:
    return {
        label: sum(xp_thresholds_by_character_level[level - 1][idx] for level in party_comp)
        for idx, label in enumerate(("easy", "medium", "hard", "deadly"))
    }


def _label_budget(budget: int, thresholds: Dict[Difficulty, int]) -> Difficulty:
    for label in ("easy", "medium", "hard"):
        if budget <= thresholds[label]:
            return label
    return "deadly"


def _default_diversity_score(lineup: Lineup) -> Tuple[int, int, int]:
    if not lineup:
        return (0, 0, 0)
    counts = Counter(lineup)
    unique_types = len(counts)
    largest_stack = max(counts.values()) if counts else 0
    total_count = len(lineup)
    return (unique_types, -largest_stack, total_count)

def strong_diversity(lineup):
    counts = Counter(lineup)
    if not counts:
        return (0, 0, 0, 0)
    unique = len(counts)                 # reward different monster types
    largest_stack = max(counts.values()) # penalise big repeats
    duplicate_mass = sum(c * c for c in counts.values())  # squares blow up streaks
    total = len(lineup)
    return (unique, -largest_stack, -duplicate_mass, -total)


def diversified_lineups(
    party_comp: Sequence[int],
    *,
    encounters: int = 7,
    mean_difficulty: Difficulty = "medium",
    stddev: float = 0.6,
    min_fill: float = 0.85,
    max_lineups_per_bucket: int = 3,
    xp_threshold_on: bool = False,
    monsters: Optional[Dict[str, int]] = None,
    random_state: Optional[int] = None,
    diversity_score: Optional[DiversityScore] = None,
) -> List[Encounter]:
    """
    Return a list of encounters whose XP budgets approximate a normal distribution.

    Args:
        party_comp: Levels of the PCs.
        encounters: How many encounter buckets to return.
        mean_difficulty: Which difficulty band should act as the mean of the curve.
        stddev: Standard deviation as a fraction of the party's easy-to-deadly XP spread.
        min_fill: Minimum fraction of each budget that a lineup must hit.
        max_lineups_per_bucket: Cap on how many lineups to keep per budget.
        xp_threshold_on: When True, clip budgets to the party's easy/deadly thresholds.
            When False, budgets may fall outside that range but never below zero.
        monsters: Override monster XP map; defaults to SRD low-CR set.
        random_state: Seed for reproducibility.
        diversity_score: Optional scoring function; higher scores surface first.

    Returns:
        A list of dictionaries with budget, label, and lineups.
    """
    if encounters <= 0:
        return []

    rng = np.random.default_rng(random_state)
    monsters = monsters or SRD_2014_MONSTERS_CR1_OR_LOWER
    min_xp = min(monsters.values())
    thresholds = _party_thresholds(party_comp)

    mean_budget = thresholds[mean_difficulty.lower()]
    easy_budget = thresholds["easy"]
    deadly_budget = thresholds["deadly"]
    xp_span = deadly_budget - easy_budget
    sigma = max(1.0, stddev * xp_span)

    sampled = rng.normal(loc=mean_budget, scale=sigma, size=encounters).round().astype(int)
    sorted_budgets = np.sort(sampled)
    # Align budgets to multiples of the cheapest monster and keep bins distinct
    processed_budgets: List[int] = []
    for raw_budget in sorted_budgets.tolist():
        if xp_threshold_on:
            target = min(max(int(raw_budget), easy_budget), deadly_budget)
        else:
            target = max(int(raw_budget), 0)

        if min_xp > 0:
            target = (target // min_xp) * min_xp

        if processed_budgets and target <= processed_budgets[-1]:
            if min_xp > 0:
                candidate = processed_budgets[-1] + min_xp
                if xp_threshold_on and candidate > deadly_budget:
                    continue
                target = candidate
            else:
                target = processed_budgets[-1] + 1

        if xp_threshold_on:
            target = min(target, deadly_budget)
        else:
            target = max(target, 0)

        if min_xp > 0 and target % min_xp != 0:
            target = (target // min_xp) * min_xp

        if processed_budgets and target == processed_budgets[-1]:
            continue

        processed_budgets.append(target)

    score_fn = diversity_score or _default_diversity_score

    results: List[Encounter] = []
    for xp_budget in processed_budgets:
        candidate_limit = None
        if max_lineups_per_bucket is not None:
            candidate_limit = max(max_lineups_per_bucket * 10, max_lineups_per_bucket)
        
        lineups = combos_under_budget_no_dupes(
            monsters,
            budget=int(xp_budget),
            threshold=min_fill,
            max_lineups=candidate_limit,
            random=True,
        )
        if not lineups:
            continue

        unique_lineups: List[Lineup] = []
        seen_signatures = set()

        for lineup in sorted(lineups, key=score_fn, reverse=True):
            signature = tuple(sorted(Counter(lineup).items()))
            if signature in seen_signatures:
                continue
            seen_signatures.add(signature)
            unique_lineups.append(lineup)
            if max_lineups_per_bucket is not None and len(unique_lineups) >= max_lineups_per_bucket:
                break

        if not unique_lineups:
            continue

        results.append(
            {
                "budget": int(xp_budget),
                "label": _label_budget(int(xp_budget), thresholds),
                "lineups": unique_lineups,
            }
        )

    return results
