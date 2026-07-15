from database.database import close_db, get_db

ROLE_LIMITS = {"Warrior": 4, "Mage": 3, "Healer": 2}

# fake current day and time for testing
SIMULATED_DAY = "Monday"
SIMULATED_TIME = "08:00"

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def time_to_minutes(time_text):
    hour, minute = time_text.split(":")
    return int(hour) * 60 + int(minute)


def get_simulated_minutes():
    day_index = DAYS.index(SIMULATED_DAY)
    return day_index * 24 * 60 + time_to_minutes(SIMULATED_TIME)


def get_session_start_minutes(day, start_time):
    day_index = DAYS.index(day)
    return day_index * 24 * 60 + time_to_minutes(start_time)


def can_change_participation(day, start_time):
    diff = get_session_start_minutes(day, start_time) - get_simulated_minutes()
    return diff > 8 * 60


def session_has_participants(session_id):
    conn = get_db()
    row = conn.execute(
        "SELECT COUNT(*) AS total FROM participations WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    close_db(conn)
    return row["total"] > 0


def get_used_slots(session_id, role):
    conn = get_db()
    row = conn.execute(
        """
        SELECT COALESCE(SUM(slots_reserved), 0) AS total
        FROM participations
        WHERE session_id = ? AND role_category = ?
        """,
        (session_id, role),
    ).fetchone()
    close_db(conn)
    return row["total"]


def get_free_slots(session_id, role):
    return ROLE_LIMITS[role] - get_used_slots(session_id, role)


def count_user_sessions(user_id):
    conn = get_db()
    row = conn.execute(
        "SELECT COUNT(*) AS total FROM participations WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    close_db(conn)
    return row["total"]


def user_has_overlap(user_id, day, start_time, duration):
    new_start = get_session_start_minutes(day, start_time)
    new_end = new_start + duration

    conn = get_db()
    rows = conn.execute(
        """
        SELECT p.session_id, qs.day_of_week,
               qs.start_time, q.duration
        FROM participations as p
        JOIN quest_sessions as qs ON qs.id = p.session_id
        JOIN quests as q ON q.id = qs.quest_id
        WHERE p.user_id = ?
        """,
        (user_id,),
    ).fetchall()
    close_db(conn)

    for row in rows:
        old_start = get_session_start_minutes(row["day_of_week"], row["start_time"])
        old_end = old_start + row["duration"]
        if new_start < old_end and old_start < new_end:
            return True
    return False


def join_session(user_id, session_id, role, slots):
    from dao.quest_dao import get_session_detail

    session = get_session_detail(session_id)
    if not session:
        return False, "Session not found."

    if count_user_sessions(user_id) >= 3:
        return False, "You can join at most 3 sessions per week."

    if user_has_overlap(user_id, session["day_of_week"], session["start_time"], session["duration"]):
        return False, "This session overlaps with one you already joined."

    if get_free_slots(session_id, role) < slots:
        return False, "Not enough free places for this role."

    conn = get_db()
    try:
        conn.execute(
            """
            INSERT INTO participations (user_id, session_id, role_category, slots_reserved)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, session_id, role, slots),
        )
        conn.commit()
        close_db(conn)
        return True, "You joined the quest session."
    except Exception:
        close_db(conn)
        return False, "You already joined this session."


def update_participation(user_id, participation_id, role, slots):
    conn = get_db()
    row = conn.execute(
        """
        SELECT p.*, qs.day_of_week, qs.start_time
        FROM participations as p
        JOIN quest_sessions as qs ON qs.id = p.session_id
        WHERE p.id = ? AND p.user_id = ?
        """,
        (participation_id, user_id),
    ).fetchone()

    if not row:
        close_db(conn)
        return False, "Participation not found."

    if not can_change_participation(row["day_of_week"], row["start_time"]):
        close_db(conn)
        return False, "Too late to change this participation."

    old_slots = row["slots_reserved"]
    old_role = row["role_category"]
    session_id = row["session_id"]

    free_slots = get_free_slots(session_id, role)
    if role == old_role:
        free_slots += old_slots

    if free_slots < slots:
        close_db(conn)
        return False, "Not enough free places for this role."

    conn.execute(
        """
        UPDATE participations
        SET role_category = ?, slots_reserved = ?
        WHERE id = ?
        """,
        (role, slots, participation_id),
    )
    conn.commit()
    close_db(conn)
    return True, "Participation updated."


def cancel_participation(user_id, participation_id):
    conn = get_db()
    row = conn.execute(
        """
        SELECT p.id, qs.day_of_week, qs.start_time
        FROM participations as p
        JOIN quest_sessions as qs ON qs.id = p.session_id
        WHERE p.id = ? AND p.user_id = ?
        """,
        (participation_id, user_id),
    ).fetchone()

    if not row:
        close_db(conn)
        return False, "Participation not found."

    if not can_change_participation(row["day_of_week"], row["start_time"]):
        close_db(conn)
        return False, "Too late to cancel this participation."

    conn.execute("DELETE FROM participations WHERE id = ?", (participation_id,))
    conn.commit()
    close_db(conn)
    return True, "Participation cancelled."


def get_user_participations(user_id):
    conn = get_db()
    rows = conn.execute(
        """
        SELECT
            p.id AS participation_id,
            p.role_category,
            p.slots_reserved,
            qs.day_of_week,
            qs.start_time,
            qs.location,
            q.title
        FROM participations as p
        JOIN quest_sessions as qs ON qs.id = p.session_id
        JOIN quests as q ON q.id = qs.quest_id
        WHERE p.user_id = ?
        ORDER BY qs.day_of_week, qs.start_time
        """,
        (user_id,),
    ).fetchall()
    close_db(conn)
    return rows


def get_session_stats(session_id):
    stats = {}
    for role, limit in ROLE_LIMITS.items():
        used = get_used_slots(session_id, role)
        stats[role] = {"used": used, "free": limit - used, "limit": limit}

    most_requested = max(stats, key=lambda r: stats[r]["used"])
    total_reserved = sum(item["used"] for item in stats.values())

    return {
        "roles": stats,
        "most_requested": most_requested,
        "total_reserved": total_reserved,
    }