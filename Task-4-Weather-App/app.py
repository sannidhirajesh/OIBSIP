import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from io import BytesIO

import requests
from PIL import Image, ImageTk

APP_DIR = Path(__file__).resolve().parent
CONFIG_FILE = APP_DIR / "weather_config.json"
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
ICON_URL = "https://openweathermap.org/img/wn/{icon}@2x.png"
TIMEOUT = (4, 8)


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OASIS Weather App")
        self.root.geometry("1050x720")
        self.root.minsize(900, 650)
        self.api_key = self.load_api_key()
        self.unit = "metric"
        self.last_weather = None
        self.last_forecast = None
        self.icon_image = None
        self.busy = False

        self.city_var = tk.StringVar()
        self.key_var = tk.StringVar(value=self.api_key)
        self.unit_var = tk.StringVar(value="C")
        self.build_ui()
        self.set_status(
            "Enter a city and click Get Weather."
            if self.api_key else
            "Enter your OpenWeatherMap API key, then click Save Key."
        )

    def load_api_key(self):
        try:
            if CONFIG_FILE.exists():
                data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
                return str(data.get("api_key", "")).strip()
        except (OSError, json.JSONDecodeError):
            pass
        return ""

    def save_api_key(self):
        key = self.key_var.get().strip()
        if not key:
            self.show_error("API Key", "Please enter your OpenWeatherMap API key.")
            return
        try:
            CONFIG_FILE.write_text(
                json.dumps({"api_key": key}, indent=2), encoding="utf-8"
            )
            self.api_key = key
            self.set_status("API key saved locally.")
            messagebox.showinfo("Saved", "API key saved locally.")
        except OSError as exc:
            self.show_error("Save Error", f"Could not save the API key:\n{exc}")

    def build_ui(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        top = ttk.Frame(self.root, padding=16)
        top.pack(fill="x")
        ttk.Label(top, text="OASIS Weather App",
                  font=("Segoe UI", 24, "bold")).grid(
            row=0, column=0, columnspan=5, sticky="w", pady=(0, 12)
        )

        ttk.Label(top, text="City:").grid(row=1, column=0, sticky="w")
        city_entry = ttk.Entry(top, textvariable=self.city_var, width=28)
        city_entry.grid(row=1, column=1, padx=(8, 12), sticky="ew")
        city_entry.bind("<Return>", lambda _e: self.get_weather())

        self.search_button = ttk.Button(
            top, text="Get Weather", command=self.get_weather
        )
        self.search_button.grid(row=1, column=2, padx=5)

        ttk.Label(top, text="Units:").grid(row=1, column=3, padx=(20, 5))
        unit_box = ttk.Combobox(
            top, textvariable=self.unit_var, values=("C", "F"),
            width=5, state="readonly"
        )
        unit_box.grid(row=1, column=4)
        unit_box.bind("<<ComboboxSelected>>", self.change_unit)

        ttk.Label(top, text="OpenWeatherMap API key:").grid(
            row=2, column=0, sticky="w", pady=(12, 0)
        )
        ttk.Entry(top, textvariable=self.key_var, show="*", width=40).grid(
            row=2, column=1, columnspan=2, padx=8, pady=(12, 0), sticky="ew"
        )
        ttk.Button(top, text="Save Key", command=self.save_api_key).grid(
            row=2, column=3, pady=(12, 0)
        )
        top.columnconfigure(1, weight=1)

        self.status = ttk.Label(self.root, text="Ready", padding=(16, 4))
        self.status.pack(fill="x")

        main = ttk.Frame(self.root, padding=(16, 4, 16, 16))
        main.pack(fill="both", expand=True)

        current = ttk.LabelFrame(main, text="Current Weather", padding=14)
        current.pack(fill="x", pady=(0, 12))

        self.current_icon = ttk.Label(current, text="☁", font=("Segoe UI", 34))
        self.current_icon.grid(row=0, column=0, rowspan=3, padx=(5, 20))
        self.city_label = ttk.Label(
            current, text="Search for a city", font=("Segoe UI", 20, "bold")
        )
        self.city_label.grid(row=0, column=1, sticky="w")
        self.temp_label = ttk.Label(
            current, text="-- °C", font=("Segoe UI", 28, "bold")
        )
        self.temp_label.grid(row=1, column=1, sticky="w")
        self.condition_label = ttk.Label(
            current, text="Weather condition will appear here",
            font=("Segoe UI", 13)
        )
        self.condition_label.grid(row=2, column=1, sticky="w")
        self.details_label = ttk.Label(
            current, text="Humidity: --    Wind: --    Pressure: --",
            font=("Segoe UI", 11)
        )
        self.details_label.grid(row=0, column=2, rowspan=3, padx=40, sticky="w")

        forecast_frame = ttk.Frame(main)
        forecast_frame.pack(fill="both", expand=True)

        hourly_box = ttk.LabelFrame(
            forecast_frame, text="Next 6 Hours", padding=10
        )
        hourly_box.pack(side="left", fill="both", expand=True, padx=(0, 6))
        self.hourly_tree = ttk.Treeview(
            hourly_box, columns=("time", "temp", "condition"),
            show="headings", height=10
        )
        for col, title, width in (
            ("time", "Time", 90), ("temp", "Temp", 80),
            ("condition", "Condition", 150)
        ):
            self.hourly_tree.heading(col, text=title)
            self.hourly_tree.column(col, width=width, anchor="center")
        self.hourly_tree.pack(fill="both", expand=True)

        daily_box = ttk.LabelFrame(
            forecast_frame, text="Next 5 Days", padding=10
        )
        daily_box.pack(side="left", fill="both", expand=True, padx=(6, 0))
        self.daily_tree = ttk.Treeview(
            daily_box, columns=("day", "temp", "condition"),
            show="headings", height=10
        )
        for col, title, width in (
            ("day", "Day", 110), ("temp", "Temp", 110),
            ("condition", "Condition", 150)
        ):
            self.daily_tree.heading(col, text=title)
            self.daily_tree.column(col, width=width, anchor="center")
        self.daily_tree.pack(fill="both", expand=True)

        ttk.Label(
            self.root, text="Weather data provided by OpenWeatherMap",
            padding=(16, 4)
        ).pack(fill="x")

    def set_status(self, text):
        self.status.config(text=text)

    def show_error(self, title, text):
        self.set_status(text.replace("\n", " "))
        messagebox.showerror(title, text)

    def get_weather(self):
        if self.busy:
            return
        city = self.city_var.get().strip()
        key = self.key_var.get().strip()

        if not city:
            self.show_error("Input Error", "Please enter a city name.")
            return
        if not key:
            self.show_error(
                "API Key Required",
                "Please enter your OpenWeatherMap API key and click Save Key."
            )
            return

        self.api_key = key
        self.busy = True
        self.search_button.config(state="disabled")
        self.set_status(f"Fetching weather for {city}...")
        threading.Thread(
            target=self.fetch_weather, args=(city, key), daemon=True
        ).start()

    def fetch_weather(self, city, key):
        try:
            current_response = requests.get(
                CURRENT_URL,
                params={"q": city, "appid": key, "units": "metric"},
                timeout=TIMEOUT,
            )
            if current_response.status_code == 401:
                raise RuntimeError(
                    "Invalid OpenWeatherMap API key. Check your API key and try again."
                )
            if current_response.status_code == 404:
                raise RuntimeError(
                    f"City '{city}' was not found. Please check the spelling."
                )
            if current_response.status_code != 200:
                raise RuntimeError(
                    f"Weather service returned HTTP {current_response.status_code}."
                )
            current = current_response.json()

            forecast_response = requests.get(
                FORECAST_URL,
                params={"q": city, "appid": key, "units": "metric"},
                timeout=TIMEOUT,
            )
            if forecast_response.status_code == 401:
                raise RuntimeError(
                    "Invalid OpenWeatherMap API key. Check your API key and try again."
                )
            if forecast_response.status_code == 404:
                raise RuntimeError(
                    f"Forecast for '{city}' was not found."
                )
            if forecast_response.status_code != 200:
                raise RuntimeError(
                    f"Forecast service returned HTTP {forecast_response.status_code}."
                )
            forecast = forecast_response.json()

            self.root.after(0, lambda: self.update_weather(current, forecast))

        except requests.Timeout:
            self.root.after(
                0, lambda: self.finish_with_error(
                    "Network Timeout",
                    "The weather service did not respond in time. Please try again."
                )
            )
        except requests.ConnectionError:
            self.root.after(
                0, lambda: self.finish_with_error(
                    "Connection Error",
                    "Could not connect to OpenWeatherMap. Check your internet connection."
                )
            )
        except requests.RequestException as exc:
            self.root.after(
                0, lambda: self.finish_with_error(
                    "Network Error", f"Could not fetch weather data.\n{exc}"
                )
            )
        except (ValueError, KeyError):
            self.root.after(
                0, lambda: self.finish_with_error(
                    "Data Error",
                    "The weather service returned an unexpected response."
                )
            )
        except RuntimeError as exc:
            self.root.after(
                0, lambda: self.finish_with_error("Weather Error", str(exc))
            )
        except Exception as exc:
            self.root.after(
                0, lambda: self.finish_with_error(
                    "Unexpected Error", f"Something went wrong:\n{exc}"
                )
            )

    def finish_with_error(self, title, text):
        self.busy = False
        self.search_button.config(state="normal")
        self.show_error(title, text)

    def update_weather(self, current, forecast):
        self.busy = False
        self.search_button.config(state="normal")
        self.last_weather = current
        self.last_forecast = forecast

        name = current["name"]
        country = current.get("sys", {}).get("country", "")
        temp_c = current["main"]["temp"]
        humidity = current["main"]["humidity"]
        pressure = current["main"]["pressure"]
        wind_ms = current.get("wind", {}).get("speed", 0)
        description = current["weather"][0]["description"].title()
        icon = current["weather"][0]["icon"]

        self.city_label.config(text=f"{name}, {country}")
        self.condition_label.config(text=description)
        self.details_label.config(
            text=f"Humidity: {humidity}%    Wind: {wind_ms:.1f} m/s    "
                 f"Pressure: {pressure} hPa"
        )
        self.set_current_temperature(temp_c)
        self.load_icon(icon)
        self.populate_forecasts(forecast)
        self.set_status(f"Weather updated for {name}.")

    def set_current_temperature(self, temp_c):
        if self.unit == "metric":
            value, symbol = temp_c, "°C"
        else:
            value, symbol = (temp_c * 9 / 5) + 32, "°F"
        self.temp_label.config(text=f"{value:.1f} {symbol}")

    def change_unit(self, _event=None):
        self.unit = "metric" if self.unit_var.get() == "C" else "imperial"
        if self.last_weather:
            self.set_current_temperature(self.last_weather["main"]["temp"])
            if self.last_forecast:
                self.populate_forecasts(self.last_forecast)

    def load_icon(self, icon_code):
        def worker():
            try:
                response = requests.get(
                    ICON_URL.format(icon=icon_code), timeout=TIMEOUT
                )
                response.raise_for_status()
                image = Image.open(BytesIO(response.content)).convert("RGBA")
                image = image.resize((90, 90), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.root.after(0, lambda: self.set_icon(photo))
            except Exception:
                pass
        threading.Thread(target=worker, daemon=True).start()

    def set_icon(self, photo):
        self.icon_image = photo
        self.current_icon.config(image=photo, text="")

    def populate_forecasts(self, forecast):
        for tree in (self.hourly_tree, self.daily_tree):
            for item in tree.get_children():
                tree.delete(item)

        items = forecast.get("list", [])
        for item in items[:6]:
            self.hourly_tree.insert(
                "", "end",
                values=(
                    item["dt_txt"][11:16],
                    self.format_temp(item["main"]["temp"]),
                    item["weather"][0]["main"],
                )
            )

        daily = {}
        for item in items:
            day = item["dt_txt"][:10]
            if day not in daily:
                daily[day] = item
            if len(daily) >= 5:
                break

        for day, item in list(daily.items())[:5]:
            self.daily_tree.insert(
                "", "end",
                values=(
                    day,
                    self.format_temp(item["main"]["temp"]),
                    item["weather"][0]["main"],
                )
            )

    def format_temp(self, temp_c):
        if self.unit == "metric":
            return f"{temp_c:.1f} °C"
        return f"{(temp_c * 9 / 5) + 32:.1f} °F"


if __name__ == "__main__":
    root = tk.Tk()
    WeatherApp(root)
    root.mainloop()
