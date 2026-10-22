import os
import sqlite3
from flask import Flask, redirect, url_for, render_template, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)

#database logic
def init_db():
    db_path = os.path.join(BASE_DIR, "classes.db")
    sql_path = os.path.join(BASE_DIR, "database", "modl.sql")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='classes'")

    if cursor.fetchone() is None:
        with open(sql_path, mode="r", encoding="utf-8") as f:
            sql_commands = f.read()
        cursor.executescript(sql_commands)
        conn.commit()

    conn.close()


init_db()


#home route

@app.route("/")
def home():
    conn = sqlite3.connect(os.path.join(BASE_DIR, "classes.db"))
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
        conn = sqlite3.connect(os.path.join(BASE_DIR, "classes.db"))
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO classes (class_name) VALUES (?)", (new_class,))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        conn.close()

    return redirect(url_for("home"))

#adding class route(user input)

@app.route("/click-item/<int:item_id>")
def click_item(item_id):
    print(f"User clicked button for class ID: {item_id}")
    return f"Clicked class #{item_id}. <a href='/'>Go Back</a>"


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)