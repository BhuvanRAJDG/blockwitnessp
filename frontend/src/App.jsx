import React from 'react'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import CreateReport from './pages/CreateReport'
import Explorer from './pages/Explorer'
import Verify from './pages/Verify'

export default function App(){
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50">
        <nav className="p-4 bg-white shadow-sm flex gap-6">
          <Link to="/" className="font-bold text-xl">BlockWitness</Link>
          <Link to="/create">Create Report</Link>
          <Link to="/explorer">Explorer</Link>
          <Link to="/verify">Verify</Link>
        </nav>
        <main className="p-6 max-w-5xl mx-auto">
          <Routes>
            <Route path="/" element={<CreateReport/>} />
            <Route path="/create" element={<CreateReport/>} />
            <Route path="/explorer" element={<Explorer/>} />
            <Route path="/verify" element={<Verify/>} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
