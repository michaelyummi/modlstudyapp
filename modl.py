import os
import json
import sqlite3
from flask import Flask, redirect, url_for, render_template, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)


#database logic
def init_db():
    db_dir = os.path.join(BASE_DIR, "database")
    os.makedirs(db_dir, exist_ok=True)

    db_path = os.path.join(db_dir, "classes.db")
    conn = sqlite3.connect(db_path)
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
        db_path = os.path.join(BASE_DIR, "database", "classes.db")
        conn = sqlite3.connect(db_path)
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
    db_path = os.path.join(BASE_DIR, "database", "classes.db")
    conn = sqlite3.connect(db_path)
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

    db_path = os.path.join(BASE_DIR, "database", "classes.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO units (class_id, unit_name) VALUES (?, ?)", (item_id, unit_name))
    conn.commit()
    conn.close()

    print("New Unit/Topic Added to class")
    return redirect(url_for('click_item', item_id=item_id))


#directs to specific unit information(bulk of the data)
#to be completed


#go back to home page from individual class page
#to do: build function to direct user from individual class page to home page

@app.route("/home-page", methods=["GET", "POST"])
def home_page():
    print("User redirected to home page")
    return redirect(url_for("home"))


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)