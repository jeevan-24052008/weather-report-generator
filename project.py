import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

import requests
from fpdf import FPDF

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
DEFAULT_TIMEOUT = 10


def get_api_key() -> str:
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENWEATHER_API_KEY is not set. Set it as an environment variable."
        )
    return api_key


def fetch_weather(city: str, api_key: str | None = None) -> dict:
    city = city.strip()
    if not city:
        raise ValueError("City name cannot be empty.")

    api_key = api_key or get_api_key()
    session = requests.Session()

    geo_response = session.get(
        "https://api.openweathermap.org/geo/1.0/direct",
        params={"q": city, "limit": 1, "appid": api_key},
        timeout=DEFAULT_TIMEOUT,
    )
    geo_response.raise_for_status()
    locations = geo_response.json()
    if not locations:
        raise ValueError(f"City '{city}' was not found.")

    location = locations[0]
    weather_response = session.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={
            "lat": location["lat"],
            "lon": location["lon"],
            "appid": api_key,
            "units": "metric",
        },
        timeout=DEFAULT_TIMEOUT,
    )
    weather_response.raise_for_status()
    data = weather_response.json()
    data["resolved_city"] = location.get("name", city)
    data["resolved_country"] = location.get("country", "")
    return data


def _weather_background(weather_type: str) -> Path:
    weather_type = weather_type.lower()
    if weather_type == "rain":
        preferred = ASSETS_DIR / "rain.jpg"
    else:
        preferred = ASSETS_DIR / "clear.jpg"

    if preferred.exists():
        return preferred
    raise FileNotFoundError(f"Background image not found: {preferred}")


def generate_weather_report(city: str, output_dir: str | Path | None = None) -> Path:
    data = fetch_weather(city)
    resolved_city = data["resolved_city"]
    weather_type = data["weather"][0]["main"]

    main = data["main"]
    wind = data.get("wind", {})
    rain_data = data.get("rain", {})

    temperature = round(main["temp"])
    feels_like = round(main["feels_like"])
    max_temp = round(main["temp_max"])
    min_temp = round(main["temp_min"])
    humidity = main.get("humidity", 0)
    pressure = main.get("pressure", 0)
    visibility = round(data.get("visibility", 0) / 1000, 1)
    wind_kph = round(float(wind.get("speed", 0)) * 3.6, 1)
    rain_1h = round(float(rain_data.get("1h", 0)), 1)

    pdf = FPDF(orientation="landscape", format="A4")
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    background = _weather_background(weather_type)
    pdf.image(str(background), x=1, y=1, w=295, h=210)

    pdf.rect(x=9, y=40, w=277, h=160)

    pdf.set_font("times", "B", 35)
    pdf.cell(0, 15, " WEATHER REPORT ", ln=1, align="C")

    pdf.set_font("helvetica", "B", 30)
    pdf.cell(0, 20, resolved_city.upper(), ln=1, align="C")

    pdf.set_font("times", "BI", 25)
    pdf.cell(120, 20, f"-> TYPE: {weather_type}", ln=0, align="L")
    pdf.cell(135, 20, f"-> TEMP: {temperature} °C", ln=1, align="R")
    pdf.cell(120, 20, f"-> FEELS LIKE: {feels_like} °C", ln=0, align="L")
    pdf.cell(135, 20, f"-> MAX TEMP: {max_temp} °C", ln=1, align="R")
    pdf.cell(120, 20, f"-> WIND: {wind_kph} KPH", ln=0, align="L")
    pdf.cell(135, 20, f"-> MIN TEMP: {min_temp} °C", ln=1, align="R")
    pdf.cell(120, 20, f"-> VISIBILITY: {visibility} KM", ln=0, align="L")
    pdf.cell(135, 20, f"-> PRESSURE: {pressure} hPa", ln=1, align="R")
    pdf.cell(120, 20, f"-> HUMIDITY: {humidity} %", ln=0, align="L")
    pdf.cell(135, 20, f"-> RAIN: {rain_1h} mm", ln=1, align="R")

    updated = datetime.now().strftime("%Y-%m-%d")
    pdf.set_font("times", "B", 20)
    pdf.cell(120, 40, f"Data last updated: {updated}", ln=1, align="L")
    pdf.set_font("times", "B", 15)
    pdf.cell(120, 1, "Powered by OpenWeatherMap", ln=1, align="L")

    output_dir = Path(output_dir) if output_dir else BASE_DIR / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_city = "_".join(resolved_city.split())
    output_path = output_dir / f"{safe_city}_weather.pdf"
    pdf.output(str(output_path))
    return output_path


def main() -> None:
    city = input("Enter city: ").strip()
    try:
        pdf_path = generate_weather_report(city)
        print(f"PDF generated successfully: {pdf_path}")
    except requests.RequestException as exc:
        print(f"Weather API error: {exc}")
    except (ValueError, RuntimeError, FileNotFoundError) as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()
