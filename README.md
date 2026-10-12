# Netflix Content Analytics Dashboard

A beginner-friendly interactive dashboard built with Python, Streamlit, Pandas and Plotly. It uses the dataset included in this repository and does not require API keys.

## Features
- Netflix-inspired dark interface with red accents
- KPIs for total titles, movies, TV shows and countries represented
- Filters for title search, content type, rating, genre and release year
- Interactive charts for content type, genres, release years, ratings, countries and dates added
- Searchable title table and CSV download of filtered results
- Includes the original analysis notebook and chart images

## Run locally
Python 3.10–3.12 is recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Streamlit will show a local URL in your terminal, usually http://localhost:8501.

## Deploy for free with Streamlit Community Cloud
1. Create a GitHub repository and upload the files in this project folder.
2. Visit https://share.streamlit.io/ and sign in with GitHub.
3. Select **Create app**, choose your repository and branch, and set the main file path to `app.py`.
4. Select **Deploy**. No secrets or API keys are required.

Keep `app.py`, `requirements.txt`, and `cleaned_netflix.csv` in the repository root so the app can find them.

## Dataset note
The ZIP originally contained an empty `netflix_titles.csv`. To avoid a broken data path, that file has been populated with the available `cleaned_netflix.csv` dataset. The app loads the cleaned dataset by default.

## Project contents
- `app.py` — Streamlit application
- `cleaned_netflix.csv` — dataset used by the dashboard
- `netflix_titles.csv` — compatible dataset filename for the existing notebook workflow
- `Netflix_Content_Analytics.ipynb` — existing analysis notebook
- `*.png` — existing charts from the original project
- `requirements.txt` — deployment dependencies
