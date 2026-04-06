import uuid
from flask import Flask, request, jsonify, render_template, session
from ai.brain import Brain
from database import db

app = Flask(__name__)
app.secret_key = "ai_learn_secret_change_in_production"

brain = Brain()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_session_id() -> str:
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    return session["session_id"]


# ---------------------------------------------------------------------------
# Páginas
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    user_input = (data.get("message") or "").strip()

    if not user_input:
        return jsonify({"error": "Mensagem vazia"}), 400

    session_id = get_session_id()
    result = brain.respond(user_input)

    if result["known"]:
        conv_id = db.save_conversation(
            user_input=user_input,
            ai_response=result["response"],
            session_id=session_id,
            pattern_id=result["pattern_id"],
            confidence=result["confidence"],
            learned_here=False,
        )
        return jsonify({
            "known":       True,
            "response":    result["response"],
            "confidence":  round(result["confidence"] * 100),
            "pattern_id":  result["pattern_id"],
            "conv_id":     conv_id,
        })

    return jsonify({
        "known":      False,
        "response":   None,
        "confidence": round(result["confidence"] * 100),
    })


@app.route("/api/learn", methods=["POST"])
def learn():
    data = request.get_json(force=True)
    user_input    = (data.get("user_input") or "").strip()
    correct       = (data.get("correct_response") or "").strip()

    if not user_input or not correct:
        return jsonify({"error": "Dados incompletos"}), 400

    session_id = get_session_id()
    pattern_id = brain.learn(user_input, correct)

    db.save_conversation(
        user_input=user_input,
        ai_response=correct,
        session_id=session_id,
        pattern_id=pattern_id,
        confidence=1.0,
        learned_here=True,
    )

    return jsonify({"ok": True, "pattern_id": pattern_id})


@app.route("/api/feedback", methods=["POST"])
def feedback():
    data    = request.get_json(force=True)
    conv_id = data.get("conv_id")
    rating  = data.get("rating")  # 1 ou -1

    if not conv_id or rating not in (1, -1):
        return jsonify({"error": "Dados inválidos"}), 400

    db.save_feedback(
        conversation_id=conv_id,
        rating=rating,
        pattern_id=data.get("pattern_id"),
    )
    return jsonify({"ok": True})


@app.route("/api/stats")
def stats():
    s = brain.stats()
    return jsonify({
        "total_patterns": s["total_patterns"],
        "threshold":      int(s["threshold"] * 100),
        "ready":          s["ready"],
    })


@app.route("/api/history")
def history():
    convs = db.get_recent_conversations(20)
    result = []
    for c in convs:
        result.append({
            "user_input":   c["user_input"],
            "ai_response":  c["ai_response"],
            "confidence":   round((c["confidence"] or 0) * 100),
            "learned_here": c["learned_here"],
            "created_at":   str(c["created_at"])[:16],
        })
    return jsonify(result)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from database.db import test_connection
    if not test_connection():
        print("✗ Sem conexão com o banco. Verifique o .env")
    else:
        print("✓ Banco conectado. Servidor iniciando em http://localhost:5000")
        app.run(debug=True, port=5000)
