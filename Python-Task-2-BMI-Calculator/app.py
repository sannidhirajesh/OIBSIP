import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib.pyplot as plt

DB_FILE = "bmi_records.db"


class BMICalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("OASIS BMI Calculator")
        self.root.geometry("900x680")
        self.root.minsize(800, 620)

        self.user_var = tk.StringVar()
        self.weight_var = tk.StringVar()
        self.height_var = tk.StringVar()
        self.result_var = tk.StringVar(value="Enter your details and click Calculate BMI.")
        self.category_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready.")

        self.init_database()
        self.build_ui()
        self.refresh_users()

    def connect(self):
        return sqlite3.connect(DB_FILE)

    def init_database(self):
        try:
            with self.connect() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS bmi_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_name TEXT NOT NULL,
                        weight REAL NOT NULL,
                        height REAL NOT NULL,
                        bmi REAL NOT NULL,
                        category TEXT NOT NULL,
                        recorded_at TEXT NOT NULL
                    )
                """)
        except sqlite3.Error as exc:
            messagebox.showerror(
                "Database Error",
                f"Could not initialize the database:\n{exc}"
            )

    def build_ui(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        main = ttk.Frame(self.root, padding=20)
        main.pack(fill="both", expand=True)

        ttk.Label(
            main,
            text="BMI Calculator",
            font=("Segoe UI", 25, "bold")
        ).pack(anchor="w")

        ttk.Label(
            main,
            text="OASIS Internship — Task 2 | Advanced Tier",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 18))

        form = ttk.LabelFrame(main, text="BMI Details", padding=15)
        form.pack(fill="x")

        ttk.Label(form, text="User name:").grid(
            row=0, column=0, sticky="w", pady=6
        )
        ttk.Entry(form, textvariable=self.user_var, width=30).grid(
            row=0, column=1, sticky="w", padx=10, pady=6
        )

        ttk.Label(form, text="Weight (kg):").grid(
            row=1, column=0, sticky="w", pady=6
        )
        ttk.Entry(form, textvariable=self.weight_var, width=30).grid(
            row=1, column=1, sticky="w", padx=10, pady=6
        )

        ttk.Label(form, text="Height (m):").grid(
            row=2, column=0, sticky="w", pady=6
        )
        ttk.Entry(form, textvariable=self.height_var, width=30).grid(
            row=2, column=1, sticky="w", padx=10, pady=6
        )

        buttons = ttk.Frame(form)
        buttons.grid(row=0, column=2, rowspan=3, padx=30)

        ttk.Button(
            buttons, text="Calculate BMI",
            command=self.calculate_bmi
        ).pack(fill="x", pady=4)

        ttk.Button(
            buttons, text="Show Selected User History",
            command=self.show_history
        ).pack(fill="x", pady=4)

        ttk.Button(
            buttons, text="Show BMI Trend Graph",
            command=self.show_graph
        ).pack(fill="x", pady=4)

        result = ttk.LabelFrame(main, text="Result", padding=18)
        result.pack(fill="x", pady=18)

        ttk.Label(
            result, textvariable=self.result_var,
            font=("Segoe UI", 25, "bold")
        ).pack()

        ttk.Label(
            result, textvariable=self.category_var,
            font=("Segoe UI", 15, "bold")
        ).pack(pady=(8, 0))

        ttk.Label(
            result,
            text="BMI categories: Underweight < 18.5 | Normal 18.5–24.9 | "
                 "Overweight 25–29.9 | Obese ≥ 30",
            font=("Segoe UI", 9)
        ).pack(pady=(10, 0))

        history_frame = ttk.LabelFrame(
            main, text="Saved BMI Records", padding=10
        )
        history_frame.pack(fill="both", expand=True)

        columns = ("user", "weight", "height", "bmi", "category", "date")
        self.tree = ttk.Treeview(
            history_frame, columns=columns, show="headings", height=8
        )

        headings = {
            "user": "User",
            "weight": "Weight (kg)",
            "height": "Height (m)",
            "bmi": "BMI",
            "category": "Category",
            "date": "Recorded At",
        }

        widths = {
            "user": 130, "weight": 90, "height": 90,
            "bmi": 80, "category": 120, "date": 150
        }

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")

        self.tree.pack(fill="both", expand=True)

        ttk.Label(
            main, textvariable=self.status_var
        ).pack(anchor="w", pady=(8, 0))

    def calculate_bmi(self):
        user = self.user_var.get().strip()

        if not user:
            self.show_error("Input Error", "Please enter a user name.")
            return

        try:
            weight = float(self.weight_var.get())
            height = float(self.height_var.get())
        except ValueError:
            self.show_error(
                "Input Error",
                "Weight and height must be numeric values."
            )
            return

        if weight <= 0 or height <= 0:
            self.show_error(
                "Input Error",
                "Weight and height must be greater than zero."
            )
            return

        bmi = weight / (height ** 2)
        category = self.classify_bmi(bmi)

        self.result_var.set(f"BMI: {bmi:.2f}")
        self.category_var.set(category)
        self.status_var.set(f"BMI calculated for {user}.")

        try:
            with self.connect() as conn:
                conn.execute("""
                    INSERT INTO bmi_records
                    (user_name, weight, height, bmi, category, recorded_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    user, weight, height, bmi, category,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))
        except sqlite3.Error as exc:
            self.show_error(
                "Database Error",
                f"BMI was calculated, but the record could not be saved:\n{exc}"
            )
            return

        self.refresh_users()
        self.refresh_records()

    @staticmethod
    def classify_bmi(bmi):
        if bmi < 18.5:
            return "Underweight"
        if bmi < 25:
            return "Normal"
        if bmi < 30:
            return "Overweight"
        return "Obese"

    def refresh_users(self):
        try:
            with self.connect() as conn:
                rows = conn.execute(
                    "SELECT DISTINCT user_name FROM bmi_records ORDER BY user_name"
                ).fetchall()
        except sqlite3.Error:
            rows = []

        self.refresh_records()

    def refresh_records(self, user=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            with self.connect() as conn:
                if user:
                    rows = conn.execute("""
                        SELECT user_name, weight, height, bmi, category, recorded_at
                        FROM bmi_records
                        WHERE user_name = ?
                        ORDER BY recorded_at DESC
                    """, (user,)).fetchall()
                else:
                    rows = conn.execute("""
                        SELECT user_name, weight, height, bmi, category, recorded_at
                        FROM bmi_records
                        ORDER BY recorded_at DESC
                    """).fetchall()

            for row in rows:
                self.tree.insert(
                    "", "end",
                    values=(
                        row[0], f"{row[1]:.2f}", f"{row[2]:.2f}",
                        f"{row[3]:.2f}", row[4], row[5]
                    )
                )
        except sqlite3.Error as exc:
            self.show_error(
                "Database Error",
                f"Could not read BMI records:\n{exc}"
            )

    def show_history(self):
        user = self.user_var.get().strip()
        if not user:
            self.show_error(
                "User Required",
                "Enter a user name to view that user's history."
            )
            return
        self.refresh_records(user)
        self.status_var.set(f"Showing BMI history for {user}.")

    def show_graph(self):
        user = self.user_var.get().strip()
        if not user:
            self.show_error(
                "User Required",
                "Enter a user name to view the BMI trend."
            )
            return

        try:
            with self.connect() as conn:
                rows = conn.execute("""
                    SELECT recorded_at, bmi
                    FROM bmi_records
                    WHERE user_name = ?
                    ORDER BY recorded_at
                """, (user,)).fetchall()
        except sqlite3.Error as exc:
            self.show_error(
                "Database Error",
                f"Could not read data for the graph:\n{exc}"
            )
            return

        if not rows:
            self.show_error(
                "No Data",
                f"No BMI records found for {user}."
            )
            return

        dates = [row[0] for row in rows]
        values = [row[1] for row in rows]

        try:
            plt.figure(figsize=(9, 5))
            plt.plot(dates, values, marker="o")
            plt.title(f"BMI Trend — {user}")
            plt.xlabel("Recorded At")
            plt.ylabel("BMI")
            plt.xticks(rotation=35, ha="right")
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
        except Exception as exc:
            self.show_error(
                "Graph Error",
                f"Could not display the BMI graph:\n{exc}"
            )

    def show_error(self, title, message):
        self.status_var.set(message.replace("\n", " "))
        messagebox.showerror(title, message)


if __name__ == "__main__":
    root = tk.Tk()
    BMICalculator(root)
    root.mainloop()
