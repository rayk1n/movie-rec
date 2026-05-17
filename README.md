# 🎬 CineMatch — AI-Powered Movie Recommender

A full-stack content-based movie recommendation system that suggests films based on semantic similarity — understanding the *vibe* and *meaning* of movies, not just shared keywords.

---

## Demo

> Search for any movie → get 10 semantically similar recommendations with posters, release year, and match score.

**Example:** Search "About Time" → get "All of Us Strangers", "The Lake House", "The Time Traveler's Wife" — films with the same bittersweet, romantic, emotionally introspective tone.

---

## How It Works

Traditional recommendation systems match movies by counting shared words (TF-IDF). This project uses **sentence embeddings** instead — a neural network that understands the *meaning* of text.

```
Movie description + genres + keywords + director
        ↓
SentenceTransformer ('all-MiniLM-L6-v2')
        ↓
384-dimensional semantic vector
        ↓
Cosine similarity against all other movies
        ↓
Genre compatibility filtering (no horror in romance results)
        ↓
Top 10 recommendations
```

Two additional filters improve quality:
- **Genre overlap scoring** — adjusts similarity scores based on genre match (same genres score higher)
- **Genre incompatibility filter** — hard blocks cross-genre results (e.g. horror never appears in romance recommendations)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Axios, react-hot-toast |
| Backend | Django, Django REST Framework |
| Database | PostgreSQL |
| ML | sentence-transformers, scikit-learn, pandas |
| Movie Data | TMDB API (live, auto-refreshes weekly) |
| Containerization | Docker, Docker Compose |
| Web Server | Gunicorn + nginx |

---

## Features

- 🔍 **Semantic search** — finds movies by meaning, not just keywords
- 🎭 **Genre-aware filtering** — no horror films appearing in romance results
- 🖼️ **Real movie posters** — fetched from TMDB's image CDN
- 📅 **Release year** — shown on every card and in autocomplete
- ⭐ **Ratings** — IMDB-style weighted rating displayed per movie
- 🔄 **Live data** — TMDB API integration with weekly auto-refresh
- 🐳 **Dockerized** — entire stack runs with one command

---

## Project Structure

```
movie-rec/
├── movie_recommender_backend/   # Django API
│   ├── core/                    # Settings, URLs
│   ├── movies/                  # Models, views, recommendation logic
│   │   ├── views.py             # API endpoints + genre filtering
│   │   ├── tmdb_fetcher.py      # TMDB API integration + embedding builder
│   │   ├── scheduler.py         # Weekly auto-refresh
│   │   └── management/
│   │       └── commands/
│   │           └── refresh_movies.py
│   └── ml_data/                 # similarity.pkl + movies_clean.csv
├── movie-frontend/              # React app
│   ├── src/
│   │   ├── components/
│   │   │   ├── SearchBar.js     # Autocomplete search
│   │   │   └── MovieCard.js     # Poster + info card
│   │   ├── App.js               # Main component + state
│   │   └── api.js               # Axios configuration
│   └── nginx.conf               # Proxies /api/ to Django
├── docker-compose.yml           # Orchestrates all three containers
└── ml.ipynb                     # Jupyter notebook (ML experimentation)
```

---

## Getting Started

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- A free [TMDB API key](https://www.themoviedb.org/settings/api)

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/movie-rec.git
cd movie-rec
```

### 2. Create the `.env` file in the project root
```env
SECRET_KEY=your-django-secret-key
DEBUG=False
DB_NAME=movie_db
DB_USER=movie_user
DB_PASSWORD=yourpassword
TMDB_API_KEY=your-tmdb-api-read-access-token
```

### 3. Start everything
```bash
docker compose up --build -d
```

First run takes a few minutes to build images.

### 4. Load movie data
```bash
docker compose exec django python manage.py refresh_movies --pages 100
```

This fetches ~2000 movies from TMDB, builds the semantic similarity matrix, and populates the database. Takes about 10–15 minutes.

### 5. Open the app
```
http://localhost:3000
```

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/recommend/?title=Inception` | GET | Get 10 similar movies |
| `/api/search/?q=dark` | GET | Autocomplete title search |
| `/api/reload/` | POST | Reload ML data after refresh |

### Example Response
```json
{
    "query": "Inception",
    "recommendations": [
        {
            "title": "Minority Report",
            "movie_id": 180,
            "similarity": 0.4821,
            "poster_url": "https://image.tmdb.org/t/p/w342/...",
            "release_year": 2002,
            "vote_average": 7.5
        }
    ]
}
```

---

## Docker Commands

```bash
# Start
docker compose up -d

# Stop
docker compose down

# Rebuild after code changes
docker compose up --build -d

# View Django logs
docker compose logs -f django

# Refresh movie data
docker compose exec django python manage.py refresh_movies --pages 100
```

---

## ML Approach

The recommendation engine went through two iterations:

**v1 — TF-IDF (discarded)**
Word frequency vectors. Fast but no semantic understanding — "Hot Tub Time Machine" and "About Time" scored as similar just because both contain "time".

**v2 — Sentence Embeddings (current)**
`all-MiniLM-L6-v2` from the `sentence-transformers` library converts natural language descriptions into 384-dimensional vectors. Movies with similar *meaning* cluster together regardless of exact wording. "A bittersweet romance across time" and "a magical love story with emotional depth" end up close in vector space.

---