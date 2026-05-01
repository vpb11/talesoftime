import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.models import get_db, init_db

#Lookup / Reference data

LOOKUP_SEED_DATA = {
    "CharacterClass": [
        {"ClassName": "Warrior", "Description": "A powerful melee fighter."},
        {"ClassName": "Alien", "Description": "A powerful creature of unknown origin, acid for blood."},
    ],
    "Species": [
        {"SpeciesName": "Human"},
        {"SpeciesName": "Xenomorph"},
    ],
    "Alignment": [
        {"AlignmentName": "Lawful Good"},
        {"AlignmentName": "Un-Lawful Bad"},
    ],
    "ItemType": [
        {"TypeName": "Weapon"},
        {"TypeName": "Consumable"},
    ],
    "Rarity": [
        {"RarityName": "common"},
        {"RarityName": "uncommon"},
        {"RarityName": "rare"},
        {"RarityName": "epic"},
        {"RarityName": "legendary"},
    ],
    "Region": [
        {"RegionName": "The Verdant Vale"},
        {"RegionName": "The Tardis Dimension"},
    ],
    "Difficulty": [
        {"DifficultyName": "Hobbiest"},
        {"DifficultyName": "Novice"},
        {"DifficultyName": "Confident"},
        {"DifficultyName": "Pro"},
    ],
}


def seed_lookup_tables():
    with get_db() as conn:
        for table, rows in LOOKUP_SEED_DATA.items():
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            if count == 0:
                for row in rows:
                    columns = ", ".join(row.keys())
                    placeholders = ", ".join("?" for _ in row)
                    conn.execute(
                        f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
                        tuple(row.values())
                    )
                print(f"  + Seeded {table}")
            else:
                print(f"  - Skipped {table} (already has data)")
        conn.commit()


