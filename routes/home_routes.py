from flask import Blueprint, render_template, request

from dao.participation_dao import SIMULATED_DAY, SIMULATED_TIME
from dao.quest_dao import get_sessions_for_home

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index():
    day_filter = request.args.get("day", "")
    quest_type_filter = request.args.get("quest_type", "")
    difficulty_filter = request.args.get("difficulty", "")
    role_filter = request.args.get("role", "")

    sessions = get_sessions_for_home(
        day_filter, quest_type_filter, difficulty_filter, role_filter
    )

    return render_template(
        "home.html",
        sessions=sessions,
        day_filter=day_filter,
        quest_type_filter=quest_type_filter,
        difficulty_filter=difficulty_filter,
        role_filter=role_filter,
        simulated_day=SIMULATED_DAY,
        simulated_time=SIMULATED_TIME,
    )