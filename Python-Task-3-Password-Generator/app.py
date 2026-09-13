import secrets
import string
import tkinter as tk
from tkinter import ttk, messagebox

AMBIGUOUS = set("0OIl1|")
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.?/\\"
HISTORY_LIMIT = 5


class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("OASIS Secure Password Generator")
        self.root.geometry("720x620")
        self.root.minsize(650, 560)

        self.length_var = tk.IntVar(value=16)
        self.upper_var = tk.BooleanVar(value=True)
        self.lower_var = tk.BooleanVar(value=True)
        self.number_var = tk.BooleanVar(value=True)
        self.symbol_var = tk.BooleanVar(value=True)
        self.ambiguous_var = tk.BooleanVar(value=False)
        self.password_var = tk.StringVar()
        self.strength_var = tk.StringVar(value="Strength: —")
        self.status_var = tk.StringVar(value="Choose your options and generate a password.")
        self.history = []

        self.build_ui()

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
            text="Secure Password Generator",
            font=("Segoe UI", 24, "bold")
        ).pack(anchor="w")

        ttk.Label(
            main,
            text="OASIS Internship — Task 3 | Advanced Tier",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 18))

        settings = ttk.LabelFrame(main, text="Password Settings", padding=15)
        settings.pack(fill="x")

        ttk.Label(settings, text="Length:").grid(
            row=0, column=0, sticky="w"
        )
        self.length_spin = ttk.Spinbox(
            settings, from_=8, to=128, textvariable=self.length_var,
            width=8, command=self.validate_length
        )
        self.length_spin.grid(row=0, column=1, padx=(10, 25), sticky="w")
        self.length_spin.bind("<FocusOut>", lambda _e: self.validate_length())

        ttk.Label(settings, text="Character types:").grid(
            row=1, column=0, sticky="nw", pady=(15, 0)
        )

        checks = ttk.Frame(settings)
        checks.grid(row=1, column=1, columnspan=3, sticky="w", pady=(10, 0))

        ttk.Checkbutton(
            checks, text="Uppercase (A-Z)", variable=self.upper_var
        ).grid(row=0, column=0, sticky="w", padx=(0, 20))
        ttk.Checkbutton(
            checks, text="Lowercase (a-z)", variable=self.lower_var
        ).grid(row=0, column=1, sticky="w")
        ttk.Checkbutton(
            checks, text="Numbers (0-9)", variable=self.number_var
        ).grid(row=1, column=0, sticky="w", padx=(0, 20), pady=(8, 0))
        ttk.Checkbutton(
            checks, text="Symbols", variable=self.symbol_var
        ).grid(row=1, column=1, sticky="w", pady=(8, 0))

        ttk.Checkbutton(
            settings,
            text="Exclude ambiguous characters (0, O, I, l, 1, |)",
            variable=self.ambiguous_var
        ).grid(row=2, column=1, columnspan=3, sticky="w", pady=(15, 0))

        output = ttk.LabelFrame(main, text="Generated Password", padding=15)
        output.pack(fill="x", pady=18)

        password_entry = ttk.Entry(
            output, textvariable=self.password_var,
            font=("Consolas", 16), justify="center"
        )
        password_entry.pack(fill="x", pady=(0, 10))

        buttons = ttk.Frame(output)
        buttons.pack(fill="x")

        ttk.Button(
            buttons, text="Generate Password",
            command=self.generate
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            buttons, text="Copy to Clipboard",
            command=self.copy_password
        ).pack(side="left")

        ttk.Label(
            output, textvariable=self.strength_var,
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(12, 0))

        history_box = ttk.LabelFrame(main, text="Last 5 Generated Passwords", padding=12)
        history_box.pack(fill="both", expand=True)

        self.history_list = tk.Listbox(
            history_box, height=6, font=("Consolas", 11)
        )
        self.history_list.pack(fill="both", expand=True)

        ttk.Label(
            main, textvariable=self.status_var
        ).pack(anchor="w", pady=(10, 0))

    def validate_length(self):
        try:
            length = int(self.length_var.get())
        except (TypeError, ValueError):
            self.length_var.set(16)
            return False

        if length < 8:
            self.length_var.set(8)
            return False
        if length > 128:
            self.length_var.set(128)
            return False
        return True

    def selected_sets(self):
        choices = []
        if self.upper_var.get():
            choices.append(string.ascii_uppercase)
        if self.lower_var.get():
            choices.append(string.ascii_lowercase)
        if self.number_var.get():
            choices.append(string.digits)
        if self.symbol_var.get():
            choices.append(SYMBOLS)

        if self.ambiguous_var.get():
            choices = [
                "".join(ch for ch in charset if ch not in AMBIGUOUS)
                for charset in choices
            ]

        return [charset for charset in choices if charset]

    def generate(self):
        if not self.validate_length():
            messagebox.showerror(
                "Invalid Length",
                "Password length must be between 8 and 128 characters."
            )
            return

        charsets = self.selected_sets()

        if not charsets:
            messagebox.showerror(
                "No Character Types",
                "Select at least one character type."
            )
            return

        length = int(self.length_var.get())

        if length < len(charsets):
            messagebox.showerror(
                "Length Too Short",
                "Password length must be at least the number of selected character types."
            )
            return

        # Guarantee at least one character from every selected type.
        password_chars = [secrets.choice(charset) for charset in charsets]
        combined = "".join(charsets)
        password_chars.extend(
            secrets.choice(combined)
            for _ in range(length - len(password_chars))
        )

        # Cryptographically secure shuffle.
        for i in range(len(password_chars) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            password_chars[i], password_chars[j] = password_chars[j], password_chars[i]

        password = "".join(password_chars)
        self.password_var.set(password)
        self.update_strength(password, len(charsets))
        self.add_history(password)
        self.status_var.set("Secure password generated.")

    def calculate_strength(self, password, diversity):
        score = 0
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
        if diversity >= 2:
            score += 1
        if diversity >= 3:
            score += 1
        if diversity >= 4:
            score += 1

        if score <= 1:
            return "Weak"
        if score <= 3:
            return "Medium"
        return "Strong"

    def update_strength(self, password, diversity):
        strength = self.calculate_strength(password, diversity)
        self.strength_var.set(f"Strength: {strength}")

    def copy_password(self):
        password = self.password_var.get()
        if not password:
            messagebox.showwarning(
                "Nothing to Copy",
                "Generate a password first."
            )
            return

        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            self.root.update()
            self.status_var.set("Password copied to clipboard.")
        except tk.TclError as exc:
            messagebox.showerror(
                "Clipboard Error",
                f"Could not copy the password:\n{exc}"
            )

    def add_history(self, password):
        self.history.insert(0, password)
        self.history = self.history[:HISTORY_LIMIT]

        self.history_list.delete(0, tk.END)
        for item in self.history:
            self.history_list.insert(tk.END, item)


if __name__ == "__main__":
    root = tk.Tk()
    PasswordGenerator(root)
    root.mainloop()
