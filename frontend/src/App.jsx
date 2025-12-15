import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Link, useLocation, Navigate } from "react-router-dom";
import CreateReport from "./pages/CreateReport";
import Explorer from "./pages/Explorer";
import Verify from "./pages/Verify";
import Search from "./pages/Search";
import Timeline from "./pages/Timeline";
import Login from "./pages/Login";
import Home from "./pages/Home";
import Footer from "./components/Footer";
import { getCurrentUser, logout } from "./api";

function NavLink({ to, children, icon }) {
  const location = useLocation();
  const isActive = location.pathname === to;

  return (
    <Link
      to={to}
      className={`
        relative px-4 py-2.5 rounded-xl font-semibold text-sm
        transition-all duration-300 flex items-center gap-2
        group overflow-hidden
        ${isActive
          ? 'text-white bg-gradient-primary shadow-button scale-105'
          : 'text-dark-300 hover:text-neon-cyan hover:bg-dark-800/50 hover:scale-105 hover:shadow-glow'
        }
        active:scale-95
      `}
    >
      {!isActive && (
        <span className="absolute inset-0 bg-gradient-to-r from-primary-500/0 via-neon-cyan/20 to-secondary-500/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000"></span>
      )}
      {icon && <span className="relative z-10 transition-transform group-hover:scale-110 group-hover:rotate-6">{icon}</span>}
      <span className="relative z-10">{children}</span>
      {isActive && (
        <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-neon-cyan/60 via-neon-cyan to-neon-cyan/60 rounded-full shadow-glow"></span>
      )}
    </Link>
  );
}

function AppContent({ user, setUser }) {
  const handleLogout = async () => {
    try {
      await logout();
      setUser(null);
    } catch (err) {
      console.error("Logout error:", err);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-mesh bg-dark-950 animate-fade-in flex flex-col">
      <nav className="sticky top-0 z-50 bg-dark-900/80 backdrop-blur-xl border-b border-primary-800/20 shadow-lg">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center gap-3 group cursor-pointer">
              <div className="w-11 h-11 bg-gradient-to-br from-primary-500 via-secondary-500 to-accent-500 rounded-xl flex items-center justify-center shadow-glow transition-all duration-500 group-hover:scale-110 group-hover:rotate-6 group-hover:shadow-glow-lg">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-extrabold gradient-text">
                  BlockWitness
                </h1>
                <p className="text-xs text-dark-400 font-medium">Tamper-Proof Evidence Recorder</p>
              </div>
            </Link>

            <div className="flex items-center gap-2">
              {user ? (
                <>
                  <NavLink to="/create" icon={
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                  }>
                    Record
                  </NavLink>
                  <NavLink to="/explorer" icon={
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                    </svg>
                  }>
                    Explorer
                  </NavLink>
                  <NavLink to="/verify" icon={
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  }>
                    Verify
                  </NavLink>
                  <NavLink to="/search" icon={
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  }>
                    Search
                  </NavLink>
                  <NavLink to="/timeline" icon={
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  }>
                    Timeline
                  </NavLink>
                  <div className="ml-4 flex items-center gap-3">
                    <span className="text-dark-300 text-sm">
                      {user.username || user.email}
                    </span>
                    <button
                      onClick={handleLogout}
                      className="px-4 py-2 text-sm font-medium text-dark-300 hover:text-white bg-dark-800/50 hover:bg-dark-700 rounded-xl transition-all duration-300"
                    >
                      Logout
                    </button>
                  </div>
                </>
              ) : (
                <NavLink to="/login" icon={
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                  </svg>
                }>
                  Login
                </NavLink>
              )}
            </div>
          </div>
        </div>
      </nav>

      <main className="flex-grow max-w-7xl mx-auto w-full px-6 py-8 animate-fade-in relative z-0">
        <Routes>
          <Route path="/login" element={
            user ? <Navigate to="/" /> : <Login onLogin={setUser} />
          } />
          <Route path="/create" element={
            user ? <CreateReport /> : <Navigate to="/login" />
          } />
          {/* Public Home Page */}
          <Route path="/" element={<Home />} />

          <Route path="/explorer" element={
            user ? <Explorer /> : <Navigate to="/login" />
          } />
          <Route path="/verify" element={
            user ? <Verify /> : <Navigate to="/login" />
          } />
          <Route path="/search" element={
            user ? <Search /> : <Navigate to="/login" />
          } />
          <Route path="/timeline" element={
            user ? <Timeline /> : <Navigate to="/login" />
          } />
        </Routes>
      </main>

      <Footer />
    </div>
  );
}

export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const result = await getCurrentUser();
        if (result.authenticated) {
          setUser(result.user);
        }
      } catch (err) {
        console.error("Auth check failed:", err);
      }
      setLoading(false);
    };
    checkAuth();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-dark-950 flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <AppContent user={user} setUser={setUser} />
    </BrowserRouter>
  );
}
