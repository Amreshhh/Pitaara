'use client';

import React, { useState } from 'react';
import { Home, Activity, BarChart2 } from 'lucide-react';

export default function BottomNav() {
  const [activeTab, setActiveTab] = useState('home');

  const handleScroll = (sectionId) => {
    setActiveTab(sectionId);
    
    // Scroll to section if it exists
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t pb-safe pt-2 px-4 flex justify-around items-center sm:hidden z-50 dark:bg-stone-900 dark:border-stone-700">
      {/* Home Button */}
      <button 
        onClick={() => handleScroll('home')}
        className={`flex flex-col items-center p-2 transition-colors duration-200 ${
          activeTab === 'home' 
            ? 'text-amber-500' 
            : 'text-stone-400 hover:text-stone-600 dark:hover:text-stone-300'
        }`}
      >
        <Home size={22} strokeWidth={1.5} />
        <span className="text-[10px] mt-1 font-medium">Home</span>
      </button>

      {/* Calculator Button */}
      <button 
        onClick={() => handleScroll('input-section')}
        className={`flex flex-col items-center p-2 transition-colors duration-200 ${
          activeTab === 'input-section' 
            ? 'text-amber-500' 
            : 'text-stone-400 hover:text-stone-600 dark:hover:text-stone-300'
        }`}
      >
        <Activity size={22} strokeWidth={1.5} />
        <span className="text-[10px] mt-1 font-medium">Calculate</span>
      </button>

      {/* Rates/Results Button */}
      <button 
        onClick={() => handleScroll('results')}
        className={`flex flex-col items-center p-2 transition-colors duration-200 ${
          activeTab === 'results' 
            ? 'text-amber-500' 
            : 'text-stone-400 hover:text-stone-600 dark:hover:text-stone-300'
        }`}
      >
        <BarChart2 size={22} strokeWidth={1.5} />
        <span className="text-[10px] mt-1 font-medium">Results</span>
      </button>
    </nav>
  );
}