def seed_core_data():
    with get_db() as conn:
        # ── Lookup helpers ──────────────────────────────────────────────────
        classes    = {r["ClassName"]:     r for r in conn.execute("SELECT * FROM CharacterClass").fetchall()}
        species    = {r["SpeciesName"]:   r for r in conn.execute("SELECT * FROM Species").fetchall()}
        alignments = {r["AlignmentName"]: r for r in conn.execute("SELECT * FROM Alignment").fetchall()}
        item_types = {r["TypeName"]:      r for r in conn.execute("SELECT * FROM ItemType").fetchall()}
        rarities   = {r["RarityName"]:    r for r in conn.execute("SELECT * FROM Rarity").fetchall()}
        regions    = {r["RegionName"]:    r for r in conn.execute("SELECT * FROM Region").fetchall()}
        difficulties = {r["DifficultyName"]: r for r in conn.execute("SELECT * FROM Difficulty").fetchall()}

        # ── Characters ──────────────────────────────────────────────────────
        character_rows = [
            {
                "CharacterName": "Thorin Ironblade",
                "ClassID":       classes["Warrior"]["ClassID"],
                "SpeciesID":     species["Human"]["SpeciesID"],
                "AlignmentID":   alignments["Lawful Good"]["AlignmentID"],
                "Level":         12,
            },
        ]

        characters = []
        if conn.execute("SELECT COUNT(*) FROM Character").fetchone()[0] == 0:
            for row in character_rows:
                cursor = conn.execute("""
                    INSERT INTO Character (CharacterName, ClassID, SpeciesID, AlignmentID, Level)
                    VALUES (?, ?, ?, ?, ?)
                """, (row["CharacterName"], row["ClassID"], row["SpeciesID"], row["AlignmentID"], row["Level"]))
                characters.append({"CharacterName": row["CharacterName"], "CharacterID": cursor.lastrowid})
            conn.commit()
            print("  + Seeded Character")
        else:
            characters = [dict(r) for r in conn.execute("SELECT CharacterID, CharacterName FROM Character").fetchall()]
            print("  - Skipped Character (already has data)")

        character_map = {c["CharacterName"]: c for c in characters}

        # ── Items ───────────────────────────────────────────────────────────
        item_rows = [
            {
                "ItemName":   "Iron Sword",
                "ItemTypeID": item_types["Weapon"]["ItemTypeID"],
                "RarityID":   rarities["Common"]["RarityID"],
            },
        ]

        items = []
        if conn.execute("SELECT COUNT(*) FROM Item").fetchone()[0] == 0:
            for row in item_rows:
                cursor = conn.execute("""
                    INSERT INTO Item (ItemName, ItemTypeID, RarityID)
                    VALUES (?, ?, ?)
                """, (row["ItemName"], row["ItemTypeID"], row["RarityID"]))
                items.append({"ItemName": row["ItemName"], "ItemID": cursor.lastrowid})
            conn.commit()
            print("  + Seeded Item")
        else:
            items = [dict(r) for r in conn.execute("SELECT ItemID, ItemName FROM Item").fetchall()]
            print("  - Skipped Item (already has data)")

        item_map = {i["ItemName"]: i for i in items}

        # ── Quests ──────────────────────────────────────────────────────────
        quest_rows = [
            {
                "QuestName":    "Defend the Vale",
                "RegionID":     regions["The Verdant Vale"]["RegionID"],
                "DifficultyID": difficulties["Novice"]["DifficultyID"],
            },
        ]

        quests = []
        if conn.execute("SELECT COUNT(*) FROM Quest").fetchone()[0] == 0:
            for row in quest_rows:
                cursor = conn.execute("""
                    INSERT INTO Quest (QuestName, RegionID, DifficultyID)
                    VALUES (?, ?, ?)
                """, (row["QuestName"], row["RegionID"], row["DifficultyID"]))
                quests.append({"QuestName": row["QuestName"], "QuestID": cursor.lastrowid})
            conn.commit()
            print("  + Seeded Quest")
        else:
            quests = [dict(r) for r in conn.execute("SELECT QuestID, QuestName FROM Quest").fetchall()]
            print("  - Skipped Quest (already has data)")

        quest_map = {q["QuestName"]: q for q in quests}

        # ── Inventory ───────────────────────────────────────────────────────
        inventory_rows = [
            {
                "CharacterID": character_map["Thorin Ironblade"]["CharacterID"],
                "ItemID":      item_map["Iron Sword"]["ItemID"],
                "Quantity":    1,
            },
        ]

        if conn.execute("SELECT COUNT(*) FROM Inventory").fetchone()[0] == 0:
            for row in inventory_rows:
                conn.execute("""
                    INSERT INTO Inventory (CharacterID, ItemID, Quantity)
                    VALUES (?, ?, ?)
                """, (row["CharacterID"], row["ItemID"], row["Quantity"]))
            conn.commit()
            print("  + Seeded Inventory")
        else:
            print("  - Skipped Inventory (already has data)")

        # ── CharacterQuest ──────────────────────────────────────────────────
        character_quest_rows = [
            {
                "CharacterID":    character_map["Thorin Ironblade"]["CharacterID"],
                "QuestID":        quest_map["Defend the Vale"]["QuestID"],
                "CompletionDate": datetime(2026, 1, 12, 14, 30).isoformat(),
            },
        ]

        if conn.execute("SELECT COUNT(*) FROM CharacterQuest").fetchone()[0] == 0:
            for row in character_quest_rows:
                conn.execute("""
                    INSERT INTO CharacterQuest (CharacterID, QuestID, CompletionDate)
                    VALUES (?, ?, ?)
                """, (row["CharacterID"], row["QuestID"], row["CompletionDate"]))
            conn.commit()
            print("  + Seeded CharacterQuest")
        else:
            print("  - Skipped CharacterQuest (already has data)")


def seed():
    init_db()
    seed_lookup_tables()
    seed_core_data()
    print("\nSeed complete.")


if __name__ == "__main__":
    seed()
