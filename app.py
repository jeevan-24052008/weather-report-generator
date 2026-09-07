from flask import Flask, render_template, request, send_file
import requests

from project import generate_weather_report

app = Flask(__name__)


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/generate")
def generate():
    city = request.form.get("city", "").strip()
    if not city:
        return render_template("index.html", error="Please enter a city name.", city=city), 400

    try:
        pdf_path = generate_weather_report(city)
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=pdf_path.name,
            mimetype="application/pdf",
        )
    except requests.RequestException:
        return render_template(
            "index.html",
            error="Could not reach the weather service. Please try again.",
            city=city,
        ), 502
    except (ValueError, RuntimeError, FileNotFoundError) as exc:
        return render_template("index.html", error=str(exc), city=city), 400


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
