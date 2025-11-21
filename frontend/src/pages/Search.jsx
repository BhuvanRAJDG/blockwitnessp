// frontend/src/pages/Search.jsx
import React, { useState } from "react";
import { searchReports } from "../api";

export default function Search() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  async function handleSearch() {
    if (!query) return setResults([]);
    setLoading(true);
    try {
      console.log("[Search] calling API for:", query);
      const res = await searchReports(query);
      console.log("[Search] API returned:", res);
      setResults(res || []);
    } catch (err) {
      console.error("[Search] API error:", err);
      alert("Search failed: " + err.message);
      setResults([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Search Reports</h1>
      <div className="flex gap-3 mb-6">
        <input
          className="flex-1 px-4 py-2 border rounded"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by title, uploader, tx_id, block..."
        />
        <button onClick={handleSearch} className="px-4 py-2 bg-blue-600 text-white rounded">
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      <div>
        <p className="text-sm text-gray-500 mb-2">Open browser console (F12) to see request/response logs.</p>
        {results.length === 0 && query && !loading && <p className="text-gray-500">No results found.</p>}
        <ul className="space-y-4">
          {results.map((r) => (
            <li key={r.tx_id} className="p-4 bg-white rounded shadow">
              <h2 className="text-xl font-semibold">{r.title}</h2>
              <p className="text-gray-600">{r.description}</p>
              <p className="mt-2 text-sm"><b>Uploader:</b> {r.uploader}</p>
              <p className="text-sm"><b>Block:</b> {r.block_index}</p>
              <p className="text-sm"><b>TX ID:</b> {r.tx_id}</p>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
