from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# ----------------- MongoDB Setup -----------------
client = MongoClient("mongodb://localhost:27017/")  # Local Mongo
db = client["fitness_db"]
users_collection = db["users"]
contacts_collection = db["contacts"]

# ----------------- Routes -----------------
@app.route("/")
def home():
    # Check if logged in
    return render_template("index.html", logged_in=("user" in session), user=session.get("user"))

# Contact Form Submission
@app.route("/contact", methods=["POST"])
def contact():
    if "user" not in session:
        flash("You must be logged in to use contact form!", "error")
        return redirect(url_for("home"))

    name = request.form.get("contactName")
    email = request.form.get("contactEmail")
    message = request.form.get("message")

    contacts_collection.insert_one({"name": name, "email": email, "message": message})

    flash(f"Thank you {name}, we have received your message!", "success")
    return redirect(url_for("home"))

# Login/Signup
@app.route("/auth", methods=["POST"])
def auth():
    email = request.form.get("loginEmail")
    password = request.form.get("loginPassword")

    user = users_collection.find_one({"email": email, "password": password})

    if user:
        session["user"] = email   # Save session
        flash(f"Welcome back {email}!", "success")
        return redirect(url_for("home"))
    else:
        # If no user, create one (basic signup)
        users_collection.insert_one({"email": email, "password": password})
        session["user"] = email
        flash(f"New account created for {email}", "success")
        return redirect(url_for("home"))

# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

# ----------------- Run App -----------------
if __name__ == "__main__":
    app.run(debug=True)
