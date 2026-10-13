import pytest

from app import app, PROGRAMS, GYM_METRICS


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


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
