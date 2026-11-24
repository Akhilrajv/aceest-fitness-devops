import os
import sqlite3

from flask import current_app, g


def get_db():
    """Open a database connection for the current application context."""
    if "db" not in g:
        db_path = current_app.config["DATABASE"]
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")

    return g.db


def close_db(error=None):
    """Close the database connection when the request ends."""
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db(app):
    """Create the ACEest Fitness database and its tables."""
    os.makedirs(app.instance_path, exist_ok=True)

    app.config["DATABASE"] = os.path.join(
        app.instance_path, "aceest_fitness.db"
    )

    with app.app_context():
        db = get_db()

        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'Staff'
            );

            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                age INTEGER,
                height REAL,
                weight REAL,
                program TEXT,
                calories INTEGER,
                target_weight REAL,
                target_adherence INTEGER,
                membership_status TEXT DEFAULT 'Active',
                membership_end TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                week TEXT NOT NULL,
                adherence INTEGER,
                FOREIGN KEY (client_id) REFERENCES clients(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                workout_type TEXT NOT NULL,
                duration_min INTEGER,
                notes TEXT,
                FOREIGN KEY (client_id) REFERENCES clients(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workout_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                sets INTEGER,
                reps INTEGER,
                weight REAL,
                FOREIGN KEY (workout_id) REFERENCES workouts(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                weight REAL,
                waist REAL,
                bodyfat REAL,
                FOREIGN KEY (client_id) REFERENCES clients(id)
                    ON DELETE CASCADE
            );
            """
        )

        db.commit()

    app.teardown_appcontext(close_db)
