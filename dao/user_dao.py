from werkzeug.security import check_password_hash, generate_password_hash

from database.database import close_db, get_db


def get_user_by_id(user_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    close_db(conn)
    return row


def get_user_by_login(login_value):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ? OR email = ?",
        (login_value, login_value),
    ).fetchone()
    close_db(conn)
    return row


def create_user(username, email, first_name, last_name, password):
    conn = get_db()
    try:
        conn.execute(
            """
            INSERT INTO users (username, email, first_name, last_name, password, role)
            VALUES (?, ?, ?, ?, ?, 'Adventurer')
            """,
            (
                username,
                email,
                first_name,
                last_name,
                generate_password_hash(password),
            ),
        )
        conn.commit()
        close_db(conn)
        return True, "Registration successful."
    except Exception:
        close_db(conn)
        return False, "Username or email already exists."


def check_login(login_value, password):
    user = get_user_by_login(login_value)
    if user and check_password_hash(user["password"], password):
        return user
    return None