from flask import Flask, jsonify, render_template, request,redirect, url_for, session
import os
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from .db import engine, session as db_session  # Import from db.py
import pandas as pd
from datetime import datetime


app = Flask(__name__, template_folder="../Frontend")
app.secret_key= "shaun"

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
            with Session() as session:
                session.execute(
                    text(
                        'INSERT INTO teachersmondayfree ("id", "Period 1", "Period 2", "Period 3", "Period 4", "Period 5", "Period 6", "Period 7", "Period 8", "Period 9") '
                        'VALUES (:id, :p1, :p2, :p3, :p4, :p5, :p6, :p7, :p8, :p9)'
                    ),
                    {
                        "id":teach_id, "p1": period1, "p2": period2, "p3": period3,
                        "p4": period4, "p5": period5, "p6": period6,
                        "p7": period7, "p8": period8, "p9": period9
                    }
                )
                db_session.commit()
                message = "Teacher free periods added successfully!"
                message_type = "success"
        except Exception as e:
                message =  f"DB error: {e}"
                message_type = "error"
    
    return render_template("teachersadd.html", message=message, message_type=message_type)
    
#MONDAY

@app.route("/teacherstimetable")
def get_teacherstimetable_monday():
    try:
        result = db_session.execute(text("SELECT * FROM teachertimetable_monday;"))  # Replace 'teachers' with your table name
        teachers = [dict(row) for row in result.mappings().all()]
        return render_template("teacherstimetable.html", teachers=teachers)
    except Exception as e:
        session.rollback()
        return f"DB connection error: {e}"
    
#TUESDAY

@app.route("/teacherstimetable")
def get_teacherstimetable_tuesday():
    try:
        result = db_session.execute(text("SELECT * FROM teachertimetable_tuesday;"))  # Replace 'teachers' with your table name
        teachers = [dict(row) for row in result.mappings().all()]
        return render_template("teacherstimetable.html", teachers=teachers)
    except Exception as e:
        session.rollback()
        return f"DB connection error: {e}"
    
#WEDNESDAY

@app.route("/teacherstimetable")
def get_teacherstimetable_wednesday():
    try:
        result = db_session.execute(text("SELECT * FROM teachertimetable_wednesday;"))  # Replace 'teachers' with your table name
        teachers = [dict(row) for row in result.mappings().all()]
        return render_template("teacherstimetable.html", teachers=teachers)
    except Exception as e:
        session.rollback()
        return f"DB connection error: {e}"
    
#THURSDAY

@app.route("/teacherstimetable")
def get_teacherstimetable_thursday():
    try:
        result = db_session.execute(text("SELECT * FROM teachertimetable_thursday;"))  # Replace 'teachers' with your table name
        teachers = [dict(row) for row in result.mappings().all()]
        return render_template("teacherstimetable.html", teachers=teachers)
    except Exception as e:
        session.rollback()
        return f"DB connection error: {e}"

#FRIDAY

@app.route("/teacherstimetable")
def get_teacherstimetable_friday():
    try:
        result = db_session.execute(text("SELECT * FROM teachertimetable_friday;"))  # Replace 'teachers' with your table name
        teachers = [dict(row) for row in result.mappings().all()]
        return render_template("teacherstimetable.html", teachers=teachers)
    except Exception as e:
        session.rollback()
        return f"DB connection error: {e}" 

#------------------------------------------------------------------------------------------------------------------------
#LOGIN STUFF

def check_login(email, password):
    # Path to Excel file
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
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid email or password.")
    
    if "user" in session and session.get("role") == "user":
        return redirect(url_for("dashboard"))
    
    return render_template("login.html")

    if "user" in session and session.get("role") == "admin":
        return redirect(url_for("admin_dashboard"))
    
    return render_template("login.html")

@app.route("/admin_dashboard")
def admin_dashboard():
    if "user" not in session or session.get("role") != "admin":
        return redirect(url_for("admin_login"))
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


#________________________________________________________________________________________________________________________________________________________________

#ASSIGNING TEACHERS

def get_teacher_names_from_excel():
    excel_path = os.path.join(os.path.dirname(__file__), "tachernames.xlsx")
    df = pd.read_excel(excel_path)
    return df["name"].tolist()


@app.route("/assignteacher", methods=["GET", "POST"])
def assign_teacher():
    free_teachers_by_period = {}
    selected_day = None
    selected_date = None
    absent_teacher = None

    teacher_list = get_teacher_names_from_excel()

    if request.method == "POST":
        absent_teacher = request.form.get("absent_teacher")
        selected_date = request.form.get("date")  
        valid_days = ["monday", "tuesday", "wednesday", "thursday", "friday"]

        if not selected_date:
            return "Please select a date"

        # now safe to parse
        selected_day = datetime.strptime(selected_date, "%Y-%m-%d").strftime("%A").lower() 

        if selected_day in valid_days:
            table_name = f"teachers{selected_day}free"

            try:
                result = db_session.execute(text(f"SELECT * FROM {table_name};"))
                teachers = [dict(row) for row in result.mappings().all()]

                max_periods = 9 if selected_day != "friday" else 4

                for p in range(1, max_periods + 1):
                    period_col = f"Period {p}"
                    names = set(
                        t[period_col] for t in teachers if t.get(period_col) and t[period_col].lower() != "busy"
                    )
                    free_teachers_by_period[p] = sorted(names)

                # 🔍 Remove already assigned teachers (same day, date, period)
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

        # 📨 When SEND button clicked
        if "send_emails" in request.form:
            for period in range(1, 10):
                selected_teacher = request.form.get(f"period_{period}")
                if selected_teacher:
                    db_session.execute(
                        text("""
                            INSERT INTO assigned_subs (Date, Day, Period, AbsentTeacher, Substitute)
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
            return "Substitution assignments saved successfully!"

    return render_template(
        "assignsub.html",
        teacher_list=teacher_list,
        free_teachers_by_period=free_teachers_by_period,
        selected_day=selected_day,
        selected_date=selected_date,
        absent_teacher=absent_teacher,
    )


@app.route('/confirm_teacher', methods=['POST'])
def confirm_teacher():
    teacher = request.form.get('absent_teacher')
    session['confirmed_teacher'] = teacher
    return redirect(url_for('assign_teacher'))

@app.route('/unconfirm_teacher')
def unconfirm_teacher():
    session.pop('confirmed_teacher', None)
    return redirect(url_for('assign_teacher'))







if __name__ == '__main__':
    app.run(debug=True)
