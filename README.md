# Weather Report Generator

A lightweight Python weather-report PDF generator with both terminal and tiny web modes.

## Modes

### Terminal

```bash
python project.py
```

Then enter a city, for example `Chennai`.

### Web

```bash
python app.py
```

Open `http://127.0.0.1:5000` and enter a city to download the PDF.

## API key

Set the `OPENWEATHER_API_KEY` environment variable. Do not commit `.env` or a real API key to GitHub.

Windows PowerShell example:

```powershell
$env:OPENWEATHER_API_KEY="YOUR_NEW_KEY"
```

## Deployment on Render

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Environment variable: `OPENWEATHER_API_KEY=<your key>`

The project includes `.python-version` set to Python 3.13 for a predictable deployment runtime.
