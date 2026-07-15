import os

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager

from dao.user_dao import get_user_by_id
from models import User
from routes.auth_routes import auth_bp
from routes.home_routes import home_bp
from routes.profile_routes import profile_bp
from routes.quest_routes import quest_bp

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    row = get_user_by_id(user_id)
    if row:
        return User(
            row["id"],
            row["username"],
            row["email"],
            row["first_name"],
            row["last_name"],
            row["role"],
        )
    return None


app.register_blueprint(home_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(quest_bp)
app.register_blueprint(profile_bp)


if __name__ == "__main__":
    app.run(debug=True)