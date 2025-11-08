from flask import Flask, render_template, request, redirect, flash
import psycopg
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # replace with your own secure key

# Get database URL from Render environment variable
db_url = os.getenv("DATABASE_URL")

# Initialize the database (create table if not exists)
def init_db():
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS subscribers (
                    id SERIAL PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL
                );
            """)
        conn.commit()

# Run DB setup once on startup
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
        with psycopg.connect(db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO subscribers (email) VALUES (%s);", (email,))
            conn.commit()
        flash("Thank you! You’ll be notified when we launch 🎉")

    except psycopg.errors.UniqueViolation:
        flash("This email is already subscribed.")
    except Exception as e:
        flash(f"Something went wrong: {e}")

    return redirect("/")

if __name__ == "__main__":
    # Run the Flask app (Render automatically binds to 0.0.0.0 and PORT)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
