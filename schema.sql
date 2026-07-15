PRAGMA FOREIGN_KEYS = ON;

DROP TABLE IF EXISTS participations;
DROP TABLE IF EXISTS quest_sessions;
DROP TABLE IF EXISTS quests;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('Guild Master', 'Adventurer'))
);

CREATE TABLE quests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE,
    duration INTEGER NOT NULL,
    quest_type TEXT NOT NULL CHECK(quest_type IN ('combat', 'exploration', 'puzzle', 'stealth', 'magic', 'survival')),
    difficulty TEXT NOT NULL CHECK(difficulty IN ('easy', 'medium', 'hard', 'legendary')),
    description TEXT NOT NULL,
    image_url TEXT NOT NULL
);

CREATE TABLE quest_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quest_id INTEGER NOT NULL,
    day_of_week TEXT NOT NULL CHECK(day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
    start_time TEXT NOT NULL,
    location TEXT NOT NULL CHECK(location IN ('Dungeon Hall', 'Enchanted Forest', 'Wizard Tower')),
    FOREIGN KEY (quest_id) REFERENCES quests(id)
);

CREATE TABLE participations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_id INTEGER NOT NULL,
    role_category TEXT NOT NULL CHECK(role_category IN ('Warrior', 'Mage', 'Healer')),
    slots_reserved INTEGER NOT NULL CHECK(slots_reserved IN (1, 2)),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (session_id) REFERENCES quest_sessions(id),
    UNIQUE(user_id, session_id)
);