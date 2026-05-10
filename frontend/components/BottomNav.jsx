'use client';

import React from 'react';
import { Home, Activity, BarChart2 } from 'lucide-react';

export default function BottomNav() {
  const scrollToSection = (selector) => {
    if (typeof window === 'undefined') return;

    if (selector === 'rates') {
      const ratesPanel = document.querySelector('.hero-rates-panel');
      ratesPanel?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }

    const target = document.querySelector(selector);
    target?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t pb-safe pt-2 px-6 flex justify-between items-center sm:hidden z-50 dark:bg-stone-900 dark:border-stone-700">
      <button type="button" onClick={() => scrollToSection('#top')} className="flex flex-col items-center text-amber-500 p-2">
        <Home size={22} />
        <span className="text-[10px] mt-1 font-medium">Home</span>
      </button>

      <button type="button" onClick={() => scrollToSection('#estimator')} className="flex flex-col items-center text-stone-400 p-2">
        <Activity size={22} />
        <span className="text-[10px] mt-1 font-medium">Calculator</span>
      </button>

      <button type="button" onClick={() => scrollToSection('rates')} className="flex flex-col items-center text-stone-400 p-2">
        <BarChart2 size={22} />
        <span className="text-[10px] mt-1 font-medium">Rates</span>
      </button>
    </nav>
  );
}
