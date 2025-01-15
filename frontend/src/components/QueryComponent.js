import React, { useState } from "react";
import './styles/QueryComponent.css';

const QueryComponent = () => {
  const [inputText, setInputText] = useState("");
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(""); // Clear any previous errors
    setResults([]); // Clear previous results

    try {
      const response = await fetch("http://localhost:5000/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: inputText }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const data = await response.json();
      setResults(data.matches); // Update results from API response
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div>
      <h1>Query Pinecone</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Enter text to query"
          required
        />
        <button type="submit">Submit</button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <div>
        <h2>Results:</h2>
        {results.length > 0 ? (
          <ul>
            {results.map((result, index) => (
              <li key={index}>
                <strong>Score:</strong> {result.score}
                <br />
                <strong>Metadata:</strong> {JSON.stringify(result.metadata)}
              </li>
            ))}
          </ul>
        ) : (
          <p>No results yet.</p>
        )}
      </div>
    </div>
  );
};

export default QueryComponent;
