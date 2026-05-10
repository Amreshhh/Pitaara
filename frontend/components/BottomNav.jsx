'use client';

import React, { useEffect, useState } from 'react';
import { Home, Activity, BarChart2 } from 'lucide-react';

export default function BottomNav() {
  const [activeTab, setActiveTab] = useState('home');

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

  useEffect(() => {
    if (typeof window === 'undefined') return undefined;

    const updateActiveTab = () => {
      const estimator = document.querySelector('#estimator');
      const ratesPanel = document.querySelector('.hero-rates-panel');
      const scrollY = window.scrollY + window.innerHeight * 0.35;

      if (ratesPanel && scrollY >= ratesPanel.offsetTop - 80) {
        setActiveTab('rates');
        return;
      }

      if (estimator && scrollY >= estimator.offsetTop - 80) {
        setActiveTab('calculator');
        return;
      }

      setActiveTab('home');
    };

    updateActiveTab();
    window.addEventListener('scroll', updateActiveTab, { passive: true });
    window.addEventListener('resize', updateActiveTab);

    return () => {
      window.removeEventListener('scroll', updateActiveTab);
      window.removeEventListener('resize', updateActiveTab);
    };
  }, []);

  const navButtonClass = (isActive) =>
    `flex flex-col items-center p-2 transition-colors ${isActive ? 'text-orange-500' : 'text-stone-400 dark:text-stone-500'}`;

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t pb-safe pt-2 px-6 flex justify-between items-center sm:hidden z-50 dark:bg-stone-900 dark:border-stone-700">
      <button type="button" onClick={() => scrollToSection('#top')} className={navButtonClass(activeTab === 'home')}>
        <Home size={22} />
        <span className="text-[10px] mt-1 font-medium">Home</span>
      </button>

      <button type="button" onClick={() => scrollToSection('#estimator')} className={navButtonClass(activeTab === 'calculator')}>
        <Activity size={22} />
        <span className="text-[10px] mt-1 font-medium">Calculator</span>
      </button>

      <button type="button" onClick={() => scrollToSection('rates')} className={navButtonClass(activeTab === 'rates')}>
        <BarChart2 size={22} />
        <span className="text-[10px] mt-1 font-medium">Rates</span>
      </button>
    </nav>
  );
}
