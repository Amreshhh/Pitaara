'use client';

import React, { useEffect, useRef, useState } from 'react';
import { Home, Activity, BarChart2, LayoutGrid } from 'lucide-react';

export default function BottomNav() {
  const [activeTab, setActiveTab] = useState('home');
  const [isDarkMode, setIsDarkMode] = useState(false);
  const manualActiveTabRef = useRef('home');
  const manualTabTimerRef = useRef(null);

  const handleNavClick = (tab, selector) => {
    manualActiveTabRef.current = tab;
    setActiveTab(tab);

    if (manualTabTimerRef.current) {
      window.clearTimeout(manualTabTimerRef.current);
    }

    manualTabTimerRef.current = window.setTimeout(() => {
      manualActiveTabRef.current = '';
      manualTabTimerRef.current = null;
    }, 650);

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

    const updateTheme = () => {
      setIsDarkMode(document.documentElement.classList.contains('dark'));
    };

    updateTheme();

    const observer = new MutationObserver(updateTheme);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class'],
    });

    const updateActiveTab = () => {
      if (manualActiveTabRef.current) {
        setActiveTab(manualActiveTabRef.current);
        return;
      }

      // Check if brand modal is open (brand summary modal)
      const modalBackdrop = document.querySelector('.fixed.inset-0.z-50');
      const isModalOpen = modalBackdrop && modalBackdrop.style.display !== 'none';

      const estimator = document.querySelector('#estimator');
      const ratesPanel = document.querySelector('.hero-rates-panel');
      const inventorySection = document.querySelector('.heatmap-section');
      const scrollY = window.scrollY + window.innerHeight * 0.35;

      // If modal is open (viewing brand summary), keep calculator tab active
      if (isModalOpen && estimator) {
        setActiveTab('calculator');
        return;
      }

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

    // Watch for modal open/close to update active tab immediately
    const modalObserver = new MutationObserver(() => {
      updateActiveTab();
    });
    
    // Observe the body for child additions/removals (modals)
    modalObserver.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['class', 'style']
    });

    return () => {
      window.removeEventListener('scroll', updateActiveTab);
      window.removeEventListener('resize', updateActiveTab);
      if (manualTabTimerRef.current) {
        window.clearTimeout(manualTabTimerRef.current);
      }
      observer.disconnect();
      modalObserver.disconnect();
    };
  }, []);

  const navButtonClass = (isActive) =>
    `group flex flex-col items-center justify-center gap-1 min-w-0 rounded-2xl px-3 py-2 transition-all duration-200 ease-out transform-gpu ${
      isActive
        ? isDarkMode
          ? 'text-amber-300 bg-amber-400/10 shadow-[0_10px_25px_rgba(251,191,36,0.14)] scale-[1.03]'
          : 'text-orange-500 bg-orange-500/10 shadow-[0_10px_25px_rgba(249,115,22,0.14)] scale-[1.03]'
        : isDarkMode
          ? 'text-stone-500 hover:text-amber-300 hover:bg-stone-800/70'
          : 'text-stone-400 hover:text-orange-400 hover:bg-stone-100/80'
    }`;

  return (
    <nav className={`fixed bottom-0 left-0 right-0 backdrop-blur-xl border-t pb-safe pt-2 px-4 flex justify-between items-center sm:hidden z-50 transition-colors duration-300 ${isDarkMode ? 'bg-stone-900/90 border-stone-700' : 'bg-white/90 border-stone-200'}`}>
      {/* Home button temporarily disabled
      <button type="button" onClick={() => handleNavClick('home', '#top')} className={navButtonClass(activeTab === 'home')}>
        <Home size={22} />
        <span className={`text-[10px] font-medium transition-colors ${activeTab === 'home' ? (isDarkMode ? 'text-amber-300' : 'text-orange-500') : ''}`}>Home</span>
      </button>
      */}

      {/* Reordered buttons: Rates, Calculator, Inventory (functionality unchanged) */}

      <button type="button" onClick={() => handleNavClick('rates', 'rates')} className={navButtonClass(activeTab === 'rates')}>
        <BarChart2 size={22} />
        <span className={`text-[10px] font-medium transition-colors ${activeTab === 'rates' ? (isDarkMode ? 'text-amber-300' : 'text-orange-500') : ''}`}>Rates</span>
      </button>

      <button type="button" onClick={() => handleNavClick('calculator', '#estimator')} className={navButtonClass(activeTab === 'calculator')}>
        <Activity size={22} />
        <span className={`text-[10px] font-medium transition-colors ${activeTab === 'calculator' ? (isDarkMode ? 'text-amber-300' : 'text-orange-500') : ''}`}>Calculator</span>
      </button>

      <button type="button" onClick={() => handleNavClick('inventory', 'inventory')} className={navButtonClass(activeTab === 'inventory')}>
        <LayoutGrid size={22} />
        <span className={`text-[10px] font-medium transition-colors ${activeTab === 'inventory' ? (isDarkMode ? 'text-amber-300' : 'text-orange-500') : ''}`}>Inventory</span>
      </button>
    </nav>
  );
}
