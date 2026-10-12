from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Netflix Content Analytics", page_icon="🎬", layout="wide")

DATA_CANDIDATES = [
    Path(__file__).parent / "cleaned_netflix.csv",
    Path(__file__).parent / "netflix_titles.csv",
]

RED = "#E50914"
DARK = "#0b0b0b"
PANEL = "#171717"

st.markdown(f"""
<style>
.stApp {{ background: {DARK}; color: #f5f5f1; }}
[data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}
[data-testid="stSidebar"] {{ background: #141414; }}
h1, h2, h3 {{ color: #ffffff; }}
.hero {{ padding: 1.2rem 0 .8rem 0; }}
.hero-kicker {{ color: {RED}; font-weight: 800; letter-spacing: .18em; }}
.hero-title {{ font-size: clamp(2rem, 4vw, 3.4rem); font-weight: 850; line-height: 1.05; }}
.hero-sub {{ color: #bdbdbd; font-size: 1.05rem; }}
div[data-testid="stMetric"] {{ background: {PANEL}; border: 1px solid #292929; padding: 1rem; border-radius: 12px; }}
div[data-testid="stMetricLabel"] {{ color: #bdbdbd; }}
div[data-testid="stMetricValue"] {{ color: #ffffff; }}
.stButton button {{ background: {RED}; color: white; border: 0; }}
hr {{ border-color: #303030; }}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    for path in DATA_CANDIDATES:
        if path.exists() and path.stat().st_size > 10:
            try:
                data = pd.read_csv(path)
                if not data.empty and "title" in data.columns:
                    return data, path.name
            except (pd.errors.ParserError, UnicodeDecodeError):
                continue
    raise FileNotFoundError("No usable dataset found. Add cleaned_netflix.csv to the project folder.")


try:
    df, data_source = load_data()
except Exception as exc:
    st.error(f"Could not load the Netflix dataset: {exc}")
    st.stop()

# Normalize expected fields so the app can handle either the cleaned or original dataset.
for col in ["type", "title", "director", "cast", "country", "rating", "duration",
            "listed_in", "description", "primary_genre", "month_added"]:
    if col not in df.columns:
        df[col] = "Unknown"
    df[col] = df[col].fillna("Unknown").astype(str).replace({"nan": "Unknown", "": "Unknown"})
for col in ["release_year", "year_added"]:
    if col not in df.columns:
        df[col] = pd.NA
    df[col] = pd.to_numeric(df[col], errors="coerce")
if "date_added" in df.columns:
    df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
else:
    df["date_added"] = pd.NaT
if "primary_genre" not in df.columns or (df["primary_genre"] == "Unknown").all():
    df["primary_genre"] = df["listed_in"].str.split(",").str[0].fillna("Unknown").str.strip()

st.markdown(f"""
<div class="hero">
  <div class="hero-kicker">STREAMING DATA • INSIGHTS</div>
  <div class="hero-title">NETFLIX <span style="color:{RED}">CONTENT</span> ANALYTICS</div>
  <div class="hero-sub">Explore the catalog, discover content trends, and filter titles in one place.</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"<h2 style='color:{RED}'>🎬 Explore</h2>", unsafe_allow_html=True)
    search = st.text_input("Search titles", placeholder="Search a movie or show…")
    types = sorted(df["type"].dropna().unique().tolist())
    selected_types = st.multiselect("Content type", types, default=types)
    ratings = sorted(df.loc[df["rating"] != "Unknown", "rating"].unique().tolist())
    selected_ratings = st.multiselect("Content rating", ratings, default=ratings)
    genres = sorted(df.loc[df["primary_genre"] != "Unknown", "primary_genre"].unique().tolist())
    selected_genres = st.multiselect("Primary genre", genres, default=genres)
    years = df["release_year"].dropna()
    if not years.empty:
        min_year, max_year = int(years.min()), int(years.max())
        year_range = st.slider("Release year", min_year, max_year, (min_year, max_year))
    else:
        year_range = (1900, 2100)
    st.caption(f"Dataset: {data_source}")

filtered = df.copy()
if selected_types:
    filtered = filtered[filtered["type"].isin(selected_types)]
else:
    filtered = filtered.iloc[0:0]
if selected_ratings:
    filtered = filtered[filtered["rating"].isin(selected_ratings)]
elif ratings:
    filtered = filtered.iloc[0:0]
if selected_genres:
    filtered = filtered[filtered["primary_genre"].isin(selected_genres)]
elif genres:
    filtered = filtered.iloc[0:0]
