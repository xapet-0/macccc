import os
import random
from datetime import date, datetime, timedelta

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from werkzeug.utils import secure_filename

from models import DailyLog, Log, Loot, Player, Quest, db


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_ROOT = os.path.join(BASE_DIR, "uploads")
SUBJECT_DIR = os.path.join(UPLOAD_ROOT, "subjects")
LOOT_DIR = os.path.join(UPLOAD_ROOT, "loot")


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'mariam.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "mariam-dev-key")

db.init_app(app)


def init_db() -> None:
    with app.app_context():
        db.create_all()


def seed_dummy_data() -> None:
    with app.app_context():
        if Player.query.first():
            return

        player = Player(
            name="Mariam",
            level=1,
            xp=0,
            hp=100,
            mana=100,
            rank="E",
            wallet=0,
            black_hole_days=100,
            daily_target_hours=17.0,
        )
        quest_chain = [
            Quest(
                title="Awaken the System",
                rank="E",
                status="ACTIVE",
                xp_reward=50,
                subject_file="",
                eval_script="",
                graph_x=80,
                graph_y=140,
            ),
            Quest(
                title="Stabilize the Core",
                rank="D",
                status="LOCKED",
                xp_reward=75,
                subject_file="",
                eval_script="",
                graph_x=280,
                graph_y=80,
            ),
            Quest(
                title="Architect's Trial",
                rank="C",
                status="LOCKED",
                xp_reward=120,
                subject_file="",
                eval_script="",
                graph_x=480,
                graph_y=180,
            ),
        ]

        db.session.add(player)
        db.session.add_all(quest_chain)
        db.session.flush()

        for quest in quest_chain:
            db.session.add(
                Loot(
                    quest_id=quest.id,
                    name=f"Loot for {quest.title}",
                    file_path="",
                    is_locked=True,
                )
            )

        db.session.commit()


@app.route("/")
def index():
    return redirect(url_for("dashboard"))


@app.route("/architect", methods=["GET", "POST"])
def architect():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        rank = request.form.get("rank", "E")
        xp_reward = int(request.form.get("xp_reward", 0) or 0)
        graph_x = int(request.form.get("graph_x", 0) or 0)
        graph_y = int(request.form.get("graph_y", 0) or 0)

        subject_file = request.files.get("subject_file")
        loot_file = request.files.get("loot_file")

        subject_path = ""
        loot_path = ""

        if subject_file and subject_file.filename:
            filename = secure_filename(subject_file.filename)
            subject_path = os.path.join("subjects", filename)
            subject_file.save(os.path.join(SUBJECT_DIR, filename))

        if loot_file and loot_file.filename:
            filename = secure_filename(loot_file.filename)
            loot_path = os.path.join("loot", filename)
            loot_file.save(os.path.join(LOOT_DIR, filename))

        quest = Quest(
            title=title,
            rank=rank,
            status="LOCKED",
            xp_reward=xp_reward,
            subject_file=subject_path,
            eval_script="",
            graph_x=graph_x,
            graph_y=graph_y,
        )
        db.session.add(quest)
        db.session.flush()

        loot = Loot(
            quest_id=quest.id,
            name=f"Loot for {title or 'Quest'}",
            file_path=loot_path,
            is_locked=True,
        )
        db.session.add(loot)
        db.session.commit()

        return redirect(url_for("architect"))

    return render_template("architect.html")


@app.route("/dashboard")
def dashboard():
    player = Player.query.first()
    quests = Quest.query.order_by(Quest.graph_x.asc()).all()
    if player:
        calculate_black_hole(player)
    edges = []
    for idx in range(len(quests) - 1):
        edges.append((quests[idx], quests[idx + 1]))
    heatmap_data = get_heatmap_data()
    heatmap_days = build_heatmap_days(90, heatmap_data)
    return render_template(
        "dashboard.html",
        player=player,
        quests=quests,
        edges=edges,
        heatmap_days=heatmap_days,
    )


@app.route("/download_subject/<int:quest_id>")
def download_subject(quest_id: int):
    quest = Quest.query.get_or_404(quest_id)
    if not quest.subject_file:
        return jsonify({"error": "No subject file"}), 404
    return send_from_directory(UPLOAD_ROOT, quest.subject_file, as_attachment=True)


