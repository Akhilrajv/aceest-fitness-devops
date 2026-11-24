import sqlite3

from flask import Flask, render_template, request, redirect, url_for, flash
from database import init_db, get_db

app = Flask(__name__)
app.secret_key = "aceest-fitness-devops-key"

init_db(app)

PROGRAMS = {
    "Fat Loss (FL)": {
        "workout": (
            "Mon: 5x5 Back Squat + AMRAP\n"
            "Tue: EMOM 20min Assault Bike\n"
            "Wed: Bench Press + 21-15-9\n"
            "Thu: 10RFT Deadlifts/Box Jumps\n"
            "Fri: 30min Active Recovery"
        ),
        "diet": (
            "B: 3 Egg Whites + Oats Idli\n"
            "L: Grilled Chicken + Brown Rice\n"
            "D: Fish Curry + Millet Roti\n"
            "Target: 2,000 kcal"
        ),
        "color": "#e74c3c",
    },
    "Muscle Gain (MG)": {
        "workout": (
            "Mon: Squat 5x5\n"
            "Tue: Bench 5x5\n"
            "Wed: Deadlift 4x6\n"
            "Thu: Front Squat 4x8\n"
            "Fri: Incline Press 4x10\n"
            "Sat: Barbell Rows 4x10"
        ),
        "diet": (
            "B: 4 Eggs + PB Oats\n"
            "L: Chicken Biryani (250g Chicken)\n"
            "D: Mutton Curry + Jeera Rice\n"
            "Target: 3,200 kcal"
        ),
        "color": "#2ecc71",
    },
    "Beginner (BG)": {
        "workout": (
            "Circuit Training: Air Squats, Ring Rows, Push-ups.\n"
            "Focus: Technique Mastery & Form (90% Threshold)"
        ),
        "diet": (
            "Balanced Tamil Meals: Idli-Sambar, Rice-Dal, Chapati.\n"
            "Protein: 120g/day"
        ),
        "color": "#3498db",
    },
}

GYM_METRICS = {
    "capacity": "150 Users",
    "area": "10,000 sq ft",
    "break_even": "250 Members",
}

@app.route("/clients/add", methods=["POST"])
def add_client():
    name = request.form.get("name", "").strip()
    age = request.form.get("age", "").strip()
    height = request.form.get("height", "").strip()
    weight = request.form.get("weight", "").strip()
    program = request.form.get("program", "").strip()

    if not name or not age or not height or not weight or program not in PROGRAMS:
        flash("Please complete all fields and select a valid program.")
        return redirect(url_for("index"))

    try:
        age = int(age)
        height = float(height)
        weight = float(weight)

        if age <= 0 or age > 120 or height <= 0 or weight <= 0:
            raise ValueError

    except ValueError:
        flash("Please enter valid age, height and weight values.")
        return redirect(url_for("index"))

    db = get_db()

    try:
        db.execute(
            """
            INSERT INTO clients (name, age, height, weight, program)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, age, height, weight, program),
        )
        db.commit()
        flash("Client registered successfully!")

    except sqlite3.IntegrityError:
        flash("A client with this name already exists.")

    return redirect(url_for("index"))
@app.route("/")
def index():
    selected = request.args.get("program", "")
    if selected not in PROGRAMS:
        selected = ""

    db = get_db()
    clients = db.execute(
        """
        SELECT id, name, age, height, weight, program
        FROM clients
        ORDER BY id DESC
        """
    ).fetchall()

    return render_template(
        "index.html",
        programs=PROGRAMS,
        selected=selected,
        program_data=PROGRAMS.get(selected),
        gym_metrics=GYM_METRICS,
        clients=clients,
    )
@app.route("/clients/<int:client_id>")
def client_profile(client_id):
    db = get_db()

    client = db.execute(
        """
        SELECT id, name, age, height, weight, program
        FROM clients
        WHERE id = ?
        """,
        (client_id,),
    ).fetchone()

    if client is None:
        flash("Client not found.")
        return redirect(url_for("index"))

    program_data = PROGRAMS.get(client["program"])

    return render_template(
        "client_profile.html",
        client=client,
        program_data=program_data,
    )
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
