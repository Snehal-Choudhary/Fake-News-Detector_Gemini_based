// frontend/src/App.js
import React, { useState } from 'react';
import './App.css';

function App() {
    const [input, setInput] = useState('');
    const [result, setResult] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');
        setResult(null);

        const isUrl = input.startsWith('http://') || input.startsWith('https://');
        const payload = isUrl ? { url: input } : { text: input };

        try {
            const response = await fetch('http://localhost:8000/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'An error occurred');
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
        if (verdict.includes('Real')) return 'real';
        if (verdict.includes('Fake')) return 'fake';
        return 'unverified';
    };

    return (
        <div className="App">
            <header className="App-header">
                <h1>Fake News Detector</h1>
                <p>Enter a news claim or article URL to analyze its credibility.</p>
            </header>
            <main>
                <form onSubmit={handleSubmit}>
                    <textarea
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Paste your text or URL here..."
                        rows="5"
                    />
                    <button type="submit" disabled={isLoading}>
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
                        <div className="sources">
                            <h3>Supporting Sources</h3>
                            <ul>
                                {result.sources.map((source, index) => (
                                    <li key={index}>
                                        <a href={source.url || source.link} target="_blank" rel="noopener noreferrer">
                                            {source.claim || source.title}
                                        </a>
                                        <p>{source.snippet || `Rating: ${source.rating}`}</p>
                                        <small>Source: {source.source}</small>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}

export default App;
