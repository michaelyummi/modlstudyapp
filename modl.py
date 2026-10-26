import os
import json
import sqlite3
from flask import Flask, redirect, url_for, render_template, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)


def get_db_connection():
    db_dir = os.path.join(BASE_DIR, "database")
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, "classes.db")
    return sqlite3.connect(db_path, timeout=30)


#database logic
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS units(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL,
            unit_name TEXT NOT NULL,
            FOREIGN KEY (class_id) REFERENCES classes (id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unit_id INTEGER NOT NULL,
            notes_name TEXT NOT NULL,
            FOREIGN KEY (unit_id) REFERENCES units (id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


init_db()


#home route

@app.route("/")
def home():
    db_path = os.path.join(BASE_DIR, "database", "classes.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, class_name FROM classes ORDER BY id")
    all_items = cursor.fetchall()
    conn.close()

    return render_template("index.html", items=all_items)

#adding class route

@app.route("/add-item", methods=["POST"])
def add_class():
    new_class = request.form.get("class_name") or request.form.get("item_name")

    if new_class:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO classes (class_name) VALUES (?)", (new_class,))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        conn.close()

    return redirect(url_for("home"))

#added class route(user input)

@app.route("/click-item/<int:item_id>")
def click_item(item_id):
    print(f"User clicked button for class ID: {item_id}")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT class_name FROM classes WHERE id = ?", (item_id,))
    class_result = cursor.fetchone()

    if class_result is None:
        conn.close()
        return redirect(url_for("home"))

    class_name = class_result[0]
    cursor.execute("SELECT id, unit_name FROM units WHERE class_id = ? ORDER BY id", (item_id,))
    units = cursor.fetchall()
    conn.close()

    return render_template("class.html", name=class_name, items=units, item_id=item_id)


@app.route("/click-item/<int:item_id>/add-unit", methods=["POST"])
def add_unit(item_id):
    unit_name = request.form.get('unit_name') or request.form.get('unit_title')
    if not unit_name:
        return redirect(url_for('click_item', item_id=item_id))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO units (class_id, unit_name) VALUES (?, ?)", (item_id, unit_name))
    conn.commit()
    conn.close()

    print("New Unit/Topic Added to class")
    return redirect(url_for('click_item', item_id=item_id))


#directs to specific unit information(bulk of the data)
#allows user input of notes for each unit

@app.route("/unit/<int:unit_id>")
def view_unit(unit_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT class_id, unit_name FROM units WHERE id = ?", (unit_id,))
    unit = cursor.fetchone()

    if unit is None:
        conn.close()
        return redirect(url_for("home"))

    class_id, unit_name = unit
    cursor.execute("SELECT id, notes_name FROM notes WHERE unit_id = ? ORDER BY id", (unit_id,))
    notes = cursor.fetchall()
    conn.close()

    return render_template("unit.html", name=unit_name, item_id=class_id, unit_id=unit_id, unit_name=unit_name, items=notes)


@app.route("/unit-notes/<int:unit_id>", methods=["POST"])
def get_notes(unit_id):
    notes_name = request.form.get('notes_name') or request.form.get('class_name') or request.form.get('unit_title')

    if not notes_name:
        return redirect(url_for('view_unit', unit_id=unit_id))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notes (unit_id, notes_name) VALUES (?, ?)", (unit_id, notes_name))
    conn.commit()
    conn.close()

    return redirect(url_for('view_unit', unit_id=unit_id))


#remove notes function for notes page

@app.route("/delete-note/<int:note_id>", methods=["POST"])
def remove_notes(note_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT unit_id FROM notes WHERE id = ?", (note_id,))
    note = cursor.fetchone()

    if note is not None:
        unit_id = note[0]
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('view_unit', unit_id=unit_id))

    conn.close()
    return redirect(url_for('home'))
    

#go back to home page from individual class page
#to do: build function to direct user from individual class page to home page

@app.route("/home-page", methods=["GET", "POST"])
def home_page():
    print("User redirected to home page")
    return redirect(url_for("home"))

#reroutes user from unit/notes page to previous class page
@app.route("/last-class/<int:item_id>", methods=["GET", "POST"])
def last_class(item_id):
    print("User redirect to last class page")
    return redirect(url_for('click_item', item_id=item_id))

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)