import React from 'react';
import { Link } from 'react-router-dom';

const FeatureCard = ({ title, description, icon, delay }) => (
    <div className={`
    group relative p-8 rounded-2xl bg-dark-900/50 border border-dark-800 
    hover:border-primary-500/30 hover:bg-dark-800/80 transition-all duration-500
    hover:shadow-glow hover:-translate-y-2
    animate-fade-in-up [animation-delay:${delay}ms]
  `}>
        <div className="absolute inset-0 bg-gradient-to-br from-primary-500/5 via-transparent to-secondary-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        <div className="w-14 h-14 mb-6 rounded-xl bg-gradient-to-br from-dark-800 to-dark-900 border border-dark-700 flex items-center justify-center group-hover:scale-110 group-hover:rotate-6 transition-transform duration-500">
            {icon}
        </div>
        <h3 className="text-xl font-bold mb-3 text-white group-hover:text-primary-400 transition-colors">{title}</h3>
        <p className="text-dark-400 leading-relaxed group-hover:text-dark-300 transition-colors">{description}</p>
    </div>
);

const StatCard = ({ value, label, color }) => (
    <div className="text-center p-6 bg-dark-900/40 rounded-2xl backdrop-blur-sm border border-white/5 hover:border-white/10 transition-colors">
        <div className={`text-4xl font-extrabold mb-2 bg-gradient-to-r ${color} bg-clip-text text-transparent`}>
            {value}
        </div>
        <div className="text-dark-400 text-sm font-medium tracking-wider uppercase">{label}</div>
    </div>
);

export default function Home() {
    return (
        <div className="flex flex-col gap-24 py-12">

            {/* Hero Section */}
            <section className="relative min-h-[80vh] flex flex-col items-center justify-center text-center px-4">
                {/* Background Gradients */}
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary-500/10 rounded-full blur-[100px] animate-pulse-slow"></div>
                <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-secondary-500/10 rounded-full blur-[120px] pointer-events-none"></div>

                <div className="relative z-10 max-w-4xl mx-auto space-y-8 animate-fade-in-up">
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-dark-800/50 border border-primary-500/20 text-primary-400 text-sm font-medium mb-4 animate-slide-up">
                        <span className="w-2 h-2 rounded-full bg-primary-500 animate-pulse"></span>
                        <span>Blockchain Evidence Management System v1.0</span>
                    </div>

                    <h1 className="text-6xl md:text-8xl font-black tracking-tight leading-tight">
                        Truth is <br />
                        <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary-400 via-secondary-400 to-accent-400 animate-gradient-x">
                            Immutable
                        </span>
                    </h1>

                    <p className="text-xl md:text-2xl text-dark-300 max-w-2xl mx-auto leading-relaxed">
                        Secure your digital evidence with military-grade encryption and blockchain verification.
                        Create unalterable records that stand the test of time.
                    </p>

                    <div className="flex flex-col sm:flex-row gap-4 justify-center pt-8">
                        <Link to="/create" className="group relative px-8 py-4 bg-gradient-to-r from-primary-600 to-secondary-600 rounded-xl font-bold text-white shadow-button hover:shadow-glow-lg hover:scale-105 transition-all duration-300 overflow-hidden">
                            <span className="relative z-10 flex items-center gap-2">
                                Start Recording
                                <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
                            </span>
                            <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-500 skew-y-12"></div>
                        </Link>

                        <Link to="/explorer" className="px-8 py-4 bg-dark-800/50 border border-dark-700 text-white rounded-xl font-bold hover:bg-dark-800 hover:border-primary-500/30 hover:scale-105 transition-all duration-300">
                            Explore Chain
                        </Link>
                    </div>
                </div>
            </section>

            {/* Features Grid */}
            <section className="relative px-6">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl md:text-5xl font-bold mb-4">Why BlockWitness?</h2>
                        <p className="text-dark-400 max-w-2xl mx-auto">Built on advanced cryptographic primitives to ensure your data remains verifiable forever.</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        <FeatureCard
                            delay={0}
                            title="Cryptographic Proof"
                            description="Every file hash is signed and anchored in a merkle tree, providing mathematical proof of existence and integrity."
                            icon={<svg className="w-7 h-7 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>}
                        />
                        <FeatureCard
                            delay={100}
                            title="Instant Verification"
                            description="Verify any file against the blockchain in milliseconds. Drag, drop, and get immediate authenticity confirmation."
                            icon={<svg className="w-7 h-7 text-secondary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
                        />
                        <FeatureCard
                            delay={200}
                            title="Decentralized Design"
                            description="No single point of failure. Your records are distributed across a resilient network of witness nodes."
                            icon={<svg className="w-7 h-7 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>}
                        />
                    </div>
                </div>
            </section>

            {/* Stats Section */}
            <section className="py-20 bg-dark-900/30 border-y border-white/5 backdrop-blur-sm">
                <div className="max-w-7xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-8">
                    <StatCard value="100%" label="Uptime" color="from-green-400 to-emerald-600" />
                    <StatCard value="256" label="Bit Encryption" color="from-blue-400 to-indigo-600" />
                    <StatCard value="0.0s" label="Tamper Risk" color="from-purple-400 to-pink-600" />
                    <StatCard value="∞" label="Retention" color="from-orange-400 to-red-600" />
                </div>
            </section>

            {/* CTA Section */}
            <section className="text-center py-24 px-6 relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-radial from-primary-900/20 to-transparent opacity-50"></div>
                <div className="relative z-10 max-w-3xl mx-auto">
                    <h2 className="text-4xl font-bold mb-6">Ready to secure your data?</h2>
                    <p className="text-dark-300 mb-10 text-lg">Join thousands of users who trust BlockWitness for their evidence management needs.</p>
                    <Link to="/create" className="inline-block px-10 py-4 bg-white text-dark-950 rounded-xl font-bold hover:bg-gray-100 hover:scale-105 transition-all duration-300 shadow-xl shadow-white/10">
                        Get Started Now
                    </Link>
                </div>
            </section>

        </div>
    );
}
