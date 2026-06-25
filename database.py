import sqlite3
from datetime import datetime

DB_FILE = 'persona_ai.db'

def init_db():
    """Creates the database file and table if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            persona TEXT,
            user_message TEXT,
            ai_response TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_chat(persona, user_msg, ai_res):
    """Saves a conversation round into the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO chat_history (persona, user_message, ai_response, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (persona, user_msg, ai_res, current_time))
    conn.commit()
    conn.close()

def get_all_chats():
    """Retrieves all stored chat histories from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT persona, user_message, ai_response, timestamp FROM chat_history ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows