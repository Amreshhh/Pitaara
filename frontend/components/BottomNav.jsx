'use client';

import React, { useEffect, useRef, useState } from 'react';
import { Activity, BarChart2, LayoutGrid } from 'lucide-react';

const NAV_ITEMS = [
  { id: 'rates', label: 'Rates', icon: BarChart2, target: '.hero-rates-panel' },
  { id: 'calculator', label: 'Calculator', icon: Activity, target: '#estimator' },
  { id: 'inventory', label: 'Inventory', icon: LayoutGrid, target: '.heatmap-section' },
];

export default function BottomNav() {
  const [activeTab, setActiveTab] = useState('calculator');
  const [isDarkMode, setIsDarkMode] = useState(false);
  const manualActiveTabRef = useRef('');
  const manualResetTimerRef = useRef(null);

  const scrollToTarget = (selector) => {
    if (typeof window === 'undefined') return;

    const target = document.querySelector(selector);
    target?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  const handleNavClick = (tabId, selector) => {
    manualActiveTabRef.current = tabId;
    setActiveTab(tabId);

    if (manualResetTimerRef.current) {
      window.clearTimeout(manualResetTimerRef.current);
    }

    manualResetTimerRef.current = window.setTimeout(() => {
      manualActiveTabRef.current = '';
      manualResetTimerRef.current = null;
    }, 500);

    scrollToTarget(selector);
  };

  useEffect(() => {
    if (typeof window === 'undefined') return undefined;

    const updateTheme = () => {
      const rootHasDarkClass = document.documentElement.classList.contains('dark');
      const bodyTheme = document.body?.dataset?.theme;
      setIsDarkMode(rootHasDarkClass || bodyTheme === 'dark');
    };

    const resolveTarget = (selector) => document.querySelector(selector);

    const chooseVisibleTab = () => {
      if (manualActiveTabRef.current) {
        setActiveTab(manualActiveTabRef.current);
        return;
      }

      const entries = NAV_ITEMS.map((item) => {
        const element = resolveTarget(item.target);
        if (!element) {
          return { id: item.id, visible: false, ratio: 0, top: Number.POSITIVE_INFINITY };
        }

        const rect = element.getBoundingClientRect();
        const viewportHeight = window.innerHeight || document.documentElement.clientHeight;
        const visibleTop = Math.max(rect.top, 0);
        const visibleBottom = Math.min(rect.bottom, viewportHeight);
        const visibleHeight = Math.max(0, visibleBottom - visibleTop);
        const ratio = rect.height > 0 ? visibleHeight / rect.height : 0;

        return {
          id: item.id,
          visible: ratio > 0,
          ratio,
          top: rect.top,
        };
      });

      const visibleEntries = entries.filter((entry) => entry.visible);

      if (!visibleEntries.length) {
        return;
      }

      const inventoryEntry = visibleEntries.find((entry) => entry.id === 'inventory');
      if (inventoryEntry && inventoryEntry.ratio >= 0.12) {
        setActiveTab('inventory');
        return;
      }

      const ratesEntry = visibleEntries.find((entry) => entry.id === 'rates');
      if (ratesEntry && ratesEntry.ratio >= 0.12) {
        setActiveTab('rates');
        return;
      }

      const calculatorEntry = visibleEntries.find((entry) => entry.id === 'calculator');
      if (calculatorEntry) {
        setActiveTab('calculator');
      }
    };

    updateTheme();
    chooseVisibleTab();

    const themeObserver = new MutationObserver(updateTheme);
    themeObserver.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class'],
    });

    const inventorySection = resolveTarget('.heatmap-section');
    const ratesPanel = resolveTarget('.hero-rates-panel');
    const estimator = resolveTarget('#estimator');

    const observer = new IntersectionObserver(
      () => {
        chooseVisibleTab();
      },
      {
        root: null,
        threshold: [0, 0.12, 0.25, 0.5],
        rootMargin: '-12% 0px -48% 0px',
      }
    );

    if (ratesPanel) observer.observe(ratesPanel);
    if (estimator) observer.observe(estimator);
    if (inventorySection) observer.observe(inventorySection);

    window.addEventListener('scroll', chooseVisibleTab, { passive: true });
    window.addEventListener('resize', chooseVisibleTab);

    const modalObserver = new MutationObserver(() => {
      chooseVisibleTab();
    });

    modalObserver.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['class', 'style', 'data-theme'],
    });

    return () => {
      window.removeEventListener('scroll', chooseVisibleTab);
      window.removeEventListener('resize', chooseVisibleTab);
      if (manualResetTimerRef.current) {
        window.clearTimeout(manualResetTimerRef.current);
      }
      observer.disconnect();
      themeObserver.disconnect();
      modalObserver.disconnect();
    };
  }, []);

  const navButtonClass = (isActive) =>
    `group flex flex-col items-center justify-center gap-1 min-w-0 rounded-2xl px-3 py-2 transition-all duration-200 ease-out transform-gpu ${
      isActive
        ? isDarkMode
          ? 'text-amber-200 bg-amber-400/15 shadow-[0_0_0_1px_rgba(251,191,36,0.18),0_0_18px_rgba(251,191,36,0.28)] scale-[1.03]'
          : 'text-orange-600 bg-orange-500/12 shadow-[0_0_0_1px_rgba(249,115,22,0.16),0_0_18px_rgba(249,115,22,0.18)] scale-[1.03]'
        : isDarkMode
          ? 'text-stone-500 hover:text-amber-300 hover:bg-stone-800/70'
          : 'text-stone-400 hover:text-orange-500 hover:bg-stone-100/80'
    }`;

  return (
    <nav
      aria-label="Mobile section navigation"
      className={`fixed bottom-0 left-0 right-0 z-50 flex items-center justify-between gap-2 border-t px-4 pb-safe pt-2 backdrop-blur-xl transition-colors duration-300 sm:hidden ${
        isDarkMode ? 'border-stone-700 bg-stone-950/92' : 'border-stone-200 bg-white/92'
      }`}
    >
      {NAV_ITEMS.map(({ id, label, icon: Icon, target }) => (
        <button
          key={id}
          type="button"
          onClick={() => handleNavClick(id, target)}
          className={navButtonClass(activeTab === id)}
          aria-current={activeTab === id ? 'page' : undefined}
        >
          <Icon size={22} strokeWidth={2.2} />
          <span
            className={`text-[10px] font-medium tracking-wide transition-colors ${
              activeTab === id ? (isDarkMode ? 'text-amber-300' : 'text-orange-600') : ''
            }`}
          >
            {label}
          </span>
        </button>
      ))}
    </nav>
  );
}
