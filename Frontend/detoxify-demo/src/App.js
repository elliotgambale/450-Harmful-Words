import React, { useState } from 'react';

export default function App() {
  const [url, setUrl]         = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult]   = useState(null);
  const [error, setError]     = useState('');

  const submit = async e => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setError('');

    // 1) Normalize: prepend https:// if missing
    const fetchUrl = url.match(/^https?:\/\//i)
      ? url
      : `https://${url}`;

    try {
      const res = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: fetchUrl }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Unknown error');
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: '2rem auto', fontFamily: 'sans-serif' }}>
      <h1>Website Toxicity Checker</h1>
      <form onSubmit={submit}>
        <input
          type="text"
          placeholder="example.com or https://example.com"
          value={url}
          onChange={e => setUrl(e.target.value)}
          required
          style={{ width: '100%', padding: 8 }}
        />
        <button type="submit" disabled={loading} style={{ marginTop: 8 }}>
          {loading ? 'Checking…' : 'Check Toxicity'}
        </button>
      </form>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {result && (
        <div style={{ marginTop: '1.5rem' }}>
          <h2>
            {result.is_toxic
              ? '⚠️ Harmful content detected!'
              : '✅ No harmful content found'}
          </h2>
          <p>
            Score: {result.toxic_score.toFixed(3)} (threshold {result.threshold})
          </p>
        </div>
      )}
    </div>
  );
}
