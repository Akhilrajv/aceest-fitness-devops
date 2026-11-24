import pytest
import sqlite3
import re

from app import app, PROGRAMS, GYM_METRICS


@pytest.fixture
def client(tmp_path):
    # Save the original application settings.
    original_database = app.config["DATABASE"]
    original_testing = app.config.get("TESTING", False)

    # Create a separate temporary database for this test.
    test_database = tmp_path / "test_aceest.db"

    # Copy the database table structure, but not its client records.
    source = sqlite3.connect(original_database)
    destination = sqlite3.connect(test_database)

    schema = source.execute(
        """
        SELECT sql
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
        AND sql IS NOT NULL
        ORDER BY name
        """
    ).fetchall()

    for statement in schema:
        destination.execute(statement[0])

    destination.commit()
    source.close()
    destination.close()

    # Configure Flask to use the temporary database.
    app.config["DATABASE"] = str(test_database)
    app.config["TESTING"] = True

    try:
        with app.test_client() as test_client:
            yield test_client
    finally:
        # Restore the original application settings.
        app.config["DATABASE"] = original_database
        app.config["TESTING"] = original_testing

def get_csrf_token(client):
    response = client.get("/")
    match = re.search(
        rb'name="csrf_token" value="([^"]+)"',
        response.data,
    )
    assert match is not None
    return match.group(1).decode()
def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"ACEest FUNCTIONAL FITNESS" in response.data


def test_all_programs_are_available(client):
    response = client.get("/")
    assert response.status_code == 200

    for program in PROGRAMS:
        assert program.encode() in response.data


def test_fat_loss_program(client):
    response = client.get("/?program=Fat%20Loss%20(FL)")
    assert response.status_code == 200
    assert b"Back Squat" in response.data
    assert b"2,000 kcal" in response.data


def test_muscle_gain_program(client):
    response = client.get("/?program=Muscle%20Gain%20(MG)")
    assert response.status_code == 200
    assert b"Deadlift 4x6" in response.data
    assert b"3,200 kcal" in response.data


def test_beginner_program(client):
    response = client.get("/?program=Beginner%20(BG)")
    assert response.status_code == 200
    assert b"Circuit Training" in response.data
    assert b"120g/day" in response.data


def test_gym_metrics_are_displayed(client):
    response = client.get("/")
    assert response.status_code == 200

    for metric in GYM_METRICS.values():
        assert metric.encode() in response.data


def test_invalid_program_does_not_crash(client):
    response = client.get("/?program=Unknown")
    assert response.status_code == 200
    assert b"Select a program to view its workout" in response.data


def test_csrf_protection_rejects_missing_token(client):
    response = client.post(
        "/clients/add",
        data={
            "name": "No Token Client",
            "age": "25",
            "height": "175",
            "weight": "70",
            "program": "Fat Loss (FL)",
        },
    )

    assert response.status_code == 400

def test_client_registration(client):
    csrf_token = get_csrf_token(client)

    response = client.post(
        "/clients/add",
        data={
            "csrf_token": csrf_token,
            "name": "Pytest Registration Client",
            "age": "25",
            "height": "175",
            "weight": "70",
            "program": "Fat Loss (FL)",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Client registered successfully!" in response.data

    connection = sqlite3.connect(app.config["DATABASE"])

    record = connection.execute(
        "SELECT age, height, weight, program FROM clients WHERE name = ?",
        ("Pytest Registration Client",),
    ).fetchone()

    connection.close()

    assert record == (25, 175.0, 70.0, "Fat Loss (FL)")


def test_duplicate_client_registration(client):
    connection = sqlite3.connect(app.config["DATABASE"])

    connection.execute(
        """
        INSERT OR IGNORE INTO clients (name, age, height, weight, program)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("Duplicate Test Client", 30, 170, 75, "Beginner (BG)"),
    )

    connection.commit()
    connection.close()

    csrf_token = get_csrf_token(client)

    response = client.post(
        "/clients/add",
        data={
            "csrf_token": csrf_token,
            "name": "Duplicate Test Client",
            "age": "31",
            "height": "171",
            "weight": "76",
            "program": "Beginner (BG)",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"A client with this name already exists." in response.data
def test_client_profile_displays_client_details(client):
    csrf_token = get_csrf_token(client)

    client.post(
        "/clients/add",
        data={
            "csrf_token": csrf_token,
            "name": "Profile Test Client",
            "age": "28",
            "height": "172",
            "weight": "68",
            "program": "Muscle Gain (MG)",
        },
    )

    db = sqlite3.connect(app.config["DATABASE"])
    client_id = db.execute(
        "SELECT id FROM clients WHERE name = ?",
        ("Profile Test Client",),
    ).fetchone()[0]
    db.close()

    response = client.get(f"/clients/{client_id}")

    assert response.status_code == 200
    assert b"Profile Test Client" in response.data
    assert b"Muscle Gain (MG)" in response.data
    assert b"Weekly Workout Plan" in response.data
    assert b"Nutrition Plan" in response.data


def test_client_profile_not_found_redirects(client):
    response = client.get("/clients/999", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")
