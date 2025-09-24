from generator import generate_monster_lineup
from diversifier import diversified_lineups

def main():
    party_comp = [1, 1, 1]  # Example party composition (levels)
    difficulty = 'easy'  # Example difficulty
    #generate_monster_lineup(party_comp, 
    #                        difficulty,
    #                        random=True
    #                        )

    encounters = diversified_lineups(
        party_comp,
        encounters=20,
        mean_difficulty='easy',
        stddev=0.6,
        min_fill=0.75,
        max_lineups_per_bucket=3,
        random_state=42,
        xp_threshold_on=False,
        
    )
    for encounter in encounters:
        print(f"Budget: {encounter['budget']}, Label: {encounter['label']}")
        for lineup in encounter['lineups']:
            print(f"  {lineup}")


if __name__ == "__main__":
    main()