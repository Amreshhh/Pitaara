'use client';

import React from 'react';
import { Home, Activity, BarChart2 } from 'lucide-react';

export default function BottomNav() {
  const scrollToId = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t pt-2 px-4 pb-[calc(env(safe-area-inset-bottom)+0.5rem)] flex justify-between items-center sm:hidden z-50 dark:bg-stone-900 dark:border-stone-700">
      <button type="button" onClick={() => scrollToId('top')} className="flex flex-col items-center text-amber-500 p-2 min-w-0">
        <Home size={22} />
        <span className="text-[10px] mt-1 font-medium">Home</span>
      </button>

      <button type="button" onClick={() => scrollToId('estimator')} className="flex flex-col items-center text-stone-400 p-2 min-w-0">
        <Activity size={22} />
        <span className="text-[10px] mt-1 font-medium">Calculator</span>
      </button>

      <button type="button" onClick={() => scrollToId('live-rates')} className="flex flex-col items-center text-stone-400 p-2 min-w-0">
        <BarChart2 size={22} />
        <span className="text-[10px] mt-1 font-medium">Rates</span>
      </button>
    </nav>
  );
}
