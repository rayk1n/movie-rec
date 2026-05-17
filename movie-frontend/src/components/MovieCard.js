import React, { useState } from 'react';

function MovieCard({ title, similarity, rank, posterUrl, releaseYear, voteAverage, onClick }) {
    const [imgError, setImgError] = useState(false);

    const similarityPercent = Math.round(similarity * 100);

    const badgeColor =
        similarityPercent > 30 ? '#22c55e' :
        similarityPercent > 15 ? '#f59e0b' :
        '#94a3b8';

    return (
        <div className="movie-card" onClick={onClick} title={`Get recommendations for "${title}"`}>

            <div className="card-poster-wrapper">
                {!imgError && posterUrl ? (
                    <img
                        src={posterUrl}
                        alt={`${title} poster`}
                        className="card-poster"
                        onError={() => setImgError(true)}
                        loading="lazy"
                    />
                ) : (
                    <div className="card-poster-fallback">
                        <span className="fallback-icon">🎬</span>
                        <span className="fallback-text">{title}</span>
                    </div>
                )}
                <div className="card-rank-badge">#{rank}</div>
                <div
                    className="card-similarity-badge"
                    style={{
                        backgroundColor: badgeColor + '33',
                        color: badgeColor,
                        borderColor: badgeColor + '66'
                    }}
                >
                    {similarityPercent}% match
                </div>
            </div>

            <div className="card-info">
                <h3 className="card-title">{title}</h3>
                <div className="card-meta">
                    {releaseYear && (
                        <span className="card-year">({releaseYear})</span>
                    )}
                    {voteAverage > 0 && (
                        <span className="card-rating">⭐ {voteAverage.toFixed(1)}</span>
                    )}
                </div>
            </div>

        </div>
    );
}

export default MovieCard;