@app.route("/start_session", methods=["POST"])
def start_session():
    data = request.get_json(silent=True) or {}
    quest_id = data.get("quest_id")
    if not quest_id:
        return jsonify({"error": "Missing quest_id"}), 400

    log = Log(start_time=datetime.utcnow(), activity_type=f"quest:{quest_id}")
    db.session.add(log)
    db.session.commit()

    session["active_log_id"] = log.id
    session["last_heartbeat"] = datetime.utcnow().isoformat()
    return jsonify({"log_id": log.id})


@app.route("/track_time", methods=["POST"])
def track_time():
    log_id = session.get("active_log_id")
    if not log_id:
        return jsonify({"error": "No active session"}), 400

    player = Player.query.first()
    if not player:
        return jsonify({"error": "No player"}), 404

    player.wallet += 1
    upsert_daily_log(minutes=1)
    db.session.commit()

    session["last_heartbeat"] = datetime.utcnow().isoformat()
    return jsonify({"wallet": player.wallet})


@app.route("/stop_session", methods=["POST"])
def stop_session():
    log_id = session.pop("active_log_id", None)
    if not log_id:
        return jsonify({"error": "No active session"}), 400

    log = Log.query.get_or_404(log_id)
    log.end_time = datetime.utcnow()
    duration = log.end_time - log.start_time
    log.duration_minutes = max(1, int(duration.total_seconds() // 60))
    db.session.commit()

    return jsonify({"duration_minutes": log.duration_minutes})


def evaluate_submission() -> int:
    return random.randint(50, 100)


def calculate_black_hole(player: Player) -> None:
    today = date.today()
    last_update = session.get("black_hole_updated")
    if last_update == today.isoformat():
        return
    daily_log = DailyLog.query.get(today)
    daily_hours = daily_log.total_hours if daily_log else 0.0
    if daily_hours < 4:
        player.black_hole_days = max(0, player.black_hole_days - 1)
    elif daily_hours > 10:
        player.black_hole_days += 1
    db.session.commit()
    session["black_hole_updated"] = today.isoformat()


def get_heatmap_data() -> dict[str, float]:
    cutoff = date.today() - timedelta(days=365)
    logs = DailyLog.query.filter(DailyLog.date >= cutoff).all()
    return {log.date.isoformat(): log.total_hours for log in logs}


def build_heatmap_days(days: int, heatmap_data: dict[str, float]) -> list[dict[str, str]]:
    today = date.today()
    output = []
    for offset in range(days - 1, -1, -1):
        current_day = today - timedelta(days=offset)
        key = current_day.isoformat()
        hours = heatmap_data.get(key, 0.0)
        output.append(
            {
                "date": key,
                "level": heatmap_level(hours),
            }
        )
    return output


def heatmap_level(hours: float) -> str:
    if hours >= 10:
        return "level-4"
    if hours >= 5:
        return "level-3"
    if hours >= 2:
        return "level-2"
    if hours > 0:
        return "level-1"
    return "level-0"


def upsert_daily_log(minutes: int) -> None:
    today = date.today()
    daily_log = DailyLog.query.get(today)
    increment = minutes / 60
    if daily_log:
        daily_log.total_hours += increment
    else:
        daily_log = DailyLog(date=today, total_hours=increment)
        db.session.add(daily_log)
    daily_log.status = status_for_hours(daily_log.total_hours)


def status_for_hours(hours: float) -> str:
    if hours >= 10:
        return "BURNING"
    if hours >= 4:
        return "ACTIVE"
    return "FROZEN"


@app.route("/submit_quest/<int:quest_id>", methods=["POST"])
def submit_quest(quest_id: int):
    quest = Quest.query.get_or_404(quest_id)
    file = request.files.get("submission")
    if not file or not file.filename:
        return jsonify({"error": "Missing submission file"}), 400

    score = evaluate_submission()
    player = Player.query.first()
    if not player:
        return jsonify({"error": "No player"}), 404

    if score > 80:
        quest.status = "COMPLETED"
        if quest.loot:
            quest.loot.is_locked = False
        player.xp += quest.xp_reward
        response = {"result": "success", "score": score}
    else:
        player.hp = max(0, player.hp - 10)
        response = {"result": "failure", "score": score}

    db.session.commit()
    return jsonify(response)


if __name__ == "__main__":
    os.makedirs(SUBJECT_DIR, exist_ok=True)
    os.makedirs(LOOT_DIR, exist_ok=True)
    init_db()
    seed_dummy_data()
    app.run(host="0.0.0.0", port=5000, debug=True)
