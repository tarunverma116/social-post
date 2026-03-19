from flask import Flask, render_template, request, redirect, session, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from model.users import Users, db
from model.posts import Post
from form import RegisterForm
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key_here"

# ✅ DATABASE CONFIG (Render Ready)
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ✅ INIT DB
db.init_app(app)

with app.app_context():
    db.create_all()

# ✅ LOGIN MANAGER
loginmanager = LoginManager()
loginmanager.init_app(app)
loginmanager.login_view = "login"


@loginmanager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# =========================
# 🔥 AUTH ROUTES
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # 🚨 Prevent duplicate usernames
        existing_user = Users.query.filter_by(username=username).first()
        if existing_user:
            return render_template("register.html", form=form, error="Username already exists")

        user = Users(username=username, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard", user_id=current_user.id))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = Users.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard", user_id=user.id))

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect("/login")


# =========================
# 🔥 DASHBOARD + POSTS
# =========================

@app.route("/dashboard<int:user_id>")
@login_required
def dashboard(user_id):
    posts = Post.query.order_by(Post.created_at.desc()).all()

    return render_template(
        "dashboard.html",
        user_id=user_id,
        current_user=current_user,
        posts=posts
    )


@app.route("/create_post", methods=["POST"])
@login_required
def create_post():
    content = request.form.get("content")

    if content:
        new_post = Post(
            content=content,
            user_id=current_user.id
        )
        db.session.add(new_post)
        db.session.commit()

    return redirect(url_for("dashboard", user_id=current_user.id))


# =========================
# 🔥 PROFILE (ONLY CURRENT USER)
# =========================

@app.route("/fetch_all")
@login_required
def fetch_all():
    return render_template("fetch_all_users.html", user=current_user)


# =========================
# 🔥 OPTIONAL (KEEP OR REMOVE)
# =========================

@app.route("/update_email/<int:user_id>", methods=["POST", "GET"])
@login_required
def update_email(user_id):
    if request.method == "POST":
        new_email = request.form.get("new_email")
        user = Users.query.get(user_id)

        if user:
            user.email = new_email
            db.session.commit()
            return redirect(url_for("dashboard", user_id=user_id))

    user = Users.query.get(user_id)
    return render_template("update_email.html", user=user)


@app.route("/delete_account/<int:user_id>", methods=["POST"])
@login_required
def delete_account(user_id):
    user = Users.query.get(user_id)

    if user:
        db.session.delete(user)
        db.session.commit()

    logout_user()
    return redirect("/login")


# =========================
# 🔥 ROOT ROUTE (OPTIONAL)
# =========================

@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard", user_id=current_user.id))
    return redirect("/login")


# =========================
# 🚀 RUN
# =========================

if __name__ == "__main__":
    app.run(debug=True)