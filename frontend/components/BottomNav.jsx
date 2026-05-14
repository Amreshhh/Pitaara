'use client';

import React, { useEffect, useState } from 'react';
import { Home, Activity, BarChart2, LayoutGrid } from 'lucide-react';

export default function BottomNav() {
  const [activeTab, setActiveTab] = useState('home');

  const handleNavClick = (tab, selector) => {
    setActiveTab(tab);
    scrollToSection(selector);
  };

  const scrollToSection = (selector) => {
    if (typeof window === 'undefined') return;

    if (selector === 'rates') {
      const ratesPanel = document.querySelector('.hero-rates-panel');
      ratesPanel?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }

    if (selector === 'inventory') {
      const inventorySection = document.querySelector('.heatmap-section');
      inventorySection?.scrollIntoView({ behavior: 'smooth', block: 'start' });
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
      const inventorySection = document.querySelector('.heatmap-section');
      const scrollY = window.scrollY + window.innerHeight * 0.35;

      if (inventorySection && scrollY >= inventorySection.offsetTop - 80) {
        setActiveTab('inventory');
        return;
      }

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
    `group flex flex-col items-center justify-center gap-1 min-w-0 rounded-2xl px-3 py-2 transition-all duration-200 ease-out transform-gpu ${
      isActive
        ? 'text-orange-500 bg-orange-500/10 dark:bg-orange-400/15 shadow-[0_10px_25px_rgba(249,115,22,0.14)] scale-[1.03]'
        : 'text-stone-400 dark:text-stone-500 hover:text-orange-400 hover:bg-stone-100/80 dark:hover:bg-stone-800/60'
    }`;

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white/90 backdrop-blur-xl border-t pb-safe pt-2 px-4 flex justify-between items-center sm:hidden z-50 dark:bg-stone-900/90 dark:border-stone-700">
      <button type="button" onClick={() => handleNavClick('home', '#top')} className={navButtonClass(activeTab === 'home')}>
        <Home size={22} />
        <span className={`text-[10px] font-medium transition-colors ${activeTab === 'home' ? 'text-orange-500' : ''}`}>Home</span>
      </button>

      <button type="button" onClick={() => handleNavClick('calculator', '#estimator')} className={navButtonClass(activeTab === 'calculator')}>
        <Activity size={22} />
        <span className={`text-[10px] font-medium transition-colors ${activeTab === 'calculator' ? 'text-orange-500' : ''}`}>Calculator</span>
      </button>

      <button type="button" onClick={() => handleNavClick('rates', 'rates')} className={navButtonClass(activeTab === 'rates')}>
        <BarChart2 size={22} />
        <span className={`text-[10px] font-medium transition-colors ${activeTab === 'rates' ? 'text-orange-500' : ''}`}>Rates</span>
      </button>

      <button type="button" onClick={() => handleNavClick('inventory', 'inventory')} className={navButtonClass(activeTab === 'inventory')}>
        <LayoutGrid size={22} />
        <span className={`text-[10px] font-medium transition-colors ${activeTab === 'inventory' ? 'text-orange-500' : ''}`}>Inventory</span>
      </button>
    </nav>
  );
}
