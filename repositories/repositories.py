#all SQL lives here, joins stay out of services and views

from models.models import get_db
from flask import abort

def _fetchone_or_404(conn, sql: str, params: tuple = ()):
    row = conn.execute(sql, params).fetchone()
    if row is None:
        abort(404)
    return row

#Character

class CharacterRepository:

    def get_all(self) -> list:
        with get_db() as conn:
            return conn.execute("""
                SELECT
                    c.CharacterID,
                    c.CharacterName,
                    c.Level,
                    cc.ClassID,
                    cc.ClassName,
                    s.SpeciesID,
                    s.SpeciesName,
                    a.AlignmentID,
                    a.AlignmentName
                FROM Character c
                JOIN CharacterClass cc ON c.ClassID     = cc.ClassID
                JOIN Species        s  ON c.SpeciesID   = s.SpeciesID
                JOIN Alignment      a  ON c.AlignmentID = a.AlignmentID
                ORDER BY c.CharacterName
            """).fetchall()

    def get_by_id(self, character_id: int):
        with get_db() as conn:
            return _fetchone_or_404(conn, """
                SELECT
                    c.CharacterID,
                    c.CharacterName,
                    c.Level,
                    c.ClassID,
                    c.SpeciesID,
                    c.AlignmentID,
                    cc.ClassName,
                    s.SpeciesName,
                    a.AlignmentName
                FROM Character c
                JOIN CharacterClass cc ON c.ClassID     = cc.ClassID
                JOIN Species        s  ON c.SpeciesID   = s.SpeciesID
                JOIN Alignment      a  ON c.AlignmentID = a.AlignmentID
                WHERE c.CharacterID = ?
            """, (character_id,))

    def create(self, data: dict) -> int:
        with get_db() as conn:
            cursor = conn.execute("""
                INSERT INTO Character (CharacterName, ClassID, SpeciesID, AlignmentID, Level)
                VALUES (?, ?, ?, ?, ?)
            """, (
                data["CharacterName"],
                data["ClassID"],
                data["SpeciesID"],
                data["AlignmentID"],
                data["Level"],
            ))
            conn.commit()
            return cursor.lastrowid

    def update(self, character_id: int, data: dict) -> None:
        with get_db() as conn:
            conn.execute("""
                UPDATE Character
                SET CharacterName = ?,
                    ClassID       = ?,
                    SpeciesID     = ?,
                    AlignmentID   = ?,
                    Level         = ?
                WHERE CharacterID = ?
            """, (
                data["CharacterName"],
                data["ClassID"],
                data["SpeciesID"],
                data["AlignmentID"],
                data["Level"],
                character_id,
            ))
            conn.commit()

    def delete(self, character_id: int) -> None:
        with get_db() as conn:
            conn.execute(
                "DELETE FROM Character WHERE CharacterID = ?",
                (character_id,)
            )
            conn.commit()

    def count(self) -> int:
        with get_db() as conn:
            return conn.execute(
                "SELECT COUNT(*) FROM Character"
            ).fetchone()[0]


#Item

class ItemRepository:

    def get_all(self) -> list:
        with get_db() as conn:
            return conn.execute("""
                SELECT
                    i.ItemID,
                    i.ItemName,
                    it.ItemTypeID,
                    it.TypeName,
                    r.RarityID,
                    r.RarityName
                FROM Item i
                JOIN ItemType it ON i.ItemTypeID = it.ItemTypeID
                JOIN Rarity   r  ON i.RarityID   = r.RarityID
                ORDER BY i.ItemName
            """).fetchall()

    def get_by_id(self, item_id: int):
        with get_db() as conn:
            return _fetchone_or_404(conn, """
                SELECT
                    i.ItemID,
                    i.ItemName,
                    it.ItemTypeID,
                    it.TypeName,
                    r.RarityID,
                    r.RarityName
                FROM Item i
                JOIN ItemType it ON i.ItemTypeID = it.ItemTypeID
                JOIN Rarity   r  ON i.RarityID   = r.RarityID
                WHERE i.ItemID = ?
            """, (item_id,))

    def create(self, data: dict) -> int:
        with get_db() as conn:
            cursor = conn.execute("""
                INSERT INTO Item (ItemName, ItemTypeID, RarityID)
                VALUES (?, ?, ?)
            """, (data["ItemName"], data["ItemTypeID"], data["RarityID"]))
            conn.commit()
            return cursor.lastrowid

    def delete(self, item_id: int) -> None:
        with get_db() as conn:
            conn.execute("DELETE FROM Item WHERE ItemID = ?", (item_id,))
            conn.commit()

    def count(self) -> int:
        with get_db() as conn:
            return conn.execute("SELECT COUNT(*) FROM Item").fetchone()[0]


#Quest

