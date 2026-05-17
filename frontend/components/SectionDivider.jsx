import React from 'react';

export default function SectionDivider({ isDarkMode, showFlourish = true }) {
  const lightColor = '#d9b895'; // slightly warm pale brown for light mode
  const darkColor = '#b87918';

  const lineColor = isDarkMode ? darkColor : lightColor;

  return (
    <div className="relative w-full overflow-visible py-2">
      {/* Solid single-pixel line (no fading) */}
      <div style={{ background: lineColor }} className="h-px w-full"></div>

      {/* optional flourish (disabled for inventory when requested) */}
      {showFlourish && (
        <div className="absolute right-4 -top-3 pointer-events-none">
          <svg viewBox="0 0 220 40" className="w-36 h-8" aria-hidden="true">
            <defs>
              <linearGradient id="section-flourish-light" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#f7dfb8" />
                <stop offset="50%" stopColor="#f0c97a" />
                <stop offset="100%" stopColor="#d99d3f" />
              </linearGradient>
              <linearGradient id="section-flourish-dark" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#ffd87a" />
                <stop offset="50%" stopColor="#e2a83a" />
                <stop offset="100%" stopColor="#b87918" />
              </linearGradient>
            </defs>

            <path d="M6 18 C40 10, 100 6, 170 12" fill="none" stroke={isDarkMode ? 'url(#section-flourish-dark)' : 'url(#section-flourish-light)'} strokeWidth="2.6" strokeLinecap="round" />
            <path d="M142 10 C150 8, 158 6, 170 12 C176 16, 184 18, 196 16" fill="none" stroke={isDarkMode ? 'url(#section-flourish-dark)' : 'url(#section-flourish-light)'} strokeWidth="3" strokeLinecap="round" />
          </svg>
        </div>
      )}
    </div>
  );
}