filtered = filtered[filtered["release_year"].between(*year_range) | filtered["release_year"].isna()]
if search.strip():
    query = search.strip().casefold()
    searchable = filtered[["title", "director", "cast", "listed_in", "country", "description"]].fillna("").astype(str).agg(" ".join, axis=1)
    filtered = filtered[searchable.str.casefold().str.contains(query, regex=False)]

st.caption(f"Showing **{len(filtered):,}** of **{len(df):,}** titles after filters.")
total = len(filtered)
movies = int((filtered["type"].str.casefold() == "movie").sum())
shows = int((filtered["type"].str.casefold() == "tv show").sum())
countries_count = filtered.loc[filtered["country"] != "Unknown", "country"].str.split(", ").explode().nunique()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Titles", f"{total:,}")
c2.metric("Movies", f"{movies:,}")
c3.metric("TV Shows", f"{shows:,}")
c4.metric("Countries represented", f"{countries_count:,}")

def chart_layout(fig, height=350):
    fig.update_layout(
        height=height, paper_bgcolor=PANEL, plot_bgcolor=PANEL,
        font_color="#f5f5f1", margin=dict(l=12, r=12, t=45, b=12),
        title_font_size=17, legend_title_text=""
    )
    fig.update_xaxes(gridcolor="#333333")
    fig.update_yaxes(gridcolor="#333333")
    return fig

st.markdown("## Catalog overview")
left, right = st.columns(2)
with left:
    counts = filtered["type"].value_counts().rename_axis("Content type").reset_index(name="Titles")
    fig = px.pie(counts, names="Content type", values="Titles", hole=.58,
                 color_discrete_sequence=[RED, "#777777"], title="Movies vs TV Shows")
    fig.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(chart_layout(fig), use_container_width=True)
with right:
    genre_counts = filtered["primary_genre"].replace("Unknown", pd.NA).dropna().value_counts().head(10).sort_values()
    fig = px.bar(genre_counts, x=genre_counts.values, y=genre_counts.index, orientation="h",
                 labels={"x": "Titles", "y": "Genre"}, title="Top 10 primary genres",
                 color_discrete_sequence=[RED])
    st.plotly_chart(chart_layout(fig), use_container_width=True)

left, right = st.columns(2)
with left:
    year_counts = filtered.dropna(subset=["release_year"]).groupby("release_year").size().reset_index(name="Titles")
    fig = px.line(year_counts, x="release_year", y="Titles", markers=True, title="Titles by release year",
                  labels={"release_year": "Release year"}, color_discrete_sequence=[RED])
    st.plotly_chart(chart_layout(fig), use_container_width=True)
with right:
    rating_counts = filtered[filtered["rating"] != "Unknown"]["rating"].value_counts().head(12).sort_values()
    fig = px.bar(rating_counts, x=rating_counts.values, y=rating_counts.index, orientation="h",
                 labels={"x": "Titles", "y": "Rating"}, title="Content ratings",
                 color_discrete_sequence=["#E50914"])
    st.plotly_chart(chart_layout(fig), use_container_width=True)

left, right = st.columns(2)
with left:
    country_counts = filtered.loc[filtered["country"] != "Unknown", "country"].str.split(", ").explode().value_counts().head(10).sort_values()
    fig = px.bar(country_counts, x=country_counts.values, y=country_counts.index, orientation="h",
                 labels={"x": "Titles", "y": "Country"}, title="Top 10 countries",
                 color_discrete_sequence=["#b20710"])
    st.plotly_chart(chart_layout(fig), use_container_width=True)
with right:
    added = filtered.dropna(subset=["date_added"]).copy()
    if not added.empty:
        added["Added year"] = added["date_added"].dt.year
        added_counts = added.groupby("Added year").size().reset_index(name="Titles")
        fig = px.bar(added_counts, x="Added year", y="Titles", title="Titles added to Netflix by year",
                     color_discrete_sequence=[RED])
        st.plotly_chart(chart_layout(fig), use_container_width=True)
    else:
        st.info("No valid date_added values are available for this filter.")

st.markdown("## Find a title")
display_cols = [c for c in ["title", "type", "release_year", "rating", "duration", "primary_genre", "country", "director", "date_added", "description"] if c in filtered.columns]
st.dataframe(filtered[display_cols].sort_values("title"), use_container_width=True, hide_index=True, height=380)
csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download filtered data (CSV)", data=csv, file_name="netflix_filtered_titles.csv", mime="text/csv")

st.markdown("---")
st.caption("Educational analytics project • Built with Python, Pandas, Plotly and Streamlit. Netflix is a trademark of its respective owner.")
