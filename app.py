import json
import os
import random
import sqlite3
from datetime import datetime
from flask import Flask, jsonify, redirect, render_template, request, url_for

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-me")

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def rows(sql, params=()):
    with db() as conn:
        return conn.execute(sql, params).fetchall()

def one(sql, params=()):
    with db() as conn:
        return conn.execute(sql, params).fetchone()

def execute(sql, params=()):
    with db() as conn:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.lastrowid

def current_user():
    return 1

def ensure_db():
    if not os.path.exists(DB_PATH):
        import seed_database
        seed_database.seed()

@app.context_processor
def template_globals():
    return {"active": request.path}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/topics")
def topics():
    return redirect("/a1")

@app.route("/a1")
@app.route("/a2")
def level():
    level_name = request.path.strip("/").upper()
    topic_rows = rows("""SELECT t.*, COUNT(w.id) word_count FROM topics t
        LEFT JOIN words w ON w.topic_id=t.id WHERE t.level=?
        GROUP BY t.id ORDER BY t.id""", (level_name,))
    return render_template("topics.html", level=level_name, topics=topic_rows)

@app.route("/vocabulary")
def vocabulary():
    return redirect("/a1")

@app.route("/vocabulary/topic/<int:topic_id>")
def topic_detail(topic_id):
    topic = one("SELECT * FROM topics WHERE id=?", (topic_id,))
    if not topic:
        return ("Not found", 404)
    words = rows("SELECT * FROM words WHERE topic_id=? ORDER BY id", (topic_id,))
    return render_template("topic_detail.html", topic=topic, words=words)

@app.route("/vocabulary/quiz/<int:topic_id>")
def quiz(topic_id):
    topic = one("SELECT * FROM topics WHERE id=?", (topic_id,))
    if not topic:
        return ("Not found", 404)
    words = [dict(row) for row in rows("SELECT * FROM words WHERE topic_id=? ORDER BY id", (topic_id,))]
    return render_template("quiz.html", topic=topic, words=words, mode="practice")

@app.route("/exams")
def exams():
    return render_template("exams.html")

@app.route("/exam/<level_name>/<int:exam_number>")
def exam(level_name, exam_number):
    level_name = level_name.upper()
    if level_name not in ("A1", "A2") or exam_number not in (1, 2, 3):
        return ("Not found", 404)
    topic_rows = rows("SELECT id FROM topics WHERE level=? ORDER BY id", (level_name,))
    words = []
    for topic_row in topic_rows:
        words.extend(dict(row) for row in rows(
            "SELECT * FROM words WHERE topic_id=? ORDER BY id LIMIT 2", (topic_row["id"],)))
    extras = [dict(row) for row in rows("SELECT * FROM words WHERE level=? ORDER BY id", (level_name,))]
    random.Random(f"extras-{level_name}-{exam_number}").shuffle(extras)
    words.extend(extras[:10])
    random.Random(f"{level_name}-{exam_number}").shuffle(words)
    return render_template("quiz.html", topic={"name": f"{level_name} Practice Exam {exam_number}", "level": level_name},
                           words=words[:50], mode="exam", exam_number=exam_number)

@app.route("/result/<int:result_id>")
def result(result_id):
    result_row = one("SELECT * FROM quiz_results WHERE id=? AND user_id=?", (result_id, current_user()))
    return render_template("result.html", result=result_row) if result_row else ("Not found", 404)

@app.route("/review")
def review():
    mistakes = rows("""SELECT w.*, rw.attempts, rw.correct_count FROM review_words rw
        JOIN words w ON w.id=rw.word_id WHERE rw.user_id=? ORDER BY rw.updated_at DESC""", (current_user(),))
    return render_template("review.html", mistakes=mistakes)

@app.route("/progress")
def progress():
    return render_template("progress.html")

@app.route("/word/<int:word_id>")
def word(word_id):
    item = one("""SELECT w.*, t.name topic FROM words w JOIN topics t ON t.id=w.topic_id
        WHERE w.id=?""", (word_id,))
    return render_template("vocabulary.html", word=item) if item else ("Not found", 404)

