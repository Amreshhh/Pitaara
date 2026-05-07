'use client';

import { Moon, Sun } from 'lucide-react';

export const ThemeToggle = ({ isDarkMode, onToggle }) => {
  return (
    <button
      onClick={onToggle}
      className={`fixed top-6 right-6 z-50 p-3 rounded-full shadow-lg backdrop-blur-md border transition-all hover:scale-105 active:scale-95 ${
        isDarkMode ? 'bg-stone-900/80 border-stone-800 text-amber-400' : 'bg-white/80 border-stone-200 text-stone-600'
      }`}
      aria-label="Toggle theme"
    >
      {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
    </button>
  );
};
