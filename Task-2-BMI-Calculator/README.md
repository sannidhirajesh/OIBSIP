# OASIS BMI Calculator

Python Tkinter BMI Calculator for OASIS Internship Task 2 — Advanced Tier.

## Features
- Tkinter GUI
- User name, weight and height input
- BMI calculation
- Standard BMI classification
- Multi-user BMI records
- SQLite persistence
- Historical records
- BMI trend graph using matplotlib
- Input validation
- Database error handling

## Run

Install dependencies:

```text
python -m pip install -r requirements.txt
```

Run:

```text
python app.py
```

Or on Windows, double-click `run.bat`.

## BMI Formula

BMI = weight (kg) / height² (m²)

Categories:
- Underweight: BMI < 18.5
- Normal: 18.5–24.9
- Overweight: 25–29.9
- Obese: BMI >= 30

## Storage

BMI records are stored locally in `bmi_records.db` using SQLite.

The database contains:
- user name
- weight
- height
- BMI
- category
- recorded timestamp

No data is sent to an external service.
