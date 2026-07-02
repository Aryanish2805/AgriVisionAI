import sqlite3
from pathlib import Path
from datetime import datetime

# Path to the sqlite database
DB_PATH = Path(__file__).resolve().parent / "data" / "history.db"


def init_db():
    """Initialize the sqlite database and predictions table."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            N REAL,
            P REAL,
            K REAL,
            temperature REAL,
            humidity REAL,
            ph REAL,
            rainfall REAL,
            predicted_crop TEXT
        )
    ''')
    conn.commit()
    conn.close()


def save_prediction(input_data: dict, predicted_crop: str):
    """Save a prediction to the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        timestamp = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO predictions (timestamp, N, P, K, temperature, humidity, ph, rainfall, predicted_crop)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp,
            input_data.get('N'),
            input_data.get('P'),
            input_data.get('K'),
            input_data.get('temperature'),
            input_data.get('humidity'),
            input_data.get('ph'),
            input_data.get('rainfall'),
            predicted_crop
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[database] Error saving prediction: {e}")


def get_history(limit: int = 50):
    """Retrieve prediction history."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM predictions 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"[database] Error getting history: {e}")
        return []
