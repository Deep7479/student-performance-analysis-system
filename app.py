"""
Student Performance Analysis System
------------------------------------
A Flask web app that loads student marks from a CSV, computes per-student
and class-wide performance metrics with pandas/numpy, and renders
dashboards and per-student reports with matplotlib charts.
"""

import base64
import io
import os

import matplotlib
matplotlib.use("Agg")  # non-interactive backend, safe for server-side rendering
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "students.csv")
SUBJECTS = ["Mathematics", "Physics", "Chemistry", "Computer Science", "English"]
PASS_MARK = 40

app = Flask(__name__)
app.secret_key = "dev-secret-key"  # only for flash messages in this demo


def load_data() -> pd.DataFrame:
    """Load the student marks CSV into a DataFrame."""
    df = pd.read_csv(DATA_PATH)
    return df


def compute_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Add average, total, grade, and pass/fail columns."""
    df = df.copy()
    df["total"] = df[SUBJECTS].sum(axis=1)
    df["average"] = df[SUBJECTS].mean(axis=1).round(2)
    df["grade"] = df["average"].apply(assign_grade)
    df["status"] = np.where((df[SUBJECTS] >= PASS_MARK).all(axis=1), "Pass", "Fail")
    return df


def assign_grade(average: float) -> str:
    if average >= 90:
        return "A+"
    elif average >= 80:
        return "A"
    elif average >= 70:
        return "B"
    elif average >= 60:
        return "C"
    elif average >= 40:
        return "D"
    return "F"


def fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=110)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


@app.route("/")
def index():
    df = compute_metrics(load_data())
    sort_by = request.args.get("sort", "average")
    ascending = request.args.get("order", "desc") == "asc"
    if sort_by not in df.columns:
        sort_by = "average"
    df = df.sort_values(by=sort_by, ascending=ascending)
    students = df.to_dict(orient="records")
    return render_template("index.html", students=students, sort_by=sort_by)


@app.route("/dashboard")
def dashboard():
    df = compute_metrics(load_data())

    subject_avgs = df[SUBJECTS].mean().round(2)
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    ax1.bar(subject_avgs.index, subject_avgs.values, color="#4C6EF5")
    ax1.set_ylabel("Class Average")
    ax1.set_title("Class Average Marks by Subject")
    ax1.set_ylim(0, 100)
    plt.xticks(rotation=20, ha="right")
    subject_chart = fig_to_base64(fig1)

    grade_counts = df["grade"].value_counts().sort_index()
    fig2, ax2 = plt.subplots(figsize=(5, 4))
    ax2.pie(grade_counts.values, labels=grade_counts.index, autopct="%1.0f%%", startangle=90)
    ax2.set_title("Grade Distribution")
    grade_chart = fig_to_base64(fig2)

    pass_count = int((df["status"] == "Pass").sum())
    fail_count = int((df["status"] == "Fail").sum())

    top_performers = df.sort_values("average", ascending=False).head(5)[["name", "average", "grade"]]

    stats = {
        "total_students": len(df),
        "class_average": round(df["average"].mean(), 2),
        "highest_average": round(df["average"].max(), 2),
        "lowest_average": round(df["average"].min(), 2),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "pass_rate": round(100 * pass_count / len(df), 1) if len(df) else 0,
    }

    return render_template(
        "dashboard.html",
        stats=stats,
        subject_chart=subject_chart,
        grade_chart=grade_chart,
        top_performers=top_performers.to_dict(orient="records"),
    )


@app.route("/student/<int:student_id>")
def student_detail(student_id):
    df = compute_metrics(load_data())
    record = df[df["student_id"] == student_id]
    if record.empty:
        flash(f"No student found with id {student_id}.")
        return redirect(url_for("index"))

    student = record.iloc[0]
    marks = {subj: int(student[subj]) for subj in SUBJECTS}

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(marks.keys(), marks.values(), color="#12B886")
    ax.axhline(PASS_MARK, color="red", linestyle="--", linewidth=1, label=f"Pass mark ({PASS_MARK})")
    ax.set_ylim(0, 100)
    ax.set_ylabel("Marks")
    ax.set_title(f"{student['name']} — Subject-wise Performance")
    ax.legend()
    plt.xticks(rotation=20, ha="right")
    chart = fig_to_base64(fig)

    class_avgs = df[SUBJECTS].mean()
    comparison = {
        subj: {
            "student": marks[subj],
            "class_avg": round(class_avgs[subj], 1),
        }
        for subj in SUBJECTS
    }

    return render_template(
        "student.html",
        student=student.to_dict(),
        marks=marks,
        chart=chart,
        comparison=comparison,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
