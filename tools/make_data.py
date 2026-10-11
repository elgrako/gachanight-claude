#!/usr/bin/env python3
"""Regenerates data/machines.json and data/figures.json from one compact table.

The game only reads the JSON files; this script exists so a rebalance of prices
does not mean editing thirty figures by hand. Run from the repository root:

    python tools/make_data.py

Everything here is a BALANCE EXAMPLE except the values the design fixes:
machine_001 costs 1, has exactly 5 figures and sells for >= 1; machine_002 costs
50 and sells for >= 30.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RARITIES = ["common", "uncommon", "rare", "epic", "legendary"]
WEIGHTS = [50, 28, 14, 6, 2]
COPIES = [5, 4, 3, 2, 1]
PRESTIGE = [1, 2, 4, 8, 16]
# Sale value as a multiple of the machine price, by rarity.
SELL_MULTIPLIERS = [0.6, 1.1, 2.0, 4.0, 10.0]
BONUSES = [
    ("sell_value_pct", 3),
    ("price_discount_pct", 5),
    ("robot_speed_pct", 10),
    ("luck_pct", 3),
    ("sell_value_pct", 6),
]

# Later machines pay back less of their price at base values: they are where
# sale upgrades and permanent prestige earn their keep, and a place to spend
# coins on collections. Expected return at base = 1.328 * sale factor.
# id, type, display name, series name, price, unlocks prestige, sale factor or explicit sales
MACHINES = [
    ("machine_001", "gacha", "Capsule Machine No. 1", "Pocket Pals", 1, False, [1, 2, 4, 8, 16]),
    ("machine_002", "gacha", "Capsule Machine No. 2", "Festival Friends", 50, True, 1.0),
    ("machine_003", "gacha", "Capsule Machine No. 3", "Snack Squad", 3000, False, 0.76),
    ("machine_004", "gacha", "Capsule Machine No. 4", "Space Patrol", 250000, False, 0.42),
    ("machine_005", "claw", "Crane Catcher", "Plush Parade", 25000000, False, 0.25),
    ("machine_006", "plinko", "Lucky Plinko", "Fortune Parade", 3000000000, False, 0.15),
]

# name, body, ears, extra, color, accent  (one row per rarity, common first)
FIGURES = {
    "machine_001": [
        ("Bubble Bird", "round", "none", "beak", "#7ec8c0", "#f2b84b"),
        ("Nap Frog", "wide", "round", "belly", "#8fc97a", "#f4ecd8"),
        ("Tin Robo", "square", "antenna", "belly", "#d9a441", "#ef7a6d"),
        ("Moon Bunny", "round", "long", "tail", "#f1d9e0", "#ef7a6d"),
        ("Golden Daruma", "wide", "none", "crown", "#e3b44c", "#c9412f"),
    ],
    "machine_002": [
        ("Ramune Bear", "tall", "round", "belly", "#6fb1d6", "#f4ecd8"),
        ("Kite Fox", "tall", "pointy", "tail", "#ef7a6d", "#f4ecd8"),
        ("Drum Tanuki", "wide", "pointy", "drum", "#b98a5e", "#f4ecd8"),
        ("Comet Owl", "square", "pointy", "wings", "#8a7fd1", "#f2b84b"),
        ("Star Kaiju", "tall", "antenna", "spikes", "#4f9ea3", "#e3b44c"),
    ],
    "machine_003": [
        ("Mochi Seal", "wide", "none", "tail", "#f4ecd8", "#f1a7b5"),
        ("Dango Chick", "round", "none", "beak", "#f6d86b", "#ef7a6d"),
        ("Taiyaki Fish", "wide", "none", "wings", "#d9a05b", "#8a5a34"),
        ("Melon Turtle", "round", "round", "shell", "#b7d77a", "#e7efb0"),
        ("Royal Pudding", "pear", "none", "crown", "#f2c96a", "#8a5a34"),
    ],
    "machine_004": [
        ("Rocket Pup", "tall", "round", "wings", "#e9e4d8", "#ef7a6d"),
        ("Saturn Snail", "wide", "antenna", "shell", "#c9b6e6", "#f2b84b"),
        ("Astro Monkey", "round", "round", "tail", "#b98a5e", "#6fb1d6"),
        ("Nebula Jelly", "pear", "none", "spikes", "#8fd3e8", "#c48ad6"),
        ("Galaxy Dragon", "tall", "horns", "wings", "#5b5fb0", "#e3b44c"),
    ],
    "machine_005": [
        ("Sleepy Panda", "round", "round", "wings", "#f4ecd8", "#2b2b33"),
        ("Cloud Sheep", "wide", "horns", "belly", "#eef3f5", "#f1a7b5"),
        ("Tiger Cub", "round", "pointy", "tail", "#f2a24b", "#2b2b33"),
        ("Thunder Oni", "square", "horns", "drum", "#ef7a6d", "#f2b84b"),
        ("Lucky Whale", "wide", "none", "crown", "#4f7fc0", "#e3b44c"),
    ],
    "machine_006": [
        ("Bell Mouse", "pear", "round", "tail", "#d6cfbd", "#e3b44c"),
        ("Coin Toad", "wide", "round", "crown", "#6fa86a", "#e3b44c"),
        ("Koi Kite", "tall", "none", "wings", "#ef7a6d", "#f4ecd8"),
        ("Lantern Ghost", "pear", "none", "star", "#f4ecd8", "#ef7a6d"),
        ("Treasure Kappa", "square", "antenna", "shell", "#7ec8a4", "#e3b44c"),
    ],
}

# Optional look keys understood by tools/blender/build_figures.py, by figure name.
LOOK_EXTRAS = {
    "Nap Frog": {"eyes": "sleepy"},
    "Golden Daruma": {"extras": ["mask"], "limbs": "none"},
    "Comet Owl": {"extras": ["beak"]},
    "Dango Chick": {"body": "pear"},
    "Rocket Pup": {"wing_style": "jet"},
    "Sleepy Panda": {"eyes": "sleepy"},
    "Cloud Sheep": {"pattern": "fluff"},
    "Lucky Whale": {"extras": ["tail", "wings"]},
    "Lantern Ghost": {"limbs": "none"},
    "Treasure Kappa": {"ears": "none", "extras": ["beak"]},
}


def main() -> None:
    machines = []
    figures = []
    for index, (machine_id, kind, name, series, price, unlocks, sale_rule) in enumerate(MACHINES):
        number = machine_id.split("_")[1]
        table = []
        if isinstance(sale_rule, list):
            sales = sale_rule
        else:
            sales = [max(1, int(round(price * multiplier * sale_rule))) for multiplier in SELL_MULTIPLIERS]
        for rank, (figure_name, body, ears, extra, color, accent) in enumerate(FIGURES[machine_id]):
            figure_id = f"g{number}_toy_{rank + 1:02d}"
            bonus_id, bonus_value = BONUSES[rank]
            figures.append({
                "id": figure_id,
                "name_en": figure_name,
                "rarity_id": RARITIES[rank],
                "base_sell_value": sales[rank],
                "copies_required": COPIES[rank],
                "prestige_reward": PRESTIGE[rank] * (index + 1),
                "collection_bonus_id": bonus_id,
                "collection_bonus_params": {"value": bonus_value},
                "look": {"body": body, "ears": ears, "extra": extra, "color": color, "accent": accent,
                         **LOOK_EXTRAS.get(figure_name, {})},
            })
            table.append({"figure_id": figure_id, "weight": WEIGHTS[rank]})
        machines.append({
            "id": machine_id,
            "machine_type": kind,
            "display_name_en": name,
            "series_name_en": series,
            "price_per_attempt": price,
            "min_sell_value": min(sales),
            "unlocks_prestige": unlocks,
            "prize_table": table,
        })
    note = "Generated by tools/make_data.py. BALANCE EXAMPLE: names, values, weights and bonuses are provisional."
    fixed = " Fixed by design: machine_001 costs 1 with exactly 5 figures and sale >= 1; machine_002 costs 50 with sale >= 30 and unlocks prestige on first use."
    write("machines.json", {"_comment": note + fixed, "machines": machines})
    write("figures.json", {"_comment": note + " 'look' drives the generated 3D model and the fallback icon.", "figures": figures})


def write(name: str, payload: dict) -> None:
    path = ROOT / "data" / name
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
