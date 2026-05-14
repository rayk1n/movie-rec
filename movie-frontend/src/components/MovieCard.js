import React from 'react';

/**
 * MovieCard Component
 * 
 * Displays a single recommended movie.
 * 
 * Props:
 *   title (string)      — Movie title
 *   similarity (number) — Similarity score (0 to 1)
 *   rank (number)       — Position in the recommendations list
 *   onClick()           — Called when this card is clicked (to get its recommendations)
 */
function MovieCard({ title, similarity, rank, onClick }) {
    // Convert similarity score to a percentage for display
    const similarityPercent = Math.round(similarity * 100);

    // Color the similarity badge based on how similar it is
    const badgeColor =
        similarityPercent > 30 ? '#22c55e' :  // green  = very similar
        similarityPercent > 15 ? '#f59e0b' :  // yellow = somewhat similar
        '#94a3b8';                             // gray   = less similar

    // Generate a colored background for the card based on the movie title
    // (Since we don't have movie posters, we use a deterministic color)
    const cardColors = [
        ['#1e3a5f', '#2d6a8f'],
        ['#2d1b69', '#4c2f8f'],
        ['#1a4731', '#2d7a50'],
        ['#5c1a1a', '#8f3333'],
        ['#3d2b1a', '#7a5533'],
    ];
    const colorSet = cardColors[rank % cardColors.length];

    return (
        <div
            className="movie-card"
            onClick={onClick}
            title={`Click to get recommendations for "${title}"`}
            style={{ background: `linear-gradient(135deg, ${colorSet[0]}, ${colorSet[1]})` }}
        >
            {/* Rank badge */}
            <div className="card-rank">#{rank}</div>

            {/* Movie title */}
            <div className="card-body">
                <div className="card-film-icon">🎬</div>
                <h3 className="card-title">{title}</h3>
            </div>

            {/* Similarity score badge */}
            <div className="card-footer">
                <span
                    className="similarity-badge"
                    style={{ backgroundColor: badgeColor + '33', color: badgeColor, border: `1px solid ${badgeColor}55` }}
                >
                    {similarityPercent}% match
                </span>
                <span className="click-hint">Get recs →</span>
            </div>
        </div>
    );
}

export default MovieCard;