# 🐍 OASIS Python Programming Internship Tasks

This repository contains three Python projects completed as part of the **OASIS Infobyte Python Programming Internship**.

## 📂 Projects

### 🧮 Task 2 — BMI Calculator

A GUI-based BMI calculator built with Python.

**Features:**

* User name, weight, and height input
* BMI calculation and classification
* Multiple-user support
* SQLite database for storing records
* BMI history
* User-specific history
* BMI trend graph using Matplotlib
* Input validation and error handling

**Technologies:** Python, Tkinter, SQLite, Matplotlib

---

### 🔐 Task 3 — Random Password Generator

A secure GUI-based password generator.

**Features:**

* Password length control
* Uppercase, lowercase, numbers, and symbols
* Secure generation using Python's `secrets` module
* Password strength indicator
* Copy to clipboard
* Exclude ambiguous characters
* Last 5 generated passwords
* Input validation

**Technologies:** Python, Tkinter, `secrets`

---

### 🌦️ Task 4 — Basic Weather App

A GUI-based real-time weather application using the OpenWeatherMap API.

**Features:**

* Search weather by city
* Current temperature
* Celsius/Fahrenheit conversion
* Humidity and wind speed
* Weather condition and icon
* Next 6-hour forecast
* Next 5-day forecast
* Invalid city and API-key handling
* Network and timeout error handling
* Local API-key configuration

**Technologies:** Python, Tkinter, Requests, Pillow, OpenWeatherMap API

---

## 🛠️ Technologies Used

| Technology         | Purpose                      |
| ------------------ | ---------------------------- |
| Python             | Main programming language    |
| Tkinter            | GUI development              |
| SQLite             | Data storage for BMI records |
| Matplotlib         | BMI trend visualization      |
| `secrets`          | Secure password generation   |
| Requests           | API communication            |
| Pillow             | Weather icon handling        |
| OpenWeatherMap API | Weather data                 |

---

## 🚀 How to Run

Each project is independent and has its own folder.

### 🧮 BMI Calculator

```bash
cd Task-2-BMI-Calculator
python -m pip install -r requirements.txt
python app.py
```

### 🔐 Password Generator

```bash
cd Task-3-Password-Generator
python app.py
```

### 🌦️ Weather App

```bash
cd Task-4-Weather-App
python -m pip install -r requirements.txt
python app.py
```

Windows users can also use the included `run.bat` file in each project.

---

## 🔒 Security & Privacy

Sensitive information should not be committed to this repository.

The Weather App stores the OpenWeatherMap API key locally and excludes the configuration file through `.gitignore`.

The Password Generator uses the Python `secrets` module for secure password generation and does not permanently store generated passwords.

The BMI Calculator stores records locally using SQLite.

---

## 🎯 Internship Projects

These projects demonstrate practical experience with:

* Python programming
* GUI development
* Database management
* API integration
* Data visualization
* Input validation
* Exception handling
* Secure random generation
* Git and GitHub

---

## 👩‍💻 Author

**Sannidhi S R**

Python Programming Internship
**OASIS Infobyte**

---

## 📁 Repository Structure

```text
OASIS-Python-Internship-Tasks/
│
├── Task-2-BMI-Calculator/
├── Task-3-Password-Generator/
└── Task-4-Weather-App/
```

Each project contains its own README with project-specific setup and feature details.