@app.route("/search")
def search():
    term = request.args.get("q", "").strip()
    like = f"%{term}%"
    results = rows("""SELECT w.*, t.name topic FROM words w JOIN topics t ON t.id=w.topic_id
        WHERE ?='' OR w.german LIKE ? OR w.english LIKE ? OR t.name LIKE ?
        ORDER BY w.level, t.name, w.german LIMIT 50""", (term, like, like, like))
    return render_template("search.html", results=results, q=term)

@app.post("/api/answer")
def answer():
    data = request.get_json(silent=True) or {}
    item_id = int(data.get("item_id", 0))
    answer_text = str(data.get("answer", ""))
    item = one("SELECT * FROM words WHERE id=?", (item_id,))
    if not item:
        return jsonify(error="Word not found"), 404
    question_type = data.get("question_type", "meaning")
    if question_type == "german":
        correct_answer = item["german"]
    elif question_type == "article":
        correct_answer = item["article"] or ""
    else:
        correct_answer = item["english"]
    correct = answer_text == correct_answer
    now = datetime.utcnow().isoformat()
    execute("""INSERT INTO user_answers(user_id,item_type,item_id,selected_answer,correct,answered_at)
        VALUES(?,?,?,?,?,?)""", (current_user(), "vocabulary", item_id, answer_text, int(correct), now))
    execute("""INSERT INTO progress(user_id,item_type,item_id,correct_count,wrong_count,last_seen)
        VALUES(?,?,?,?,?,?) ON CONFLICT(user_id,item_type,item_id) DO UPDATE SET
        correct_count=correct_count+excluded.correct_count,
        wrong_count=wrong_count+excluded.wrong_count,last_seen=excluded.last_seen""",
        (current_user(), "vocabulary", item_id, int(correct), int(not correct), now))
    if not correct:
        execute("""INSERT INTO review_words(user_id,word_id,attempts,correct_count,updated_at)
            VALUES(?,?,?,?,?) ON CONFLICT(user_id,word_id) DO UPDATE SET attempts=attempts+1,
            correct_count=correct_count+excluded.correct_count,updated_at=excluded.updated_at""",
            (current_user(), item_id, 1, 0, now))
    return jsonify(correct=correct, correct_answer=correct_answer, item=dict(item))

@app.post("/api/quiz-result")
def quiz_result():
    data = request.get_json(silent=True) or {}
    total = max(1, int(data.get("total", 1)))
    score = max(0, min(total, int(data.get("score", 0))))
    result_id = execute("""INSERT INTO quiz_results(user_id,quiz_type,level,topic_id,score,total,accuracy,
        duration_seconds,created_at,exam_number) VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (current_user(), data.get("quiz_type", "practice"), data.get("level", ""),
         data.get("topic_id"), score, total, round(score * 100 / total, 1),
         int(data.get("duration", 0)), datetime.utcnow().isoformat(), data.get("exam_number")))
    return jsonify(redirect=url_for("result", result_id=result_id))

@app.get("/api/progress")
def api_progress():
    total = one("SELECT COUNT(*) n FROM words")["n"]
    practiced = one("""SELECT COUNT(DISTINCT item_id) n FROM user_answers
        WHERE user_id=? AND item_type='vocabulary'""", (current_user(),))["n"]
    mastered = one("""SELECT COUNT(*) n FROM progress WHERE user_id=? AND item_type='vocabulary'
        AND correct_count>=3""", (current_user(),))["n"]
    correct = one("SELECT COALESCE(SUM(correct),0) n FROM user_answers WHERE user_id=?", (current_user(),))["n"]
    answered = one("SELECT COUNT(*) n FROM user_answers WHERE user_id=?", (current_user(),))["n"]
    exams_done = one("SELECT COUNT(*) n FROM quiz_results WHERE user_id=? AND quiz_type='exam'", (current_user(),))["n"]
    best = one("SELECT COALESCE(MAX(accuracy),0) n FROM quiz_results WHERE user_id=? AND quiz_type='exam'", (current_user(),))["n"]
    return jsonify(total=total, practiced=practiced, mastered=mastered,
                   accuracy=round(correct * 100 / answered, 1) if answered else 0,
                   exams_completed=exams_done, best_exam_score=best)

ensure_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
