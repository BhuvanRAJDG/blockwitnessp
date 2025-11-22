import React from 'react';

export default function Card({ 
  children, 
  className = '', 
  hover = false,
  glow = false,
  gradient = false,
  ...props 
}) {
  const baseStyles = 'bg-white rounded-2xl shadow-card transition-all duration-500 border border-dark-100/50 backdrop-blur-sm animate-fade-in-up';
  const hoverStyles = hover ? 'hover:shadow-card-hover hover:-translate-y-2 hover:border-primary-300/50 cursor-pointer card-interactive' : '';
  const glowStyles = glow ? 'shadow-glow hover:shadow-glow-lg animate-pulse-glow' : '';
  const gradientStyles = gradient ? 'bg-gradient-to-br from-white via-white to-primary-50/40 border-primary-200/30' : '';
  
  return (
    <div 
      className={`${baseStyles} ${hoverStyles} ${glowStyles} ${gradientStyles} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

export function GlassCard({ children, className = '', ...props }) {
  return (
    <div 
      className={`bg-white/80 backdrop-blur-xl rounded-2xl shadow-glass border border-white/30 transition-all duration-500 hover:bg-white/90 hover:shadow-card-hover animate-fade-in-up ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}
