import os
import sqlite3

from modl import app


def test_unit_route_loads():
    db_path = os.path.join(os.path.dirname(__file__), "database", "classes.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO classes (id, class_name) VALUES (999, 'Test Class')")
    cursor.execute("INSERT OR IGNORE INTO units (id, class_id, unit_name) VALUES (999, 999, 'Test Unit')")
    conn.commit()
    conn.close()

    client = app.test_client()
    response = client.get('/unit/999')
    assert response.status_code == 200
    assert b'Test Unit' in response.data


def test_delete_note_removes_note():
    db_path = os.path.join(os.path.dirname(__file__), "database", "classes.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO classes (id, class_name) VALUES (1000, 'Delete Test Class')")
    cursor.execute("INSERT OR IGNORE INTO units (id, class_id, unit_name) VALUES (1000, 1000, 'Delete Test Unit')")
    cursor.execute("INSERT INTO notes (unit_id, notes_name) VALUES (?, ?)", (1000, 'Delete me'))
    note_id = cursor.execute("SELECT id FROM notes WHERE unit_id = 1000 AND notes_name = 'Delete me'").fetchone()[0]
    conn.commit()
    conn.close()

    client = app.test_client()
    response = client.post(f'/delete-note/{note_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Delete me' not in response.data

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    remaining = cursor.execute("SELECT COUNT(*) FROM notes WHERE id = ?", (note_id,)).fetchone()[0]
    conn.close()
    assert remaining == 0
