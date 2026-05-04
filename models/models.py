import sqlite3
import os

_HERE   = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.normpath(os.environ.get("DATABASE_PATH", os.path.join(_HERE, "..", "instance", "tales_of_time.db")))


def get_db() -> sqlite3.Connection:
    #results come back as dicts, foreign keys on by default
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


#Schema DDL, safe to rerun on startup

_SCHEMA = """

-- Lookup tables

CREATE TABLE IF NOT EXISTS CharacterClass (
    ClassID     INTEGER PRIMARY KEY AUTOINCREMENT,
    ClassName   VARCHAR(50)  NOT NULL UNIQUE,
    Description TEXT
);

CREATE TABLE IF NOT EXISTS Species (
    SpeciesID   INTEGER PRIMARY KEY AUTOINCREMENT,
    SpeciesName VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Alignment (
    AlignmentID   INTEGER PRIMARY KEY AUTOINCREMENT,
    AlignmentName VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS ItemType (
    ItemTypeID INTEGER PRIMARY KEY AUTOINCREMENT,
    TypeName   VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Rarity (
    RarityID   INTEGER PRIMARY KEY AUTOINCREMENT,
    RarityName VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Region (
    RegionID   INTEGER PRIMARY KEY AUTOINCREMENT,
    RegionName VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Difficulty (
    DifficultyID   INTEGER PRIMARY KEY AUTOINCREMENT,
    DifficultyName VARCHAR(50) NOT NULL UNIQUE
);

-- Core entities

CREATE TABLE IF NOT EXISTS Character (
    CharacterID   INTEGER PRIMARY KEY AUTOINCREMENT,
    CharacterName VARCHAR(100) NOT NULL,
    ClassID       INTEGER NOT NULL,
    SpeciesID     INTEGER NOT NULL,
    AlignmentID   INTEGER NOT NULL,
    Level         INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (ClassID)     REFERENCES CharacterClass(ClassID),
    FOREIGN KEY (SpeciesID)   REFERENCES Species(SpeciesID),
    FOREIGN KEY (AlignmentID) REFERENCES Alignment(AlignmentID)
);

CREATE TABLE IF NOT EXISTS Item (
    ItemID     INTEGER PRIMARY KEY AUTOINCREMENT,
    ItemName   VARCHAR(100) NOT NULL,
    ItemTypeID INTEGER NOT NULL,
    RarityID   INTEGER NOT NULL,
    FOREIGN KEY (ItemTypeID) REFERENCES ItemType(ItemTypeID),
    FOREIGN KEY (RarityID)   REFERENCES Rarity(RarityID)
);

CREATE TABLE IF NOT EXISTS Quest (
    QuestID      INTEGER PRIMARY KEY AUTOINCREMENT,
    QuestName    VARCHAR(100) NOT NULL,
    RegionID     INTEGER NOT NULL,
    DifficultyID INTEGER NOT NULL,
    FOREIGN KEY (RegionID)     REFERENCES Region(RegionID),
    FOREIGN KEY (DifficultyID) REFERENCES Difficulty(DifficultyID)
);

-- Join tables

CREATE TABLE IF NOT EXISTS Inventory (
    InventoryID INTEGER PRIMARY KEY AUTOINCREMENT,
    CharacterID INTEGER NOT NULL,
    ItemID      INTEGER NOT NULL,
    Quantity    INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (CharacterID) REFERENCES Character(CharacterID) ON DELETE CASCADE,
    FOREIGN KEY (ItemID)      REFERENCES Item(ItemID)
);

CREATE TABLE IF NOT EXISTS CharacterQuest (
    CharacterQuestID INTEGER PRIMARY KEY AUTOINCREMENT,
    CharacterID      INTEGER  NOT NULL,
    QuestID          INTEGER  NOT NULL,
    CompletionDate   DATETIME,
    FOREIGN KEY (CharacterID) REFERENCES Character(CharacterID) ON DELETE CASCADE,
    FOREIGN KEY (QuestID)     REFERENCES Quest(QuestID)
);

-- Rewards

CREATE TABLE IF NOT EXISTS RewardType (
    RewardTypeID INTEGER PRIMARY KEY AUTOINCREMENT,
    TypeName     VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Reward (
    RewardID     INTEGER PRIMARY KEY AUTOINCREMENT,
    RewardName   VARCHAR(100) NOT NULL,
    RewardTypeID INTEGER NOT NULL,
    Value        INTEGER,
    ItemID       INTEGER,
    FOREIGN KEY (RewardTypeID) REFERENCES RewardType(RewardTypeID),
    FOREIGN KEY (ItemID)       REFERENCES Item(ItemID)
);

CREATE TABLE IF NOT EXISTS QuestReward (
    QuestRewardID INTEGER PRIMARY KEY AUTOINCREMENT,
    QuestID       INTEGER NOT NULL,
    RewardID      INTEGER NOT NULL,
    FOREIGN KEY (QuestID)  REFERENCES Quest(QuestID)  ON DELETE CASCADE,
    FOREIGN KEY (RewardID) REFERENCES Reward(RewardID) ON DELETE CASCADE
);

"""


def init_db() -> None:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_db() as conn:
        conn.executescript(_SCHEMA)
        conn.commit()