class QuestRepository:

    def get_all(self) -> list:
        with get_db() as conn:
            return conn.execute("""
                SELECT
                    q.QuestID,
                    q.QuestName,
                    r.RegionID,
                    r.RegionName,
                    d.DifficultyID,
                    d.DifficultyName
                FROM Quest q
                JOIN Region     r ON q.RegionID     = r.RegionID
                JOIN Difficulty d ON q.DifficultyID = d.DifficultyID
                ORDER BY q.QuestName
            """).fetchall()

    def get_by_id(self, quest_id: int):
        with get_db() as conn:
            return _fetchone_or_404(conn, """
                SELECT
                    q.QuestID,
                    q.QuestName,
                    r.RegionID,
                    r.RegionName,
                    d.DifficultyID,
                    d.DifficultyName
                FROM Quest q
                JOIN Region     r ON q.RegionID     = r.RegionID
                JOIN Difficulty d ON q.DifficultyID = d.DifficultyID
                WHERE q.QuestID = ?
            """, (quest_id,))

    def create(self, data: dict) -> int:
        with get_db() as conn:
            cursor = conn.execute("""
                INSERT INTO Quest (QuestName, RegionID, DifficultyID)
                VALUES (?, ?, ?)
            """, (data["QuestName"], data["RegionID"], data["DifficultyID"]))
            conn.commit()
            return cursor.lastrowid

    def delete(self, quest_id: int) -> None:
        with get_db() as conn:
            conn.execute("DELETE FROM Quest WHERE QuestID = ?", (quest_id,))
            conn.commit()

    def count(self) -> int:
        with get_db() as conn:
            return conn.execute("SELECT COUNT(*) FROM Quest").fetchone()[0]


#Inventory

class InventoryRepository:

    def get_for_character(self, character_id: int) -> list:
        with get_db() as conn:
            return conn.execute("""
                SELECT
                    inv.InventoryID,
                    inv.Quantity,
                    i.ItemID,
                    i.ItemName,
                    it.TypeName,
                    r.RarityName
                FROM Inventory inv
                JOIN Item     i  ON inv.ItemID     = i.ItemID
                JOIN ItemType it ON i.ItemTypeID   = it.ItemTypeID
                JOIN Rarity   r  ON i.RarityID     = r.RarityID
                WHERE inv.CharacterID = ?
                ORDER BY i.ItemName
            """, (character_id,)).fetchall()

    def get_by_id(self, inventory_id: int):
        with get_db() as conn:
            return _fetchone_or_404(
                conn,
                "SELECT * FROM Inventory WHERE InventoryID = ?",
                (inventory_id,)
            )

    def add_item(self, character_id: int, item_id: int, quantity: int = 1):
        #stack if already in inventory, else insert
        with get_db() as conn:
            existing = conn.execute("""
                SELECT InventoryID, Quantity
                FROM Inventory
                WHERE CharacterID = ? AND ItemID = ?
            """, (character_id, item_id)).fetchone()

            if existing:
                conn.execute("""
                    UPDATE Inventory
                    SET Quantity = Quantity + ?
                    WHERE InventoryID = ?
                """, (quantity, existing["InventoryID"]))
            else:
                conn.execute("""
                    INSERT INTO Inventory (CharacterID, ItemID, Quantity)
                    VALUES (?, ?, ?)
                """, (character_id, item_id, quantity))

            conn.commit()

    def remove_item(self, inventory_id: int) -> None:
        with get_db() as conn:
            conn.execute(
                "DELETE FROM Inventory WHERE InventoryID = ?",
                (inventory_id,)
            )
            conn.commit()


#CharacterQuest

class CharacterQuestRepository:

    def get_for_character(self, character_id: int) -> list:
        with get_db() as conn:
            return conn.execute("""
                SELECT
                    cq.CharacterQuestID,
                    cq.CompletionDate,
                    q.QuestID,
                    q.QuestName,
                    r.RegionName,
                    d.DifficultyName
                FROM CharacterQuest cq
                JOIN Quest      q  ON cq.QuestID     = q.QuestID
                JOIN Region     r  ON q.RegionID      = r.RegionID
                JOIN Difficulty d  ON q.DifficultyID  = d.DifficultyID
                WHERE cq.CharacterID = ?
                ORDER BY cq.CompletionDate DESC, q.QuestName
            """, (character_id,)).fetchall()

    def get_by_id(self, cq_id: int):
        with get_db() as conn:
            return _fetchone_or_404(
                conn,
                "SELECT * FROM CharacterQuest WHERE CharacterQuestID = ?",
                (cq_id,)
            )

    def assign(self, character_id: int, quest_id: int) -> int:
        with get_db() as conn:
            cursor = conn.execute("""
                INSERT INTO CharacterQuest (CharacterID, QuestID)
                VALUES (?, ?)
            """, (character_id, quest_id))
            conn.commit()
            return cursor.lastrowid

    def complete(self, cq_id: int) -> None:
        with get_db() as conn:
            conn.execute("""
                UPDATE CharacterQuest
                SET CompletionDate = datetime('now')
                WHERE CharacterQuestID = ?
            """, (cq_id,))
            conn.commit()


#Lookup

class LookupRepository:

    def get_classes(self) -> list:
        with get_db() as conn:
            return conn.execute(
                "SELECT ClassID, ClassName, Description FROM CharacterClass ORDER BY ClassName"
            ).fetchall()

    def get_species(self) -> list:
        with get_db() as conn:
            return conn.execute(
                "SELECT SpeciesID, SpeciesName FROM Species ORDER BY SpeciesName"
            ).fetchall()

    def get_alignments(self) -> list:
        with get_db() as conn:
            return conn.execute(
                "SELECT AlignmentID, AlignmentName FROM Alignment ORDER BY AlignmentName"
            ).fetchall()

    def get_item_types(self) -> list:
        with get_db() as conn:
            return conn.execute(
                "SELECT ItemTypeID, TypeName FROM ItemType ORDER BY TypeName"
            ).fetchall()

    def get_rarities(self) -> list:
        with get_db() as conn:
            return conn.execute(
                "SELECT RarityID, RarityName FROM Rarity ORDER BY RarityID"
            ).fetchall()

    def get_regions(self) -> list:
        with get_db() as conn:
            return conn.execute(
                "SELECT RegionID, RegionName FROM Region ORDER BY RegionName"
            ).fetchall()

    def get_difficulties(self) -> list:
        with get_db() as conn:
            return conn.execute(
                "SELECT DifficultyID, DifficultyName FROM Difficulty ORDER BY DifficultyID"
            ).fetchall()

    def get_reward_types(self) -> list:
        with get_db() as conn:
            return conn.execute(
                "SELECT RewardTypeID, TypeName FROM RewardType ORDER BY TypeName"
            ).fetchall()


#Reward

class RewardRepository:

    def get_all(self) -> list:
        with get_db() as conn:
            return conn.execute("""
                SELECT
                    r.RewardID,
                    r.RewardName,
                    r.Value,
                    r.ItemID,
                    rt.RewardTypeID,
                    rt.TypeName,
                    i.ItemName
                FROM Reward r
                JOIN RewardType rt ON r.RewardTypeID = rt.RewardTypeID
                LEFT JOIN Item  i  ON r.ItemID       = i.ItemID
                ORDER BY rt.TypeName, r.RewardName
            """).fetchall()

    def get_by_id(self, reward_id: int):
        with get_db() as conn:
            return _fetchone_or_404(conn, """
                SELECT
                    r.RewardID,
                    r.RewardName,
                    r.Value,
                    r.ItemID,
                    rt.RewardTypeID,
                    rt.TypeName,
                    i.ItemName
                FROM Reward r
                JOIN RewardType rt ON r.RewardTypeID = rt.RewardTypeID
                LEFT JOIN Item  i  ON r.ItemID       = i.ItemID
                WHERE r.RewardID = ?
            """, (reward_id,))

    def create(self, data: dict) -> int:
        with get_db() as conn:
            cursor = conn.execute("""
                INSERT INTO Reward (RewardName, RewardTypeID, Value, ItemID)
                VALUES (?, ?, ?, ?)
            """, (data["RewardName"], data["RewardTypeID"], data.get("Value"), data.get("ItemID")))
            conn.commit()
            return cursor.lastrowid

    def delete(self, reward_id: int) -> None:
        with get_db() as conn:
            conn.execute("DELETE FROM Reward WHERE RewardID = ?", (reward_id,))
            conn.commit()

    def count(self) -> int:
        with get_db() as conn:
            return conn.execute("SELECT COUNT(*) FROM Reward").fetchone()[0]


#QuestReward

class QuestRewardRepository:

    def get_for_quest(self, quest_id: int) -> list:
        with get_db() as conn:
            return conn.execute("""
                SELECT
                    qr.QuestRewardID,
                    qr.QuestID,
                    r.RewardID,
                    r.RewardName,
                    r.Value,
                    rt.TypeName,
                    i.ItemName
                FROM QuestReward qr
                JOIN Reward     r  ON qr.RewardID    = r.RewardID
                JOIN RewardType rt ON r.RewardTypeID = rt.RewardTypeID
                LEFT JOIN Item  i  ON r.ItemID       = i.ItemID
                WHERE qr.QuestID = ?
                ORDER BY rt.TypeName, r.RewardName
            """, (quest_id,)).fetchall()

    def get_by_id(self, qr_id: int):
        with get_db() as conn:
            return _fetchone_or_404(
                conn,
                "SELECT * FROM QuestReward WHERE QuestRewardID = ?",
                (qr_id,)
            )

    def add(self, quest_id: int, reward_id: int) -> int:
        with get_db() as conn:
            cursor = conn.execute("""
                INSERT INTO QuestReward (QuestID, RewardID)
                VALUES (?, ?)
            """, (quest_id, reward_id))
            conn.commit()
            return cursor.lastrowid

    def remove(self, qr_id: int) -> None:
        with get_db() as conn:
            conn.execute("DELETE FROM QuestReward WHERE QuestRewardID = ?", (qr_id,))
            conn.commit()
