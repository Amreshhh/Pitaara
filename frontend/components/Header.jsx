'use client';

import { Sun, Moon } from 'lucide-react';
import { getThemeStyles } from '@/lib/utils';

export const Header = ({ isDarkMode, currentRate, onToggleTheme }) => {
  const styles = getThemeStyles(isDarkMode);

  return (
    <header
      className={`sticky top-0 z-40 backdrop-blur-xl border-b transition-colors duration-500 ${styles.headerBg} ${styles.borderColor}`}
    >
      <div className="max-w-7xl mx-auto px-6 py-4 flex flex-row items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-serif font-bold tracking-tight">OmRani</h1>
        </div>

        <div className="flex items-center gap-3 sm:gap-6">
          <div className="text-right hidden sm:block">
            <div className={`text-[10px] uppercase font-bold tracking-wider ${styles.textMuted}`}>
              Today&apos;s Rate (24K)
            </div>
            <div className="text-lg font-serif font-bold">
              ₹{currentRate.toLocaleString()}{' '}
              <span className={`text-xs font-sans font-normal ${styles.textMuted}`}>/g</span>
            </div>
          </div>
          {onToggleTheme && (
            <button
              onClick={onToggleTheme}
              className={`p-2 rounded-full transition-colors ${isDarkMode ? 'bg-stone-800 text-amber-400 hover:bg-stone-700' : 'bg-stone-100 text-stone-800 hover:bg-stone-200'}`}
              aria-label="Toggle theme"
            >
              {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
