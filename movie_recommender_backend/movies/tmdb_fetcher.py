# movies/tmdb_fetcher.py
import os
import time
import requests
import pandas as pd
import pickle
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from django.conf import settings
from decouple import config

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_API_KEY = config('TMDB_API_KEY')

def get_headers():
    return {
        "Authorization": f"Bearer {TMDB_API_KEY}",
        "accept": "application/json",
    }


# ─────────────────────────────────────────────
# FETCH FROM TMDB
# ─────────────────────────────────────────────

def fetch_popular_movies(total_pages=100):
    all_movies = []
    print(f"Fetching movies from TMDB ({total_pages} pages)...")
    for page in range(1, total_pages + 1):
        try:
            response = requests.get(
                f"{TMDB_BASE_URL}/movie/popular",
                headers=get_headers(),
                params={"page": page, "language": "en-US"},
            )
            response.raise_for_status()
            all_movies.extend(response.json().get("results", []))
            if page % 10 == 0:
                print(f"  Fetched page {page}/{total_pages} ({len(all_movies)} movies so far)")
            time.sleep(0.05)
        except requests.RequestException as e:
            print(f"  Error on page {page}: {e}")
            continue
    print(f"Total movies fetched: {len(all_movies)}")
    return all_movies


def fetch_movie_details(movie_id):
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/movie/{movie_id}",
            headers=get_headers(),
            params={"append_to_response": "keywords,credits"},
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


# ─────────────────────────────────────────────
# PROCESS: same logic as the notebook
# ─────────────────────────────────────────────

def build_rich_tags(movie_detail):
    """
    Builds natural language sentences — same function as the notebook.
    The embedding model understands sentences far better than word soup.
    """
    parts = []

    overview = movie_detail.get("overview", "")
    if overview:
        parts.append(overview)

    genres = [g["name"] for g in movie_detail.get("genres", [])]
    if genres:
        parts.append(f"This is a {', '.join(genres)} film.")

    keywords_data = movie_detail.get("keywords", {}).get("keywords", [])
    keywords = [k["name"] for k in keywords_data[:8]]
    if keywords:
        parts.append(f"Themes include {', '.join(keywords)}.")

    crew_data = movie_detail.get("credits", {}).get("crew", [])
    directors = [p["name"] for p in crew_data if p["job"] == "Director"]
    if directors:
        parts.append(f"Directed by {directors[0]}.")

    cast_data = movie_detail.get("credits", {}).get("cast", [])
    if cast_data:
        parts.append(f"Starring {cast_data[0]['name']}.")  # lead actor only

    return " ".join(parts)


def process_movie(movie_detail):
    if not movie_detail:
        return None

    genres = [g["name"] for g in movie_detail.get("genres", [])]
    tags   = build_rich_tags(movie_detail)

    release_date = movie_detail.get("release_date", "")
    release_year = int(release_date[:4]) if release_date and len(release_date) >= 4 else None

    return {
        "movie_id":     movie_detail["id"],
        "title":        movie_detail.get("title", ""),
        "overview":     movie_detail.get("overview", ""),
        "genres":       genres,        # kept as list for genre scoring
        "release_year": release_year,
        "poster_path":  movie_detail.get("poster_path", ""),
        "vote_average": movie_detail.get("vote_average", 0.0),
        "vote_count":   movie_detail.get("vote_count", 0),
        "tags":         tags,
    }


# ─────────────────────────────────────────────
# REBUILD SIMILARITY — sentence embeddings + popularity
# ─────────────────────────────────────────────

def rebuild_similarity_matrix(movies_df):
    print("Rebuilding similarity matrix with sentence embeddings...")

    movies_df = movies_df[movies_df["tags"].str.strip() != ""].reset_index(drop=True)

    # Sentence embeddings (same model as notebook)
    model      = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(
        movies_df["tags"].tolist(),
        show_progress_bar=True,
        batch_size=64,
    )
    similarity = cosine_similarity(embeddings)

    # Popularity score (IMDB weighted rating) — same as notebook
    C = movies_df["vote_average"].mean()
    m = movies_df["vote_count"].quantile(0.75)

    def weighted_rating(row):
        v = row["vote_count"]
        R = row["vote_average"]
        return (v / (v + m)) * R + (m / (v + m)) * C

    movies_df["popularity_score"] = movies_df.apply(weighted_rating, axis=1)
    min_p = movies_df["popularity_score"].min()
    max_p = movies_df["popularity_score"].max()
    movies_df["popularity_score"] = (movies_df["popularity_score"] - min_p) / (max_p - min_p)

    # Save
    ml_dir = settings.ML_DATA_DIR
    os.makedirs(ml_dir, exist_ok=True)
    movies_df.to_csv(os.path.join(ml_dir, "movies_clean.csv"), index=False)
    with open(os.path.join(ml_dir, "similarity.pkl"), "wb") as f:
        pickle.dump(similarity, f)

    print(f"✅ Saved {len(movies_df)} movies to {ml_dir}")
    return movies_df, similarity


# ─────────────────────────────────────────────
# FULL REFRESH
# ─────────────────────────────────────────────

def full_refresh(pages=100):
    from movies.models import Movie

    popular   = fetch_popular_movies(total_pages=pages)
    movie_ids = list({m["id"] for m in popular})

    processed = []
    print(f"\nFetching details for {len(movie_ids)} movies...")
    for i, movie_id in enumerate(movie_ids):
        detail = fetch_movie_details(movie_id)
        result = process_movie(detail)
        if result and result["tags"]:
            processed.append(result)
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{len(movie_ids)}")
        time.sleep(0.05)

    df = pd.DataFrame(processed)
    df.drop_duplicates(subset=["movie_id"], inplace=True)

    df, similarity = rebuild_similarity_matrix(df)

    print("\nUpdating database...")
    Movie.objects.all().delete()
    Movie.objects.bulk_create([
        Movie(
            movie_id=    int(row["movie_id"]),
            title=       str(row["title"]),
            tags=        str(row["tags"]),
            release_year=int(row["release_year"]) if pd.notna(row.get("release_year")) else None,
            poster_path= str(row.get("poster_path", "") or ""),
            vote_average=float(row.get("vote_average", 0.0) or 0.0),
        )
        for _, row in df.iterrows()
    ])

    total = Movie.objects.count()
    print(f"✅ Database updated with {total} movies!")
    return total