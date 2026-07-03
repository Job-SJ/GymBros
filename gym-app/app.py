from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
db = SQLAlchemy()

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Log eerst in om deze pagina te bekijken."
login_manager.login_message_category = "warning"

from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    return "GymBros werkt!"


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not email or not password:
            flash("Vul alle velden in.", "danger")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("Wachtwoord moet minimaal 6 tekens lang zijn.", "danger")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Wachtwoorden komen niet overeen.", "danger")
            return redirect(url_for("register"))

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            flash("Gebruikersnaam of e-mail bestaat al.", "danger")
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)

        new_user = User(
            username=username,
            email=email,
            password=password_hash
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Account succesvol aangemaakt. Je kunt nu inloggen.", "success")
        return redirect(url_for("register"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash("E-mail of wachtwoord is onjuist.", "danger")
            return redirect(url_for("login"))

        login_user(user)
        flash("Je bent succesvol ingelogd.", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return f"Welkom {current_user.username}!"


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Je bent uitgelogd.", "success")
    return redirect(url_for("login"))