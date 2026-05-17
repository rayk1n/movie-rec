from django.shortcuts import render
import os
import pickle
import pandas as pd
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

ML_DIR = settings.ML_DATA_DIR

try:
    # Load the similarity matrix we built in Phase 1
    with open(os.path.join(ML_DIR, 'similarity.pkl'), 'rb') as f:
        similarity = pickle.load(f)

    # Load the cleaned movie dataframe
    movies_df = pd.read_csv(os.path.join(ML_DIR, 'movies_clean.csv'))

    print("✅ ML data loaded successfully")

except FileNotFoundError as e:
    print(f"⚠️  WARNING: Could not load ML data: {e}")
    similarity = None
    movies_df = None


@api_view(['GET'])
def recommend(request):
    """
    GET /api/recommend/?title=Inception
    
    Returns a JSON object like:
    {
        "query": "Inception",
        "recommendations": [
            {"title": "Interstellar", "movie_id": 157336},
            ...
        ]
    }
    """
    
    # Check if ML data is available
    if similarity is None or movies_df is None:
        return Response(
            {"error": "Recommendation engine not available. Check ML data files."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    # Get the ?title= query parameter from the URL
    title = request.query_params.get('title', '').strip()

    if not title:
        return Response(
            {"error": "Please provide a 'title' query parameter. E.g. /api/recommend/?title=Inception"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # ── Find the movie (case-insensitive) ──
    matches = movies_df[movies_df['title'].str.lower() == title.lower()]

    if matches.empty:
        # Try a partial match as a helpful suggestion
        partial = movies_df[movies_df['title'].str.lower().str.contains(title.lower())]
        suggestions = partial['title'].head(5).tolist()

        return Response({
            "error": f"Movie '{title}' not found.",
            "suggestions": suggestions
        }, status=status.HTTP_404_NOT_FOUND)

    # ── Calculate recommendations ──
    idx = matches.index[0]
    sim_scores = list(enumerate(similarity[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]  # Top 10, skip self

    # Build the response list
    movie_indices = [i[0] for i in sim_scores]
    recommendations = []
    for i, score in zip(movie_indices, [s[1] for s in sim_scores]):
        row = movies_df.iloc[i]
        recommendations.append({
            "title":      row['title'],
            "movie_id":   int(row['movie_id']),
            "similarity": round(float(score), 4),
        })

    return Response({
        "query":           title,
        "recommendations": recommendations,
    })


@api_view(['GET'])
def search_movies(request):
    """
    GET /api/search/?q=dark
    
    Returns a list of movies whose title contains the query.
    Used by the React search bar for autocomplete.
    """
    query = request.query_params.get('q', '').strip()

    if not query or len(query) < 2:
        return Response({"results": []})

    if movies_df is None:
        return Response({"error": "Data not available"}, status=503)

    # Filter movies by title (case-insensitive)
    mask = movies_df['title'].str.lower().str.contains(query.lower(), na=False)
    results = movies_df[mask]['title'].head(10).tolist()

    return Response({"results": results})
