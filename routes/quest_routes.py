from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from dao.participation_dao import (
    ROLE_LIMITS,
    cancel_participation,
    get_free_slots,
    get_session_stats,
    join_session,
    update_participation,
)
from dao.quest_dao import get_session_detail, get_sessions_by_quest

quest_bp = Blueprint("quest", __name__)


@quest_bp.route("/session/<int:session_id>")
def session_detail(session_id):
    session = get_session_detail(session_id)
    if not session:
        flash("Session not found.", "danger")
        return redirect(url_for("home.index"))

    role_info = {}
    for role in ROLE_LIMITS:
        role_info[role] = get_free_slots(session_id, role)

    stats = get_session_stats(session_id)
    quest_sessions = get_sessions_by_quest(session["quest_id"])

    return render_template(
        "session_detail.html",
        session=session,
        role_info=role_info,
        stats=stats,
        quest_sessions=quest_sessions,
    )


@quest_bp.route("/session/<int:session_id>/join", methods=["POST"])
@login_required
def join(session_id):
    if current_user.role != "Adventurer":
        flash("Only adventurers can join sessions.", "danger")
        return redirect(url_for("quest.session_detail", session_id=session_id))

    role = request.form.get("role", "")
    slots_text = request.form.get("slots", "1")

    if role not in ROLE_LIMITS:
        flash("Please choose a valid role.", "danger")
        return redirect(url_for("quest.session_detail", session_id=session_id))

    try:
        slots = int(slots_text)
    except ValueError:
        flash("Please choose 1 or 2 places.", "danger")
        return redirect(url_for("quest.session_detail", session_id=session_id))

    if slots not in [1, 2]:
        flash("You can reserve 1 or 2 places.", "danger")
        return redirect(url_for("quest.session_detail", session_id=session_id))

    ok, message = join_session(current_user.id, session_id, role, slots)
    flash(message, "success" if ok else "danger")
    return redirect(url_for("quest.session_detail", session_id=session_id))


@quest_bp.route("/participation/<int:participation_id>/edit", methods=["POST"])
@login_required
def edit_participation(participation_id):
    role = request.form.get("role", "")
    slots_text = request.form.get("slots", "1")

    try:
        slots = int(slots_text)
    except ValueError:
        flash("Please choose 1 or 2 places.", "danger")
        return redirect(url_for("profile.index"))

    ok, message = update_participation(current_user.id, participation_id, role, slots)
    flash(message, "success" if ok else "danger")
    return redirect(url_for("profile.index"))


@quest_bp.route("/participation/<int:participation_id>/cancel", methods=["POST"])
@login_required
def cancel(participation_id):
    ok, message = cancel_participation(current_user.id, participation_id)
    flash(message, "success" if ok else "danger")
    return redirect(url_for("profile.index"))