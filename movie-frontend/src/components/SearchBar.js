// src/components/SearchBar.js
import React, { useState, useEffect, useRef } from 'react';
import api from '../api';

/**
 * SearchBar Component
 * 
 * Props:
 *   onMovieSelect(title) — called when the user picks a movie
 *   isLoading — if true, the input is disabled (recommendations loading)
 */
function SearchBar({ onMovieSelect, isLoading }) {
    const [inputValue, setInputValue]     = useState('');    // What's typed in the box
    const [suggestions, setSuggestions]   = useState([]);    // Autocomplete dropdown list
    const [showDropdown, setShowDropdown] = useState(false); // Whether to show the dropdown
    const dropdownRef = useRef(null);  // Used to detect clicks outside the dropdown

    // ── Autocomplete: search as the user types ──
    useEffect(() => {
        // Don't search if the input is too short
        if (inputValue.trim().length < 2) {
            setSuggestions([]);
            setShowDropdown(false);
            return;
        }

        // "Debounce" — wait 300ms after the user stops typing before searching.
        // This prevents sending a request for every single keystroke.
        const timer = setTimeout(async () => {
            try {
                const response = await api.get(`/search/?q=${encodeURIComponent(inputValue)}`);
                setSuggestions(response.data.results || []);
                setShowDropdown(true);
            } catch (err) {
                console.error("Search error:", err);
            }
        }, 300);

        // Cleanup: cancel the timer if the user types again before 300ms
        return () => clearTimeout(timer);
    }, [inputValue]);  // This effect re-runs whenever inputValue changes

    // ── Close dropdown when user clicks outside it ──
    useEffect(() => {
        function handleClickOutside(event) {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setShowDropdown(false);
            }
        }
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    // ── When user picks a suggestion ──
    function handleSelect(item) {
        const title = typeof item === 'string' ? item : item.title;
        setInputValue(title);
        setShowDropdown(false);
        onMovieSelect(title);
    }

    // ── When user presses Enter ──
    function handleKeyDown(e) {
        if (e.key === 'Enter' && inputValue.trim()) {
            setShowDropdown(false);
            onMovieSelect(inputValue.trim());
        }
    }

    return (
        <div className="search-container" ref={dropdownRef}>
            <div className="search-input-wrapper">
                <span className="search-icon">🔍</span>
                <input
                    type="text"
                    className="search-input"
                    placeholder="Search for a movie... e.g. Inception"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                    disabled={isLoading}
                />
                {inputValue && (
                    <button
                        className="clear-btn"
                        onClick={() => { setInputValue(''); setSuggestions([]); }}
                    >
                        ✕
                    </button>
                )}
            </div>

            {/* Autocomplete Dropdown */}
            {showDropdown && suggestions.length > 0 && (
                <ul className="suggestions-dropdown">
                    {suggestions.map((item, index) => (
                        <li
                            key={index}
                            className="suggestion-item"
                            onClick={() => handleSelect(item)}
                        >
                            <span>🎬 {item.title}</span>
                            {item.release_year && (
                                <span className="suggestion-year"> ({item.release_year})</span>
                            )}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}

export default SearchBar;