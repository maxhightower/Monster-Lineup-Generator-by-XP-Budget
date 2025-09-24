import numpy as np
from typing import Dict, List, Tuple, Iterator, Optional
from collections import Counter
from monsters import SRD_2014_MONSTERS_CR1_OR_LOWER as calling_all_the_monsters


# how can I make this scalable???
xp_thresholds_by_character_level = [
    [25, 50, 75, 100],
    [50, 100, 150, 200],
    [75, 150, 225, 400],
    [125, 250, 375, 500],
    [250, 500, 750, 1100],
    [300, 600, 900, 1400],
    [350, 750, 1100, 1700],
    [450, 900, 1400, 2100],
    [550, 1100, 1600, 2400],
    [600, 1200, 1900, 2800],
    [800, 1600, 2400, 3600],
    [1000, 2000, 3000, 4500],
    [1100, 2200, 3400, 5100],
    [1250, 2500, 3800, 5700],
    [1400, 2800, 4300, 6400],
    [1600, 3200, 4800, 7200],
    [2000, 3900, 5900, 8800],
    [2100, 4200, 6300, 9500],
    [2400, 4900, 7300, 10900],
    [2800, 5700, 8500, 12700],
]
# now I can grab the xp thresholds for any level from 1 to 20

def total_xp(lineup: List[str], monsters_xp: Dict[str, int]) -> int:
    return sum(monsters_xp[m] for m in lineup)

def total_xp_counts(lineup: Counter, monsters_xp: Dict[str, int]) -> int:
    return sum(monsters_xp[m] * c for m, c in lineup.items())

def _sorted_items(monsters_xp: Dict[str, int]) -> List[Tuple[str, int]]:
    # Sort by XP ascending (helps pruning)
    return sorted(monsters_xp.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)

def combos_under_budget_no_dupes(
    monsters_xp: Dict[str, int],
    budget: int,
    max_monsters: Optional[int] = None,
    min_monsters: Optional[int] = None,
    threshold: Optional[int] = None,   # the minimum % of the budget that must be used
) -> Iterator[List[str]]:
    """
    Yield lists of monster names (no repeats) with total XP <= budget.
    Order within each list is lexicographic (by XP then name), not significant.
    """
    # monsters from highest xp to lowest
    items = _sorted_items(monsters_xp)  # [(name, xp), ...]
    filter_items = [item for item in items if item[1] <= budget]
    n = len(filter_items)

    stack: List[str] = []
    stack_xp = 0

    def dfs(start: int):
        nonlocal stack_xp

        # Every node (including empty) is a valid combo
        if stack_xp <= budget and (min_monsters is None or len(stack) >= min_monsters) and (threshold is None or stack_xp >= budget * threshold):
            yield list(stack)
        
        # Try to extend
        for i in range(start, n):
            name, xp = filter_items[i]
        
            if max_monsters is not None and len(stack) >= max_monsters:
                break
        
            if stack_xp + xp > budget:
                # All further items are >= xp, so we can prune
                break
        
            stack.append(name)
            stack_xp += xp
        
            yield from dfs(i + 1)  # move to next index (no repeats)
        
            stack_xp -= xp
            stack.pop()

    # add all valid lineups to a list and return that list
    #valid_lineups = list(dfs(0))
    #return valid_lineups
    for lineup in dfs(0):
        yield lineup




def generate_monster_lineup(party_comp: list, difficulty: str):
    num_players = len(party_comp)

    # so the list contains the levels of the party members
    # we can't use the average, the xp budget is based on each member's level
    if difficulty.lower() == 'easy':
        difficulty_index = 0
    elif difficulty.lower() == 'medium':
        difficulty_index = 1
    elif difficulty.lower() == 'hard':
        difficulty_index = 2
    elif difficulty.lower() == 'deadly':
        difficulty_index = 3
    else:
        raise ValueError("Invalid difficulty level. Choose from 'easy', 'medium', 'hard', 'deadly'.")

    party_xp_thresholds = [xp_thresholds_by_character_level[level - 1][difficulty_index] for level in party_comp]
    total_xp_budget = sum(party_xp_thresholds)
    print(f"Total XP Budget: {total_xp_budget}")

    tonight_all_the_monsters_gonna_dance = combos_under_budget_no_dupes(
        calling_all_the_monsters,
        total_xp_budget,
        max_monsters=None,
        min_monsters=None,
        threshold=1
    )
    
    print("Generated monster lineups:")
    for lineup in tonight_all_the_monsters_gonna_dance:
        print(f"Lineup: {lineup}")
    #print(f"Counting lineups...{tonight_all_the_monsters_gonna_dance}")

