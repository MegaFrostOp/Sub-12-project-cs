from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
import os
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from .db import engine, session as db_session  # Import from db.py
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__, template_folder="../Frontend")
app.secret_key = "shaun"

ADMIN_USER = "admin@mpsabudhabi.com"
ADMIN_PASSWORD = "mayooradmin@2026"

# Test route to check DB connection
@app.route('/')
def index():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT NOW();"))
            current_time = result.fetchone()[0]
        return render_template("login.html", current_time=current_time)
    except Exception as e:
        return f"DB connection error: {e}"

# Example route to fetch teachers table
@app.route("/teachers")
def get_teachers():
    try:
        result = db_session.execute(text("SELECT * FROM teachersmondayfree;"))  # Replace 'teachers' with your table name
        teachers = [dict(row) for row in result.mappings().all()]
        return render_template("teachers.html", teachers=teachers)
    except Exception as e:
        db_session.rollback()
        return f"DB connection error: {e}"

# SQLAlchemy session factory
Session = sessionmaker(bind=engine)

@app.route('/teachersadd', methods=['GET', 'POST'])
def add_free_period():

    message = None
    message_type = None

    if request.method == 'POST':
        name = request.form.get('name')
        teach_id = request.form.get('id')

        period1 = name if request.form.get('period1') == "Free" else "busy"
        period2 = name if request.form.get('period2') == "Free" else "busy"
        period3 = name if request.form.get('period3') == "Free" else "busy"
        period4 = name if request.form.get('period4') == "Free" else "busy"
        period5 = name if request.form.get('period5') == "Free" else "busy"
        period6 = name if request.form.get('period6') == "Free" else "busy"
        period7 = name if request.form.get('period7') == "Free" else "busy"
        period8 = name if request.form.get('period8') == "Free" else "busy"
        period9 = name if request.form.get('period9') == "Free" else "busy"

        try:
            with Session() as db_sess:
                db_sess.execute(
                    text(
                        'INSERT INTO teachersmondayfree ("id", "Period 1", "Period 2", "Period 3", "Period 4", "Period 5", "Period 6", "Period 7", "Period 8", "Period 9") '
                        'VALUES (:id, :p1, :p2, :p3, :p4, :p5, :p6, :p7, :p8, :p9)'
                    ),
                    {
                        "id": teach_id, "p1": period1, "p2": period2, "p3": period3,
                        "p4": period4, "p5": period5, "p6": period6,
                        "p7": period7, "p8": period8, "p9": period9
                    }
                )
                db_sess.commit()
                message = "Teacher free periods added successfully!"
                message_type = "success"
        except Exception as e:
            message = f"DB error: {e}"
            message_type = "error"

    return render_template("teachersadd.html", message=message, message_type=message_type)

#------------------------------------------------------------------------------------------------------------------------
# COMBINED TEACHER TIMETABLE ROUTE

@app.route("/teacherstimetable")
def get_teacherstimetable():
    day = request.args.get("day", "monday").lower()
    valid_days = ["monday", "tuesday", "wednesday", "thursday", "friday"]

    if day not in valid_days:
        return "Invalid day selected"

    table_name = f"teachertimetable_{day}"
    try:
        result = db_session.execute(text(f"SELECT * FROM {table_name};"))
        teachers = [dict(row) for row in result.mappings().all()]
        return render_template("teacherstimetable.html", teachers=teachers, day=day)
    except Exception as e:
        db_session.rollback()
        return f"DB connection error: {e}"

#------------------------------------------------------------------------------------------------------------------------
# LOGIN STUFF

def check_login(email, password):
    excel_path = os.path.join(os.path.dirname(__file__), "teachers.xlsx")
    df = pd.read_excel(excel_path)
    user = df[df["Email"] == email]
    return not user.empty and user.iloc[0]["password"] == password

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email == ADMIN_USER and password == ADMIN_PASSWORD:
            session["user"] = email
            session["role"] = 'admin'
            return redirect(url_for("admin_dashboard"))

        elif check_login(email, password):
            session["user"] = email
            session["role"] = "user"
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid email or password.")

    if "user" in session:
        if session.get("role") == "user":
            return redirect(url_for("dashboard"))
        elif session.get("role") == "admin":
            return redirect(url_for("admin_dashboard"))

    return render_template("login.html")

