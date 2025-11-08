from flask import Flask, render_template, request, redirect, flash
import psycopg2
import os
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Get database URL from environment variable
db_url = os.getenv("DATABASE_URL")

# Parse database URL
result = urlparse(db_url)
username = result.username
password = result.password
database = result.path[1:]
hostname = result.hostname
port = result.port

# Function to get DB connection
def get_connection():
    return psycopg2.connect(
        database=database,
        user=username,
        password=password,
        host=hostname,
        port=port
    )

# Initialize DB (create table if not exists)
def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email")
    if not email:
        flash("Please enter a valid email!")
        return redirect("/")

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO subscribers (email) VALUES (%s)", (email,))
        conn.commit()
        cur.close()
        conn.close()
        flash("Thank you! You’ll be notified when we launch 🎉")
    except psycopg2.errors.UniqueViolation:
        flash("This email is already subscribed.")
    except Exception as e:
        flash(f"Something went wrong: {e}")
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
