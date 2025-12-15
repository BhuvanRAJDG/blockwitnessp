import React from 'react';
import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="relative bg-dark-900 border-t border-dark-800 overflow-hidden mt-auto">
      {/* Abstract Background Elements */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary-500/5 rounded-full blur-3xl pointer-events-none"></div>
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-secondary-500/5 rounded-full blur-3xl pointer-events-none"></div>

      <div className="max-w-7xl mx-auto px-6 py-12 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 text-center md:text-left">
          
          {/* Brand Section */}
          <div className="col-span-1 md:col-span-1">
            <div className="flex items-center justify-center md:justify-start gap-2 mb-4 group">
              <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center shadow-lg group-hover:rotate-12 transition-transform duration-300">
                 <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                BlockWitness
              </span>
            </div>
            <p className="text-dark-400 text-sm leading-relaxed mb-6">
              Securing truth through immutable blockchain technology. Verify evidence with mathematical certainty.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-white font-semibold mb-4 text-base">Platform</h3>
            <ul className="space-y-3 text-sm">
              <li><Link to="/explorer" className="text-dark-400 hover:text-primary-400 transition-colors">Block Explorer</Link></li>
              <li><Link to="/verify" className="text-dark-400 hover:text-primary-400 transition-colors">Verify Artifacts</Link></li>
              <li><Link to="/timeline" className="text-dark-400 hover:text-primary-400 transition-colors">Live Timeline</Link></li>
              <li><Link to="/search" className="text-dark-400 hover:text-primary-400 transition-colors">Global Search</Link></li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h3 className="text-white font-semibold mb-4 text-base">Resources</h3>
            <ul className="space-y-3 text-sm">
              <li><a href="#" className="text-dark-400 hover:text-primary-400 transition-colors">Documentation</a></li>
              <li><a href="#" className="text-dark-400 hover:text-primary-400 transition-colors">API Reference</a></li>
              <li><a href="#" className="text-dark-400 hover:text-primary-400 transition-colors">Privacy Policy</a></li>
              <li><a href="#" className="text-dark-400 hover:text-primary-400 transition-colors">Terms of Service</a></li>
            </ul>
          </div>

          {/* Newsletter / Connect */}
          <div>
            <h3 className="text-white font-semibold mb-4 text-base">Stay Verified</h3>
            <p className="text-dark-400 text-sm mb-4">Join the network of truth keepers.</p>
            <div className="flex gap-2 justify-center md:justify-start">
              {[1, 2, 3].map((i) => (
                <div key={i} className="w-8 h-8 rounded-full bg-dark-800 flex items-center justify-center hover:bg-primary-500 hover:text-white transition-all duration-300 cursor-pointer text-dark-400">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="border-t border-dark-800 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center text-sm text-dark-500">
          <p>&copy; 2025 BlockWitness Inc. All rights reserved.</p>
          <div className="flex gap-6 mt-4 md:mt-0">
            <span>Powered by PyChain</span>
            <span className="w-1.5 h-1.5 rounded-full bg-success-500 my-auto animate-pulse"></span>
            <span>System Operational</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
