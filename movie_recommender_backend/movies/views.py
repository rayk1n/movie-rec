from django.shortcuts import render
import os
import ast
import pickle
import pandas as pd
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

ML_DIR = settings.ML_DATA_DIR

try:
    with open(os.path.join(ML_DIR, 'similarity.pkl'), 'rb') as f:
        similarity = pickle.load(f)
    movies_df = pd.read_csv(os.path.join(ML_DIR, 'movies_clean.csv'))

    # genres column is saved as a string like "['Romance', 'Drama']"
    # we need to convert it back to an actual Python list
    movies_df['genres'] = movies_df['genres'].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else []
    )

    print("✅ ML data loaded successfully")

except FileNotFoundError as e:
    print(f"⚠️  WARNING: Could not load ML data: {e}")
    similarity = None
    movies_df  = None


# ─────────────────────────────────────────────
# GENRE HELPERS (same logic as the notebook)
# ─────────────────────────────────────────────

INCOMPATIBLE_GENRES = [
    {'Horror', 'Thriller'},
    {'Romance', 'Comedy', 'Family'},
    {'Animation', 'Family'},
]

def genres_are_compatible(genres_a, genres_b):
    set_a = set(genres_a)
    set_b = set(genres_b)
    for group in INCOMPATIBLE_GENRES:
        if bool(set_a & group) != bool(set_b & group):
            return False
    return True

def genre_overlap_score(genres_a, genres_b):
    if not genres_a or not genres_b:
        return 0.7
    set_a   = set(genres_a)
    set_b   = set(genres_b)
    jaccard = len(set_a & set_b) / len(set_a | set_b)
    return 0.3 + (0.7 * jaccard)


# ─────────────────────────────────────────────
# VIEWS
# ─────────────────────────────────────────────

@api_view(['GET'])
def recommend(request):
    if similarity is None or movies_df is None:
        return Response(
            {"error": "Recommendation engine not available."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    title = request.query_params.get('title', '').strip()
    if not title:
        return Response(
            {"error": "Please provide a 'title' query parameter."},
            status=status.HTTP_400_BAD_REQUEST
        )

    matches = movies_df[movies_df['title'].str.lower() == title.lower()]
    if matches.empty:
        partial     = movies_df[movies_df['title'].str.lower().str.contains(title.lower())]
        suggestions = partial['title'].head(5).tolist()
        return Response(
            {"error": f"Movie '{title}' not found.", "suggestions": suggestions},
            status=status.HTTP_404_NOT_FOUND
        )

    idx          = matches.index[0]
    query_genres = movies_df.iloc[idx]['genres']

    # Fix 4: adjust raw scores by genre overlap
    sim_scores = []
    for i, raw_score in enumerate(similarity[idx]):
        candidate_genres = movies_df.iloc[i]['genres']
        bonus            = genre_overlap_score(query_genres, candidate_genres)
        adjusted_score   = raw_score * bonus
        sim_scores.append((i, adjusted_score))

    # Sort highest first, skip the movie itself
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:]

    # Fix 2: walk down the list, skip genre-incompatible movies
    recommendations = []
    for movie_idx, score in sim_scores:
        candidate_genres = movies_df.iloc[movie_idx]['genres']
        if genres_are_compatible(query_genres, candidate_genres):
            row = movies_df.iloc[movie_idx]

            poster_path  = str(row.get('poster_path', '') or '')
            poster_url   = (
                f"https://image.tmdb.org/t/p/w342{poster_path}"
                if poster_path and poster_path != 'nan'
                else "https://via.placeholder.com/342x513?text=No+Poster"
            )

            release_year = row.get('release_year')
            try:
                release_year = int(release_year) if pd.notna(release_year) else None
            except (ValueError, TypeError):
                release_year = None

            recommendations.append({
                "title":        row['title'],
                "movie_id":     int(row['movie_id']),
                "similarity":   round(float(score), 4),
                "poster_url":   poster_url,
                "release_year": release_year,
                "vote_average": round(float(row.get('vote_average', 0) or 0), 1),
            })

        if len(recommendations) >= 10:
            break

    return Response({"query": title, "recommendations": recommendations})


@api_view(['GET'])
def search_movies(request):
    query = request.query_params.get('q', '').strip()
    if not query or len(query) < 2:
        return Response({"results": []})
    if movies_df is None:
        return Response({"error": "Data not available"}, status=503)

    mask    = movies_df['title'].str.lower().str.contains(query.lower(), na=False)
    subset  = movies_df[mask].head(10)

    results = []
    for _, row in subset.iterrows():
        year = row.get('release_year')
        try:
            year = int(year) if pd.notna(year) else None
        except (ValueError, TypeError):
            year = None
        results.append({"title": row['title'], "release_year": year})

    return Response({"results": results})


def reload_ml_data():
    global similarity, movies_df
    try:
        with open(os.path.join(ML_DIR, 'similarity.pkl'), 'rb') as f:
            similarity = pickle.load(f)
        movies_df = pd.read_csv(os.path.join(ML_DIR, 'movies_clean.csv'))
        movies_df['genres'] = movies_df['genres'].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else []
        )
        print("✅ ML data reloaded")
    except Exception as e:
        print(f"Reload failed: {e}")


@api_view(['POST'])
def reload_data(request):
    reload_ml_data()
    return Response({"status": "reloaded", "movies": len(movies_df) if movies_df is not None else 0})