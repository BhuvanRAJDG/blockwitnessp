// frontend/src/App.jsx
import React from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import CreateReport from "./pages/CreateReport";
import Explorer from "./pages/Explorer";
import Verify from "./pages/Verify";
import Search from "./pages/Search";

export default function App(){
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-100">
        <nav className="bg-white px-6 py-3 shadow">
          <div className="max-w-6xl mx-auto flex items-center justify-between">
            <div className="font-bold text-lg">BlockWitness</div>
            <div className="flex gap-4 items-center">
              <Link to="/" className="text-sm text-indigo-600">Create</Link>
              <Link to="/explorer" className="text-sm text-indigo-600">Explorer</Link>
              <Link to="/verify" className="text-sm text-indigo-600">Verify</Link>
              <Link to="/search" className="text-sm text-indigo-600">Search</Link>
            </div>
          </div>
        </nav>

        <main className="max-w-6xl mx-auto py-8">
          <Routes>
            <Route path="/" element={<CreateReport />} />
            <Route path="/explorer" element={<Explorer />} />
            <Route path="/verify" element={<Verify />} />
            <Route path="/search" element={<Search />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
