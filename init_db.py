from werkzeug.security import generate_password_hash

from database.database import close_db, get_db

PASSWORD = generate_password_hash("password123")


def init_database():
    conn = get_db()
    cursor = conn.cursor()

    with open("schema.sql", "r") as f:
        cursor.executescript(f.read())

    cursor.executescript(
        f"""
        INSERT INTO users (username, email, first_name, last_name, password, role) VALUES
        ('guildmaster', 'gm@guild.com', 'Aragorn', 'Stormcrow', '{PASSWORD}', 'Guild Master'),
        ('adventurer1', 'adv1@guild.com', 'Elara', 'Moonwhisper', '{PASSWORD}', 'Adventurer'),
        ('adventurer2', 'adv2@guild.com', 'Thorin', 'Ironfist', '{PASSWORD}', 'Adventurer'),
        ('adventurer3', 'adv3@guild.com', 'Lirael', 'Starweaver', '{PASSWORD}', 'Adventurer'),
        ('adventurer4', 'adv4@guild.com', 'Garrick', 'Blackthorn', '{PASSWORD}', 'Adventurer');
        """
    )

    cursor.executescript(
        """
        INSERT INTO quests (title, duration, quest_type, difficulty, description, image_url) VALUES
        ('Slay the Ancient Dragon', 120, 'combat', 'legendary', 'Defeat the mighty dragon terrorizing the lands.', 'https://picsum.photos/id/1015/400/180'),
        ('Lost Artifact Recovery', 90, 'exploration', 'medium', 'Recover the ancient relic from the ruins.', 'https://picsum.photos/id/160/400/180'),
        ('Shadow Assassin Hunt', 60, 'stealth', 'hard', 'Track down the rogue assassin.', 'https://picsum.photos/id/201/400/180'),
        ('Mystic Forest Cleansing', 75, 'magic', 'easy', 'Restore balance to the enchanted forest.', 'https://picsum.photos/id/251/400/180'),
        ('Puzzle of the Sphinx', 45, 'puzzle', 'medium', 'Solve the riddles of the Sphinx.', 'https://picsum.photos/id/29/400/180'),
        ('Survival in the Frozen Wastes', 150, 'survival', 'hard', 'Survive in the harsh frozen lands.', 'https://picsum.photos/id/1005/400/180');
        """
    )

    cursor.executescript(
        """
        INSERT INTO quest_sessions (quest_id, day_of_week, start_time, location) VALUES
        (1, 'Monday', '10:00', 'Dungeon Hall'),
        (2, 'Monday', '14:00', 'Enchanted Forest'),
        (3, 'Tuesday', '09:00', 'Wizard Tower'),
        (4, 'Tuesday', '16:00', 'Dungeon Hall'),
        (5, 'Wednesday', '11:00', 'Enchanted Forest'),
        (6, 'Wednesday', '15:00', 'Wizard Tower'),
        (1, 'Thursday', '10:00', 'Dungeon Hall'),
        (3, 'Thursday', '14:00', 'Enchanted Forest'),
        (2, 'Friday', '14:00', 'Enchanted Forest'),
        (4, 'Friday', '16:00', 'Wizard Tower'),
        (5, 'Saturday', '10:00', 'Dungeon Hall'),
        (6, 'Saturday', '14:00', 'Enchanted Forest'),
        (1, 'Sunday', '11:00', 'Wizard Tower'),
        (2, 'Sunday', '15:00', 'Dungeon Hall');
        """
    )

    cursor.executescript(
        """
        INSERT INTO participations (user_id, session_id, role_category, slots_reserved) VALUES
        (2, 1, 'Warrior', 1),
        (3, 1, 'Mage', 1),
        (4, 2, 'Healer', 1),
        (5, 3, 'Warrior', 2),
        (2, 3, 'Warrior', 1),
        (3, 3, 'Warrior', 1);
        """
    )

    conn.commit()
    close_db(conn)
    print("Database ready with sample data.")


if __name__ == "__main__":
    init_database()