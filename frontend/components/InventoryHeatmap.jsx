'use client';

import { useState, useEffect, useMemo } from 'react';
import { getThemeStyles } from '@/lib/utils';

export default function InventoryHeatmap({ isDarkMode = false }) {
  const styles = getThemeStyles(isDarkMode);
  const [categoriesObj, setCategoriesObj] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedPurity, setSelectedPurity] = useState('22K');
  const [availablePurities, setAvailablePurities] = useState([]);
  const [heatmapData, setHeatmapData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [categoriesLoaded, setCategoriesLoaded] = useState(false);
  const [error, setError] = useState(null);
  const [viewportWidth, setViewportWidth] = useState(0);
  const purityOrder = ['24K', '22K', '14K', '18K'];

  const isMobile = viewportWidth > 0 && viewportWidth < 640;

  // Track viewport width for responsive chart/layout behavior
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const updateViewport = () => setViewportWidth(window.innerWidth);

    updateViewport();
    window.addEventListener('resize', updateViewport, { passive: true });

    return () => window.removeEventListener('resize', updateViewport);
  }, []);

  // Fetch all categories on mount
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        setLoading(true);
        console.log('🔍 Fetching categories via Next.js API route');
        const response = await fetch('/api/inventory-categories');
        
        if (!response.ok) {
          throw new Error(`API returned ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ Categories fetched:', data.categories);
        const rawCats = data.categories || [];

        // Map display labels but keep original value for backend queries
        const mapped = rawCats.map((c) => {
          const original = c;
          // Normalize value to match backend canonical category strings
          let value = original;
          let label = String(c || '').trim();
          if (label === 'Hoops(a type of Bali)') {
            label = 'Hoops';
          }
          // Accept both historical and canonical forms and send canonical to backend
          if (label === 'Band(Plain Ring)' || label === 'Band or Plain Ring') {
            value = 'Band or Plain Ring';
            label = 'Band or Plain Ring';
          }
          return { value, label };
        });

        if (!mapped.some((cat) => cat.value === 'Band or Plain Ring')) {
          mapped.push({ value: 'Band or Plain Ring', label: 'Band or Plain Ring' });
        }

        setCategoriesObj(mapped);

        if (mapped.length > 0) {
          console.log('🎯 Setting default category to:', mapped[0]);
          setSelectedCategory(mapped[0].value);
        }

        setCategoriesLoaded(true);
      } catch (err) {
        console.error('❌ Failed to fetch categories:', err);
        setError(`Cannot fetch categories: ${err.message}`);
        setCategoriesLoaded(false);
      } finally {
        setLoading(false);
      }
    };

    fetchCategories();
  }, []);

  // Fetch heatmap data when category changes
  useEffect(() => {
    if (!categoriesLoaded) {
      console.log('⏳ Waiting for categories to load...');
      return;
    }

    if (!selectedCategory || typeof selectedCategory !== 'string' || selectedCategory.trim() === '') {
      console.log('⏭️  Skipping heatmap fetch - no valid category yet:', { selectedCategory, type: typeof selectedCategory });
      return;
    }

    const fetchHeatmapData = async () => {
      try {
        setLoading(true);
        const categoryParam = encodeURIComponent(selectedCategory.trim());
        const purityTrim = (selectedPurity || '').trim();
        const purityParam = purityTrim ? `&purity=${encodeURIComponent(purityTrim)}` : '';
        console.log('📊 Fetching heatmap (brands × ranges) for:', categoryParam, purityTrim || '<no-purity>');
        const response = await fetch(`/api/inventory-heatmap?category=${categoryParam}${purityParam}`);
        if (!response.ok) throw new Error(`API returned ${response.status}`);
        
        const data = await response.json();
        console.log('✅ Heatmap data loaded');
        setHeatmapData(data);
        // update available purities from backend
        setAvailablePurities((data.available_purities || []).filter((p) => purityOrder.includes(p)));
        // If selectedPurity is empty (first load), pick the first allowed purity available
        if (!selectedPurity || selectedPurity === '') {
          const pick = purityOrder.find((p) => (data.available_purities || []).includes(p));
          if (pick) setSelectedPurity(pick);
        } else {
          // if currently selected purity is not present in availablePurities, reset to first allowed
          if (selectedPurity && !(data.available_purities || []).includes(selectedPurity)) {
            const pick = purityOrder.find((p) => (data.available_purities || []).includes(p));
            setSelectedPurity(pick || '');
          }
        }
        setError(null);
      } catch (err) {
        console.error('❌ Error fetching heatmap:', err);
        setError(err.message);
        setHeatmapData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchHeatmapData();
  }, [selectedCategory, categoriesLoaded, selectedPurity]);

  const brands = heatmapData?.brands || [];
  const weightRanges = heatmapData?.weight_ranges || [];
  const matrix = heatmapData?.matrix || [];
  const maxCount = useMemo(() => {
    if (!Array.isArray(matrix)) return 0;
    return matrix.flat().reduce((max, value) => Math.max(max, Number(value) || 0), 0);
  }, [matrix]);

  const cellStyle = (value) => {
    const count = Number(value) || 0;
    const intensity = maxCount > 0 ? count / maxCount : 0;
    
    if (isDarkMode) {
      const bgAlpha = 0.10 + intensity * 0.72;
      const borderAlpha = 0.22 + intensity * 0.38;
      return {
        background: `linear-gradient(135deg, rgba(245,158,11,${bgAlpha}) 0%, rgba(30,41,59,${Math.max(0.22, bgAlpha - 0.03)}) 100%)`,
        borderColor: `rgba(251,191,36,${borderAlpha})`,
        color: intensity > 0.45 ? '#fffaf0' : '#f8e7bf',
        boxShadow: intensity > 0.55 ? '0 14px 34px rgba(15,23,42,0.24)' : '0 8px 18px rgba(15,23,42,0.10)',
      };
    } else {
      const r = Math.round(255 * (1 - intensity * 0.3));
      const g = Math.round(180 + intensity * 75);
      const b = Math.round(50 + intensity * 205);
      const bgAlpha = 0.15 + intensity * 0.85;
      const borderAlpha = 0.35 + intensity * 0.65;
      return {
        background: `linear-gradient(135deg, rgba(255,245,210,${0.8 + intensity * 0.2}) 0%, rgba(${r},${g},${b},${bgAlpha}) 100%)`,
        borderColor: `rgba(${Math.round(255 * (1 - intensity * 0.2))},${Math.round(180 + intensity * 60)},${Math.round(50 + intensity * 180)},${borderAlpha})`,
        color: '#000000',
        boxShadow: intensity > 0.6 ? '0 12px 28px rgba(200,100,0,0.25)' : '0 6px 14px rgba(200,100,0,0.12)',
      };
    }
  };

  if (error) {
    return (
      <div className="w-full p-8 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
        <div className="max-w-md mx-auto">
          <h3 className="text-lg font-bold text-red-700 dark:text-red-400 mb-3">
            🔴 Cannot Load Heatmap
          </h3>
          <p className="text-sm text-red-600 dark:text-red-300 mb-4">{error}</p>
          <div className="bg-white dark:bg-gray-900 p-4 rounded text-xs font-mono text-gray-700 dark:text-gray-300 mb-4">
            <p className="mb-2">Make sure:</p>
            <p className="text-gray-600">1. Backend is running (locally: port 8000)</p>
            <p className="text-gray-600">2. BACKEND_API_URL env var is set</p>
            <p className="text-gray-600">3. Network can reach backend server</p>
          </div>
        </div>
      </div>
    );
  }

  if (loading || !heatmapData) {
    return (
      <div className="w-full flex items-center justify-center bg-linear-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 rounded-lg p-8 min-h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading inventory matrix...</p>
        </div>
      </div>
    );
  }
  const { total_products, category, purity } = heatmapData;
  const gridColumns = `140px repeat(${brands.length || 4}, minmax(110px, 1fr))`;

  return (
    <div
      className={`heatmap-section w-full rounded-2xl p-4 sm:p-6 md:p-8 border shadow-[0_24px_80px_rgba(2,6,23,0.18)] ${styles.cardBg} ${styles.borderColor}`}
      style={{
        backgroundImage: isDarkMode
          ? 'radial-gradient(circle at top left, rgba(251,191,36,0.10), transparent 28%), linear-gradient(135deg, #0b1220 0%, #101827 45%, #1f2937 100%)'
          : 'radial-gradient(circle at top left, rgba(217,119,6,0.08), transparent 30%), linear-gradient(135deg, #fffaf1 0%, #f8f2e7 46%, #ede4d2 100%)',
      }}
    >
      {/* Header */}
      <div className="mb-5 sm:mb-8">
        <h2 className={`heatmap-title text-xl sm:text-3xl font-bold mb-3 sm:mb-6 tracking-tight ${styles.textMain}`}>
           Inventory Matrix Heatmap
        </h2>
        <p className={`text-sm mb-4 ${styles.textMuted}`}>
          Category: <span className={`font-semibold ${isDarkMode ? 'text-amber-200' : 'text-amber-700'}`}>{category}</span> • Purity: <span className={`font-semibold ${isDarkMode ? 'text-amber-200' : 'text-amber-700'}`}>{purity}</span>
        </p>

        {/* Category Dropdown */}
        <div className="heatmap-controls flex flex-col sm:flex-row gap-3 sm:gap-4 sm:items-center">
          <label htmlFor="category-select" className={`text-sm font-semibold ${styles.textMain}`}>
            Select Category:
          </label>
          <select
            id="category-select"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className={`w-full sm:w-auto min-h-11 px-4 py-3 rounded-lg border shadow-inner shadow-black/10 focus:ring-2 focus:ring-amber-400 focus:border-transparent cursor-pointer transition-all backdrop-blur ${isDarkMode ? 'border-white/10 bg-slate-950/70 text-slate-100' : 'border-amber-200/60 bg-white/80 text-stone-900'}`}
          >
            {categoriesObj.map((cat) => (
              <option key={cat.value} value={cat.value}>
                {cat.label}
              </option>
            ))}
          </select>

          {/* Purity selector */}
          <label htmlFor="purity-select" className={`text-sm font-semibold ml-0 sm:ml-4 ${styles.textMain}`}>
            Purity:
          </label>
          <select
            id="purity-select"
            value={selectedPurity}
            onChange={(e) => setSelectedPurity(e.target.value)}
            className={`w-full sm:w-auto min-h-11 px-4 py-3 rounded-lg border shadow-inner shadow-black/10 focus:ring-2 focus:ring-amber-400 focus:border-transparent cursor-pointer transition-all backdrop-blur ${isDarkMode ? 'border-white/10 bg-slate-950/70 text-slate-100' : 'border-amber-200/60 bg-white/80 text-stone-900'}`}
          >
            {purityOrder.filter((p) => availablePurities.includes(p)).map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>

          {/* Stats */}
          <div className={`ml-0 sm:ml-auto text-sm ${styles.textMuted}`}>
            <p>
              <span className={`font-semibold ${isDarkMode ? 'text-amber-300' : 'text-amber-700'}`}>
                {total_products}
              </span>{' '}
              products
            </p>
          </div>
        </div>
      </div>

      {/* Heatmap */}
      <div className={`rounded-2xl p-3 sm:p-6 overflow-hidden shadow-[inset_0_1px_0_rgba(255,255,255,0.04)] ${isDarkMode ? 'border border-white/10 bg-slate-950/55' : 'border border-amber-100 bg-white/70'}`}>
        <div className="overflow-x-auto">
          <div className="min-w-190">
            <div
              className="grid gap-2 mb-2"
              style={{ gridTemplateColumns: gridColumns }}
            >
              <div className="text-xs sm:text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide px-2 py-3" />
              {brands.map((brand) => (
                <div key={brand} className={`text-center text-sm sm:text-base font-semibold px-2 py-3 rounded-lg border shadow-[0_8px_20px_rgba(15,23,42,0.18)] ${isDarkMode ? 'text-amber-50 bg-linear-to-b from-slate-800/95 to-slate-900/95 border-amber-200/10' : 'text-stone-800 bg-linear-to-b from-amber-50 to-stone-100 border-amber-200/50'}`}>
                  {brand}
                </div>
              ))}
            </div>

            <div className="space-y-2">
              {weightRanges.map((rangeLabel, rowIndex) => (
                <div
                  key={rangeLabel}
                  className="grid gap-2"
                  style={{ gridTemplateColumns: gridColumns }}
                >
                  <div className={`flex items-center justify-end pr-2 text-xs sm:text-sm font-medium ${styles.textMuted}`}>
                    {rangeLabel}
                  </div>
                  {brands.map((brand, colIndex) => {
                    const count = matrix?.[rowIndex]?.[colIndex] || 0;
                    return (
                      <div
                        key={`${rangeLabel}-${brand}`}
                        className="min-h-16 sm:min-h-20 rounded-xl border flex flex-col items-center justify-center text-center px-2 py-3 transition-all duration-200 hover:scale-[1.02] hover:shadow-[0_18px_36px_rgba(15,23,42,0.22)]"
                        style={cellStyle(count)}
                        title={`${brand} • ${rangeLabel} • ${count} products`}
                      >
                        <div className="text-lg sm:text-2xl font-bold leading-none">{count}</div>
                        <div className="text-[10px] sm:text-xs font-semibold uppercase tracking-wide mt-1 opacity-90">pcs</div>
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Legend */}
      {/* <div className={`heatmap-legend mt-5 sm:mt-8 grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-6 text-sm ${styles.textMuted}`}>
        <div>
          <p className={`font-semibold mb-2 ${styles.textMain}`}>📍 How to Read</p>
          <ul className="list-disc list-inside space-y-1">
            <li>X-axis: Brands (Tanishq, Malabar, Kalyan, Senco)</li>
            <li>Y-axis: Weight ranges (in grams)</li>
            <li>Color intensity: Product availability</li>
          </ul>
        </div>
        <div>
          <p className={`font-semibold mb-2 ${styles.textMain}`}>🎨 Interaction</p>
          <ul className="list-disc list-inside space-y-1">
            <li>Hover over cells to see exact counts</li>
            <li>Use dropdown to switch categories</li>
            <li>Use the purity selector to filter the inventory slice</li>
          </ul>
        </div>
        <div>
          <p className={`font-semibold mb-2 ${styles.textMain}`}>💡 Tips</p>
          <ul className="list-disc list-inside space-y-1">
            <li>Brighter colors = more products</li>
            <li>Darker colors = fewer products</li>
            <li>This version works without Plotly or external scripts</li>
          </ul>
        </div>
      </div> */}
    </div>
  );
}
