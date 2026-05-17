import React, { useState } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import SearchBar from './components/SearchBar';
import MovieCard from './components/MovieCard';
import api from './api';
import './App.css';

function App() {
    // State variables — React re-renders the UI whenever these change
    const [recommendations, setRecommendations] = useState([]);  // List of recommended movies
    const [queriedMovie, setQueriedMovie]       = useState('');   // The movie we searched for
    const [isLoading, setIsLoading]             = useState(false);// Are we fetching from Django?
    const [error, setError]                     = useState(null); // Any error message

    /**
     * fetchRecommendations(title)
     * 
     * Calls the Django API and updates the state with results.
     * This function is passed down to SearchBar and MovieCard so they can trigger it.
     */
    async function fetchRecommendations(title) {
        if (!title.trim()) return;

        setIsLoading(true);
        setError(null);

        try {
            const response = await api.get(`/recommend/?title=${encodeURIComponent(title)}`);
            const data = response.data;

            setQueriedMovie(data.query);
            setRecommendations(data.recommendations);

            toast.success(`Found ${data.recommendations.length} recommendations!`);

        } catch (err) {
            if (err.response) {
                // Django returned an error response (4xx, 5xx)
                const errData = err.response.data;

                if (err.response.status === 404) {
                    const msg = errData.error || 'Movie not found';
                    setError({ message: msg, suggestions: errData.suggestions || [] });
                    toast.error('Movie not found!');
                } else {
                    setError({ message: errData.error || 'Server error' });
                    toast.error('Something went wrong on the server.');
                }
            } else {
                // Network error — Django probably isn't running
                setError({ message: 'Cannot connect to the server. Is Django running?' });
                toast.error('Connection failed. Is Django running on port 8000?');
            }

            setRecommendations([]);
        } finally {
            setIsLoading(false);
        }
    }

    return (
        <div className="app">
            {/* Toast notifications (the little popups) */}
            <Toaster position="top-right" />

            {/* ── HEADER ── */}
            <header className="header">
                <div className="header-content">
                    <h1 className="logo">🎬 CineMatch</h1>
                    <p className="tagline">Discover movies you'll love, powered by AI</p>
                </div>
            </header>

            {/* ── MAIN CONTENT ── */}
            <main className="main-content">

                {/* ── SEARCH SECTION ── */}
                <section className="search-section">
                    <h2>Find your next favorite movie</h2>
                    <p className="search-hint">
                        Type a movie name and we'll find 10 similar movies for you
                    </p>
                    <SearchBar
                        onMovieSelect={fetchRecommendations}
                        isLoading={isLoading}
                    />
                </section>

                {/* ── LOADING STATE ── */}
                {isLoading && (
                    <div className="loading">
                        <div className="spinner"></div>
                        <p>Finding similar movies...</p>
                    </div>
                )}

                {/* ── ERROR STATE ── */}
                {error && !isLoading && (
                    <div className="error-box">
                        <p>❌ {error.message}</p>
                        {error.suggestions && error.suggestions.length > 0 && (
                            <div className="suggestions-list">
                                <p>Did you mean:</p>
                                {error.suggestions.map((s, i) => (
                                    <button
                                        key={i}
                                        className="suggestion-btn"
                                        onClick={() => fetchRecommendations(s)}
                                    >
                                        {s}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {/* ── RESULTS SECTION ── */}
                {recommendations.length > 0 && !isLoading && (
                    <section className="results-section">
                        <h2 className="results-title">
                            Because you liked <span className="highlight">"{queriedMovie}"</span>
                        </h2>
                        <p className="results-subtitle">
                            Click any movie below to get recommendations for it
                        </p>

                        <div className="movie-grid">
                            {recommendations.map((movie, index) => (
                                <MovieCard
                                    key={movie.movie_id}
                                    title={movie.title}
                                    similarity={movie.similarity}
                                    rank={index + 1}
                                    posterUrl={movie.poster_url}
                                    releaseYear={movie.release_year}
                                    voteAverage={movie.vote_average} 
                                    onClick={() => fetchRecommendations(movie.title)}
                                />
                            ))}
                        </div>
                    </section>
                )}

                {/* ── EMPTY STATE (before any search) ── */}
                {recommendations.length === 0 && !isLoading && !error && (
                    <div className="empty-state">
                        <div className="empty-icon">🍿</div>
                        <p>Search for any movie to get started!</p>
                        <div className="popular-searches">
                            <p>Popular searches:</p>
                            {['The Dark Knight', 'Inception', 'Avengers', 'Toy Story', 'The Godfather'].map(title => (
                                <button
                                    key={title}
                                    className="popular-btn"
                                    onClick={() => fetchRecommendations(title)}
                                >
                                    {title}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

            </main>

            {/* ── FOOTER ── */}
            <footer className="footer">
                <p>Powered by TMDB data · Content-based filtering · Django + React</p>
            </footer>
        </div>
    );
}

export default App;