@app.route("/admin_dashboard")
def admin_dashboard():
    if "user" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))
    return render_template("adminindex.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

#------------------------------------------------------------------------------------------------------------------------
# ASSIGNING TEACHERS

def get_teacher_names_from_excel():
    excel_path = os.path.join(os.path.dirname(__file__), "tachernames.xlsx")
    df = pd.read_excel(excel_path)
    return df["name"].tolist()

@app.route("/assignteacher", methods=["GET", "POST"])
def select_absent_teacher():
    teacher_list = get_teacher_names_from_excel()
    
    if request.method == "POST":
        absent_teacher = request.form.get("absent_teacher")
        selected_date = request.form.get("date")

        if not absent_teacher or not selected_date:
            return "Please select both teacher and date."

        # Store in session to use in Page 2
        session['confirmed_teacher'] = absent_teacher
        session['selected_date'] = selected_date

        # Redirect to the second page to assign substitutes
        return redirect(url_for("assign_substitutes"))

    return render_template(
        "assignsub.html",
        teacher_list=teacher_list
    )

@app.route("/assignteacher/substitute", methods=["GET", "POST"])
def assign_substitutes():
    if "confirmed_teacher" not in session or "selected_date" not in session:
        return redirect(url_for("select_absent_teacher"))

    absent_teacher = session["confirmed_teacher"]
    selected_date = session["selected_date"]
    selected_day = datetime.strptime(selected_date, "%Y-%m-%d").strftime("%A").lower()
    free_teachers_by_period = {}

    valid_days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    if selected_day not in valid_days:
        return "Invalid day selected"

    table_name = f"teachers{selected_day}free"
    max_periods = 9 if selected_day != "friday" else 4

    try:
        # Fetch free teachers
        result = db_session.execute(text(f"SELECT * FROM {table_name};"))
        teachers = [dict(row) for row in result.mappings().all()]

        for p in range(1, max_periods + 1):
            period_col = f"Period {p}"
            names = set(
                t[period_col] for t in teachers if t.get(period_col) and t[period_col].lower() != "busy"
            )
            free_teachers_by_period[p] = sorted(names)

        # Remove already assigned teachers
        assigned_subs = db_session.execute(
            text('SELECT * FROM assigned_subs WHERE "Day" = :Day AND "Date" = :Date'),
            {"Day": selected_day, "Date": selected_date}
        ).mappings().all()

        for period, teachers in free_teachers_by_period.items():
            already_assigned = [
                sub["Substitute"] for sub in assigned_subs if sub["Period"] == period
            ]
            free_teachers_by_period[period] = [
                t for t in teachers if t not in already_assigned
            ]

    except Exception as e:
        db_session.rollback()
        return f"DB error: {e}"

    # Handle sending substitutions
    if request.method == "POST" and "send_emails" in request.form:
        try:
            for period in range(1, max_periods + 1):
                selected_teacher = request.form.get(f"period{period}")
                if not selected_teacher or selected_teacher == "-- Select Substitute --":
                    continue
                if selected_teacher:
                    db_session.execute(
                        text("""
                            INSERT INTO assigned_subs ("Date", "Day", "Period", "AbsentTeacher", "Substitute")
                            VALUES (:date, :day, :period, :absent, :sub)
                        """),
                        {
                            "date": selected_date,
                            "day": selected_day,
                            "period": period,
                            "absent": absent_teacher,
                            "sub": selected_teacher
                        }
                    )
            db_session.commit()
            for period in range(1, max_periods + 1):
                selected_teacher = request.form.get(f"period{period}")
                if not selected_teacher or selected_teacher == "-- Select Substitute --":
                    continue
                send_email_to_teacher(selected_teacher, absent_teacher, selected_date, period)
                # replace send_email_to_teacher with your actual email sending function

            # 3️⃣ Only after emails sent successfully → flash
            session.pop("confirmed_teacher")
            session.pop("selected_date")
            flash("Emails sent successfully!", "success")
            return redirect(url_for("select_absent_teacher"))
        except Exception as e:
            db_session.rollback()
            return f"DB error: {e}"

    return render_template(
        "assigntwo.html",
        free_teachers_by_period=free_teachers_by_period,
        absent_teacher=absent_teacher,
        selected_date=selected_date,
        max_periods=max_periods
    )

excel_path_foremail = os.path.join(os.path.dirname(__file__), "teachername.xlsx")
teacher_df = pd.read_excel(excel_path_foremail)  
teacher_email_map = dict(zip(teacher_df["name"], teacher_df["email"]))


def send_email_to_teacher(to_teacher, absent_teacher, date, period):
    to_email = None
    for name, email in teacher_email_map.items():
        if name.lower() == to_teacher.lower():
            to_email = email
            break

    if not to_email:
        print(f"No email found for {to_teacher}")
        return

    subject = f"Substitute Assignment for {absent_teacher} on {date}"
    body = f"You have been assigned as a substitute for {absent_teacher} on {date}, Period {period}."

    msg = MIMEMultipart()
    msg['From'] = "srinivasans@mpsabudhabi.com"
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.google.com', 587)  # replace with your SMTP
        server.starttls()
        server.login("your_school_email@example.com", "your_email_password")
        server.send_message(msg)
        server.quit()
        print(f"Email sent to {to_teacher}")
    except Exception as e:
        print(f"Failed to send email to {to_teacher}: {e}")


@app.route('/confirm_teacher', methods=['POST'])
def confirm_teacher():
    teacher = request.form.get('absent_teacher')
    session['confirmed_teacher'] = teacher
    return redirect(url_for('assign_teacher'))

@app.route('/unconfirm_teacher')
def unconfirm_teacher():
    session.pop('confirmed_teacher', None)
    return redirect(url_for('assign_teacher'))

#------------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
