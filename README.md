# Student Performance Analysis System

A Flask web app that analyzes student academic performance from a CSV
dataset. It computes per-subject and overall averages with pandas/numpy,
assigns letter grades, tracks pass/fail status, and renders dashboards
and per-student reports with matplotlib charts.

## Features

- **Student list** — sortable table of all students with total marks, average, grade, and pass/fail status.
- **Class dashboard** — class-wide average per subject (bar chart), grade distribution (pie chart), pass rate, and top 5 performers.
- **Per-student report** — subject-wise bar chart with the pass-mark line, plus a table comparing the student's marks against the class average per subject.
- Grading logic: A+ (90+), A (80-89), B (70-79), C (60-69), D (40-59), F (<40). A student fails overall if any single subject is below the pass mark (40).

## Dataset

`data/students.csv` contains 40 sample students across 5 subjects
(Mathematics, Physics, Chemistry, Computer Science, English). Replace
this file with your own CSV (same column headers) to analyze a
different class.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000 in your browser.

## Project Structure

```
student-performance-analysis-system/
├── app.py                 # Flask routes + pandas/numpy analysis logic
├── data/students.csv      # Sample dataset
├── templates/             # Jinja2 templates (index, dashboard, student detail)
├── static/style.css       # Styling
└── requirements.txt
```

## Tech Stack

Python, Flask, Pandas, NumPy, Matplotlib, HTML, CSS
