from database.database import close_db, get_db
from dao.participation_dao import time_to_minutes,get_free_slots

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def get_all_quests():
    conn = get_db()
    rows = conn.execute("SELECT * FROM quests ORDER BY title").fetchall()
    close_db(conn)
    return rows


def get_quest_by_id(quest_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM quests WHERE id = ?", (quest_id,)).fetchone()
    close_db(conn)
    return row


def create_quest(title, duration, quest_type, difficulty, description, image_url):
    conn = get_db()
    try:
        conn.execute(
            """
            INSERT INTO quests (title, duration, quest_type, difficulty, description, image_url)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (title, duration, quest_type, difficulty, description, image_url),
        )
        conn.commit()
        close_db(conn)
        return True, "Quest created."
    except Exception:
        close_db(conn)
        return False, "Quest title already exists."


def get_sessions_for_home(day_filter="", quest_type_filter="", difficulty_filter="", role_filter=""):
    conn = get_db()

    query = """
        SELECT
            qs.id AS session_id,
            qs.day_of_week,
            qs.start_time,
            qs.location,
            q.id AS quest_id,
            q.title,
            q.duration,
            q.quest_type,
            q.difficulty,
            q.description,
            q.image_url
        FROM quest_sessions as qs
        JOIN quests as q ON q.id = qs.quest_id
        WHERE 1 = 1
    """
    params = []

    if day_filter:
        query += " AND qs.day_of_week = ?"
        params.append(day_filter)

    if quest_type_filter:
        query += " AND q.quest_type = ?"
        params.append(quest_type_filter)

    if difficulty_filter:
        query += " AND q.difficulty = ?"
        params.append(difficulty_filter)

    rows = conn.execute(query, params).fetchall()
    close_db(conn)

    sessions = []
    for row in rows:
        item = dict(row)
        if role_filter:
            if get_free_slots(item["session_id"], role_filter) <= 0:
                continue
        sessions.append(item)

    sessions.sort(key=lambda s: (DAYS.index(s["day_of_week"]), s["start_time"]))
    return sessions


def get_session_detail(session_id):
    conn = get_db()
    row = conn.execute(
        """
        SELECT
            qs.id AS session_id,
            qs.day_of_week,
            qs.start_time,
            qs.location,
            q.id AS quest_id,
            q.title,
            q.duration,
            q.quest_type,
            q.difficulty,
            q.description,
            q.image_url
        FROM quest_sessions as qs
        JOIN quests as q ON q.id = qs.quest_id
        WHERE qs.id = ?
        """,
        (session_id,),
    ).fetchone()
    close_db(conn)
    return row


def get_sessions_by_quest(quest_id):
    conn = get_db()
    rows = conn.execute(
        """
        SELECT * FROM quest_sessions
        WHERE quest_id = ?
        ORDER BY day_of_week, start_time
        """,
        (quest_id,),
    ).fetchall()
    close_db(conn)
    return rows


def times_overlap(start_a, duration_a, start_b, duration_b):
    end_a = start_a + duration_a
    end_b = start_b + duration_b
    return start_a < end_b and start_b < end_a


def location_is_busy(day, start_time, duration, location, session_id=None):
    new_start = time_to_minutes(start_time)
    conn = get_db()

    if session_id:
        rows = conn.execute(
            """
            SELECT qs.start_time, q.duration
            FROM quest_sessions as qs
            JOIN quests as q ON q.id = qs.quest_id
            WHERE qs.day_of_week = ? AND qs.location = ? AND qs.id != ?
            """,
            (day, location, session_id),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT qs.start_time, q.duration
            FROM quest_sessions as qs
            JOIN quests as q ON q.id = qs.quest_id
            WHERE qs.day_of_week = ? AND qs.location = ?
            """,
            (day, location),
        ).fetchall()

    close_db(conn)

    for row in rows:
        old_start = time_to_minutes(row["start_time"])
        if times_overlap(new_start, duration, old_start, row["duration"]):
            return True
    return False


def create_session(quest_id, day, start_time, location):
    quest = get_quest_by_id(quest_id)
    if not quest:
        return False, "Quest not found."

    if location_is_busy(day, start_time, quest["duration"], location):
        return False, "This location overlaps with another session."

    conn = get_db()
    conn.execute(
        """
        INSERT INTO quest_sessions (quest_id, day_of_week, start_time, location)
        VALUES (?, ?, ?, ?)
        """,
        (quest_id, day, start_time, location),
    )
    conn.commit()
    close_db(conn)
    return True, "Session created."


def update_quest_image(quest_id, image_url):
    conn = get_db()
    conn.execute(
        "UPDATE quests SET image_url = ? WHERE id = ?",
        (image_url, quest_id),
    )
    conn.commit()
    close_db(conn)
    return True


def update_session(session_id, day, start_time, location):
    from dao.participation_dao import session_has_participants

    if session_has_participants(session_id):
        return False, "Cannot edit: adventurers already joined."

    session = get_session_detail(session_id)
    if not session:
        return False, "Session not found."

    if location_is_busy(day, start_time, session["duration"], location, session_id):
        return False, "This location overlaps with another session."

    conn = get_db()
    conn.execute(
        """
        UPDATE quest_sessions
        SET day_of_week = ?, start_time = ?, location = ?
        WHERE id = ?
        """,
        (day, start_time, location, session_id),
    )
    conn.commit()
    close_db(conn)
    return True, "Session updated."


def delete_session(session_id):
    from dao.participation_dao import session_has_participants

    if session_has_participants(session_id):
        return False, "Cannot cancel: adventurers already joined."

    conn = get_db()
    conn.execute("DELETE FROM quest_sessions WHERE id = ?", (session_id,))
    conn.commit()
    close_db(conn)
    return True, "Session cancelled."


def get_all_sessions_for_gm():
    conn = get_db()
    rows = conn.execute(
        """
        SELECT
            qs.id AS session_id,
            qs.day_of_week,
            qs.start_time,
            qs.location,
            q.id AS quest_id,
            q.title,
            q.duration,
            q.quest_type,
            q.difficulty
        FROM quest_sessions as qs
        JOIN quests as q ON q.id = qs.quest_id
        ORDER BY q.title, qs.day_of_week, qs.start_time
        """
    ).fetchall()
    close_db(conn)
    return rows