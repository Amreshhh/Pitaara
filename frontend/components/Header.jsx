'use client';

import { Sun, Moon } from 'lucide-react';
import { getThemeStyles } from '@/lib/utils';

export const Header = ({ isDarkMode, currentRate = 14620, onToggleTheme }) => {
  const styles = getThemeStyles(isDarkMode);
  const rateValue = currentRate || 15000 ;

  return (
    <header
      className={`sticky top-0 z-40 backdrop-blur-xl border-b transition-colors duration-500 ${styles.headerBg} ${styles.borderColor}`}
    >
      <div className="relative">
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
                ₹{rateValue.toLocaleString()}{' '}
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

        <div className="pointer-events-none absolute bottom-0 left-6 right-6 md:left-8 md:right-8 h-px overflow-visible">
          <div
            className={`h-0.75 w-full ${isDarkMode ? 'shadow-[0_0_70px_rgba(251,146,60,1)] bg-linear-to-r from-transparent via-orange-200 to-transparent' : 'shadow-[0_0_70px_rgba(34,211,238,1)] bg-linear-to-r from-transparent via-cyan-300 to-transparent'}`}
          ></div>
        </div>
      </div>
    </header>
  );
};
