from flask import Flask, jsonify, render_template, request
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from .db import engine, session  # Import from db.py


app = Flask(__name__, template_folder="../Frontend")

# Test route to check DB connection
@app.route('/')
def index():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT NOW();"))
            current_time = result.fetchone()[0]
        return render_template("index.html", current_time=current_time)
    except Exception as e:
        return f"DB connection error: {e}"

# Example route to fetch teachers table
@app.route("/teachers")
def get_teachers():
    try:
        result = session.execute(text("SELECT * FROM teachersmondayfree;"))  # Replace 'teachers' with your table name
        teachers = [dict(row) for row in result.mappings().all()]
        return render_template("teachers.html", teachers=teachers)
    except Exception as e:
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
                        'VALUES (:p1, :p2, :p3, :p4, :p5, :p6, :p7, :p8, :p9)'
                    ),
                    {
                        "id":teach_id, "p1": period1, "p2": period2, "p3": period3,
                        "p4": period4, "p5": period5, "p6": period6,
                        "p7": period7, "p8": period8, "p9": period9
                    }
                )
                session.commit()
                message = "Teacher free periods added successfully!"
                message_type = "success"
        except Exception as e:
                message =  f"DB error: {e}"
                message_type = "error"
    
    return render_template("teachersadd.html", message=message, message_type=message_type)



if __name__ == '__main__':
    app.run(debug=True)
