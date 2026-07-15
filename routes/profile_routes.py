from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from dao.image_dao import save_quest_image
from dao.participation_dao import get_session_stats, get_user_participations,session_has_participants
from dao.quest_dao import (
    create_quest,
    create_session,
    delete_session,
    get_all_quests,
    get_all_sessions_for_gm,
    get_session_detail,
    update_quest_image,
    update_session,
)

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile")
@login_required
def index():
    if current_user.role == "Guild Master":
        grouped = {quest["title"]: [] for quest in get_all_quests()}
        sessions = get_all_sessions_for_gm()
        for item in sessions:
            grouped[item["title"]].append(item)

        session_stats = {}
        for item in sessions:
            session_stats[item["session_id"]] = get_session_stats(item["session_id"])

        return render_template(
            "profile_gm.html",
            grouped_sessions=grouped,
            session_stats=session_stats,
        )

    participations = get_user_participations(current_user.id)
    return render_template("profile_adventurer.html", participations=participations)


@profile_bp.route("/gm/quest/new", methods=["GET", "POST"])
@login_required
def new_quest():
    if current_user.role != "Guild Master":
        flash("Only the Guild Master can create quests.", "danger")
        return redirect(url_for("home.index"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        duration = request.form.get("duration", "").strip()
        quest_type = request.form.get("quest_type", "").strip()
        difficulty = request.form.get("difficulty", "").strip()
        description = request.form.get("description", "").strip()
        image_file = request.files.get("image")

        if not all([title, duration, quest_type, difficulty, description]):
            flash("Please fill in all fields.", "danger")
            return render_template("gm_new_quest.html")

        try:
            duration_value = int(duration)
        except ValueError:
            flash("Duration must be a number.", "danger")
            return render_template("gm_new_quest.html")

        ok, result = save_quest_image(image_file)
        if not ok:
            flash(result, "danger")
            return render_template("gm_new_quest.html")

        ok, message = create_quest(
            title, duration_value, quest_type, difficulty, description, result
        )
        flash(message, "success" if ok else "danger")
        if ok:
            return redirect(url_for("profile.index"))

    return render_template("gm_new_quest.html")


@profile_bp.route("/gm/session/new", methods=["GET", "POST"])
@login_required
def new_session():
    if current_user.role != "Guild Master":
        flash("Only the Guild Master can create sessions.", "danger")
        return redirect(url_for("home.index"))

    quests = get_all_quests()

    if request.method == "POST":
        quest_id = request.form.get("quest_id", "")
        day = request.form.get("day", "")
        start_time = request.form.get("start_time", "")
        location = request.form.get("location", "")

        if not all([quest_id, day, start_time, location]):
            flash("Please fill in all fields.", "danger")
            return render_template("gm_new_session.html", quests=quests)

        ok, message = create_session(quest_id, day, start_time, location)
        flash(message, "success" if ok else "danger")
        if ok:
            return redirect(url_for("profile.index"))

    return render_template("gm_new_session.html", quests=quests)


@profile_bp.route("/gm/session/<int:session_id>/edit", methods=["GET", "POST"])
@login_required
def edit_session(session_id):
    if current_user.role != "Guild Master":
        flash("Only the Guild Master can edit sessions.", "danger")
        return redirect(url_for("home.index"))

    if session_has_participants(session_id):
        flash("Cannot edit: adventurers already joined.", "danger")
        return redirect(url_for("profile.index"))

    session = get_session_detail(session_id)
    if not session:
        flash("Session not found.", "danger")
        return redirect(url_for("profile.index"))

    if request.method == "POST":
        day = request.form.get("day", "")
        start_time = request.form.get("start_time", "")
        location = request.form.get("location", "")

        ok, message = update_session(session_id, day, start_time, location)
        if not ok:
            flash(message, "danger")
            return render_template("gm_edit_session.html", session=session)

        image_file = request.files.get("image")
        if image_file and image_file.filename:
            ok_img, result = save_quest_image(image_file)
            if not ok_img:
                flash(result, "danger")
                return render_template("gm_edit_session.html", session=session)
            update_quest_image(session["quest_id"], result)

        flash(message, "success")
        return redirect(url_for("profile.index"))

    return render_template("gm_edit_session.html", session=session)


@profile_bp.route("/gm/session/<int:session_id>/delete", methods=["POST"])
@login_required
def remove_session(session_id):
    if current_user.role != "Guild Master":
        flash("Only the Guild Master can cancel sessions.", "danger")
        return redirect(url_for("home.index"))

    ok, message = delete_session(session_id)
    flash(message, "success" if ok else "danger")
    return redirect(url_for("profile.index"))