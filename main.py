import sys
import os
import requests
from dotenv import load_dotenv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QFrame,
    QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QColor, QFont

load_dotenv()


class StatCard(QFrame):
    """A small pill card showing an icon + value + label."""
    def __init__(self, icon, value, label):
        super().__init__()
        self.setObjectName("stat_card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(2)

        self.icon_lbl = QLabel(icon)
        self.icon_lbl.setObjectName("stat_icon")
        self.icon_lbl.setAlignment(Qt.AlignCenter)

        self.value_lbl = QLabel(value)
        self.value_lbl.setObjectName("stat_value")
        self.value_lbl.setAlignment(Qt.AlignCenter)

        self.label_lbl = QLabel(label)
        self.label_lbl.setObjectName("stat_label")
        self.label_lbl.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.icon_lbl)
        layout.addWidget(self.value_lbl)
        layout.addWidget(self.label_lbl)

    def update(self, value):
        self.value_lbl.setText(value)


class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("SkyCast Weather")
        self.setFixedSize(460, 680)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(28, 36, 28, 36)
        self.main_layout.setSpacing(14)

        # ── App title ──────────────────────────────────────────────
        title = QLabel("SkyCast")
        title.setObjectName("app_title")
        title.setAlignment(Qt.AlignCenter)

        # ── Input row ─────────────────────────────────────────────
        input_row = QHBoxLayout()
        input_row.setSpacing(10)

        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Search city…")
        self.city_input.setObjectName("city_input")

        self.get_weather_button = QPushButton("Go")
        self.get_weather_button.setObjectName("get_weather_button")
        self.get_weather_button.setCursor(Qt.PointingHandCursor)
        self.get_weather_button.setFixedWidth(60)

        input_row.addWidget(self.city_input)
        input_row.addWidget(self.get_weather_button)

        # ── Weather card ───────────────────────────────────────────
        self.card = QFrame()
        self.card.setObjectName("weather_card")
        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(20, 24, 20, 24)
        self.card_layout.setSpacing(6)

        # City + country
        self.city_display = QLabel("Welcome")
        self.city_display.setObjectName("city_display")
        self.city_display.setAlignment(Qt.AlignCenter)

        # Big emoji
        self.emoji_label = QLabel("🌍")
        self.emoji_label.setObjectName("emoji_label")
        self.emoji_label.setAlignment(Qt.AlignCenter)

        # Temperature
        self.temperature_label = QLabel("--°C")
        self.temperature_label.setObjectName("temperature_label")
        self.temperature_label.setAlignment(Qt.AlignCenter)

        # Feels like
        self.feels_label = QLabel("")
        self.feels_label.setObjectName("feels_label")
        self.feels_label.setAlignment(Qt.AlignCenter)

        # Description
        self.description_label = QLabel("Search a city to start")
        self.description_label.setObjectName("description_label")
        self.description_label.setAlignment(Qt.AlignCenter)

        # ── Stat pills row ─────────────────────────────────────────
        self.stats_row = QHBoxLayout()
        self.stats_row.setSpacing(10)

        self.humidity_card  = StatCard("💧", "--", "Humidity")
        self.wind_card      = StatCard("💨", "--", "Wind")
        self.visibility_card = StatCard("👁", "--", "Visibility")

        for card in (self.humidity_card, self.wind_card, self.visibility_card):
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.stats_row.addWidget(card)

        # Assemble card
        self.card_layout.addWidget(self.city_display)
        self.card_layout.addWidget(self.emoji_label)
        self.card_layout.addWidget(self.temperature_label)
        self.card_layout.addWidget(self.feels_label)
        self.card_layout.addWidget(self.description_label)
        self.card_layout.addSpacing(14)
        self.card_layout.addLayout(self.stats_row)

        # Drop shadow on card
        shadow = QGraphicsDropShadowEffect(blurRadius=28, xOffset=0, yOffset=12)
        shadow.setColor(QColor(0, 0, 0, 90))
        self.card.setGraphicsEffect(shadow)

        # Assemble window
        self.main_layout.addWidget(title)
        self.main_layout.addSpacing(4)
        self.main_layout.addLayout(input_row)
        self.main_layout.addSpacing(10)
        self.main_layout.addWidget(self.card)
        self.setLayout(self.main_layout)

        self.apply_styles("default")

        self.get_weather_button.clicked.connect(self.get_weather)
        self.city_input.returnPressed.connect(self.get_weather)

    # ── Theming ────────────────────────────────────────────────────
    def apply_styles(self, weather_type):
        themes = {
            # Deep navy night sky
            "default":  ("qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #0d1b2a,stop:1 #1b2d42)", "#2a4a6b"),
            # Burnt amber dusk — warm but dim, like late afternoon haze
            "sunny":    ("qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #1a0a00,stop:1 #6b3a10)", "#a05a1a"),
            # Dark slate overcast
            "cloudy":   ("qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #1c1c24,stop:1 #2e3040)", "#44475a"),
            # Deep ocean storm
            "rain":     ("qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #0a0e1a,stop:1 #152040)", "#1a3060"),
            # Cold midnight blue — ice without brightness
            "snow":     ("qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #0d1520,stop:1 #1a2d40)", "#2a4a60"),
            # Near-black with deep purple undertone
            "thunder":  ("qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #0a0a12,stop:1 #1a1428)", "#2a2040"),
            # Charcoal fog
            "mist":     ("qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #141820,stop:1 #252a38)", "#353c50"),
        }

        bg, accent = themes.get(weather_type, themes["default"])

        self.setStyleSheet(f"""
            QWidget {{
                background: {bg};
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }}

            /* App title */
            QLabel#app_title {{
                font-size: 15px;
                font-weight: 600;
                letter-spacing: 4px;
                color: rgba(255,255,255,0.65);
                background: transparent;
            }}

            /* Input */
            QLineEdit#city_input {{
                background: rgba(255,255,255,0.18);
                border: 1.5px solid rgba(255,255,255,0.30);
                border-radius: 14px;
                padding: 11px 16px;
                font-size: 16px;
                color: white;
            }}
            QLineEdit#city_input:focus {{
                border: 1.5px solid rgba(255,255,255,0.65);
                background: rgba(255,255,255,0.23);
            }}

            /* Go button */
            QPushButton#get_weather_button {{
                background: rgba(255,255,255,0.22);
                color: white;
                border: 1.5px solid rgba(255,255,255,0.35);
                border-radius: 14px;
                font-size: 15px;
                font-weight: bold;
                padding: 11px;
            }}
            QPushButton#get_weather_button:hover {{
                background: rgba(255,255,255,0.32);
            }}
            QPushButton#get_weather_button:pressed {{
                background: rgba(255,255,255,0.14);
            }}

            /* Card */
            QFrame#weather_card {{
                background: rgba(255,255,255,0.13);
                border-radius: 28px;
                border: 1px solid rgba(255,255,255,0.22);
            }}

            /* Stat pill cards */
            QFrame#stat_card {{
                background: rgba(255,255,255,0.14);
                border-radius: 16px;
                border: 1px solid rgba(255,255,255,0.20);
            }}

            /* All labels default */
            QLabel {{
                background: transparent;
                color: white;
            }}

            QLabel#city_display {{
                font-size: 22px;
                font-weight: 700;
                letter-spacing: 1px;
            }}
            QLabel#emoji_label   {{ font-size: 88px; }}
            QLabel#temperature_label {{
                font-size: 68px;
                font-weight: 200;
                letter-spacing: -2px;
            }}
            QLabel#feels_label {{
                font-size: 14px;
                color: rgba(255,255,255,0.65);
            }}
            QLabel#description_label {{
                font-size: 18px;
                font-style: italic;
                color: rgba(255,255,255,0.85);
            }}

            /* Stat card sub-labels */
            QLabel#stat_icon  {{ font-size: 22px; }}
            QLabel#stat_value {{
                font-size: 16px;
                font-weight: 700;
            }}
            QLabel#stat_label {{
                font-size: 11px;
                color: rgba(255,255,255,0.60);
                letter-spacing: 0.5px;
            }}
        """)

    # ── API call ───────────────────────────────────────────────────
    def get_weather(self):
        api_key = os.getenv("WEATHER_API_KEY")
        city = self.city_input.text().strip()

        if not city:
            return

        if not api_key:
            self.display_error("API Key Missing", "Set WEATHER_API_KEY in your .env file")
            return

        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={api_key}&units=metric"
        )

        try:
            response = requests.get(url, timeout=8)
            response.raise_for_status()
            self.display_weather(response.json())
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                self.display_error("City Not Found", f'No results for "{city}"')
            else:
                self.display_error("Request Failed", f"HTTP {response.status_code}")
        except requests.exceptions.ConnectionError:
            self.display_error("No Connection", "Check your internet and try again")
        except Exception as e:
            self.display_error("Error", str(e))

    # ── Display ────────────────────────────────────────────────────
    def display_weather(self, data):
        temp       = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity   = data["main"]["humidity"]
        weather_id = data["weather"][0]["id"]
        description = data["weather"][0]["description"]
        city_name  = data["name"]
        country    = data.get("sys", {}).get("country", "")
        wind_speed = data.get("wind", {}).get("speed", None)   # m/s
        visibility = data.get("visibility", None)               # metres

        # Theme
        theme = "default"
        if 200 <= weather_id <= 232:  theme = "thunder"
        elif 300 <= weather_id <= 321: theme = "rain"
        elif 500 <= weather_id <= 531: theme = "rain"
        elif 600 <= weather_id <= 622: theme = "snow"
        elif 700 <= weather_id <= 781: theme = "mist"
        elif weather_id == 800:        theme = "sunny"
        elif 801 <= weather_id <= 804: theme = "cloudy"
        self.apply_styles(theme)

        # Main labels
        location = f"{city_name}, {country}" if country else city_name
        self.city_display.setText(location)
        self.temperature_label.setText(f"{temp:.0f}°C")
        self.feels_label.setText(f"Feels like {feels_like:.0f}°C")
        self.emoji_label.setText(self.get_weather_emoji(weather_id))
        self.description_label.setText(description.capitalize())

        # Stat pills
        self.humidity_card.update(f"{humidity}%")

        if wind_speed is not None:
            wind_kmh = wind_speed * 3.6
            self.wind_card.update(f"{wind_kmh:.0f} km/h")
        else:
            self.wind_card.update("N/A")

        if visibility is not None:
            vis_km = visibility / 1000
            self.visibility_card.update(f"{vis_km:.1f} km")
        else:
            self.visibility_card.update("N/A")

    def display_error(self, title, detail=""):
        self.apply_styles("default")
        self.city_display.setText(title)
        self.temperature_label.setText("")
        self.feels_label.setText("")
        self.emoji_label.setText("⚠️")
        self.description_label.setText(detail)
        self.humidity_card.update("--")
        self.wind_card.update("--")
        self.visibility_card.update("--")

    @staticmethod
    def get_weather_emoji(weather_id):
        if 200 <= weather_id <= 232: return "⛈️"
        if 300 <= weather_id <= 321: return "🌦️"
        if 500 <= weather_id <= 531: return "🌧️"
        if 600 <= weather_id <= 622: return "❄️"
        if 700 <= weather_id <= 781: return "🌫️"
        if weather_id == 800:        return "☀️"
        if 801 <= weather_id <= 804: return "☁️"
        return "🌡️"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WeatherApp()
    window.show()
    sys.exit(app.exec_())