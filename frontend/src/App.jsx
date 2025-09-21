import React, { useState } from 'react';
import './App.css';

function App() {
    const [input, setInput] = useState('');
    const [result, setResult] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    // Use Vite's `import.meta.env` to access environment variables.
    // This allows the app to use the live URL on Netlify and a fallback for local testing.
    // The variable on Netlify MUST be named VITE_API_URL.
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/analyze';

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');
        setResult(null);

        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                // The backend is smart enough to detect URLs, so we always send a 'text' payload.
                body: JSON.stringify({ text: input }),
            });

            if (!response.ok) {
                // Try to get a detailed error message from the backend, otherwise show a generic one.
                const errData = await response.json().catch(() => ({ detail: 'An unknown error occurred.' }));
                throw new Error(errData.detail || 'An error occurred during analysis.');
            }

            const data = await response.json();
            setResult(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    const getVerdictClass = (verdict) => {
        if (!verdict) return 'unverified';
        if (verdict.includes('Real')) return 'real';
        if (verdict.includes('Fake')) return 'fake';
        return 'unverified';
    };

    return (
        <div className="App">
            <header className="App-header">
                <h1>FactScope</h1>
                <p>Enter a news claim or article URL to analyze its credibility.</p>
            </header>
            <main>
                <form onSubmit={handleSubmit}>
                    <textarea
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Paste your text or URL here..."
                        rows="5"
                        aria-label="News claim input"
                    />
                    <button type="submit" disabled={isLoading || !input}>
                        {isLoading ? 'Analyzing...' : 'Analyze'}
                    </button>
                </form>

                {error && <div className="error-message">{error}</div>}

                {result && (
                    <div className="results">
                        <h2>Analysis Result</h2>
                        <div className={`verdict ${getVerdictClass(result.verdict)}`}>
                            <strong>Verdict:</strong> {result.verdict}
                        </div>
                        <div className="score">
                            <strong>Confidence Score:</strong> {Math.round(result.confidence_score * 100)}%
                        </div>
                        <div className="explanation">
                            <h3>Explanation</h3>
                            <p>{result.explanation}</p>
                        </div>
                        
                        {/* Defensive check to prevent crash if supporting_sources is missing or not an array */}
                        {Array.isArray(result.supporting_sources) && result.supporting_sources.length > 0 && (
                            <div className="sources">
                                <h3>Supporting Sources</h3>
                                <ul>
                                    {result.supporting_sources.map((source) => (
                                        <li key={source.link || source.title}>
                                            <a href={source.link} target="_blank" rel="noopener noreferrer">
                                                {source.title}
                                            </a>
                                            <p>{source.snippet}</p>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                )}
            </main>
        </div>
    );
}

export default App;

