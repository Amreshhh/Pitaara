'use client';

import { useState, useEffect, useRef } from 'react';

export default function InventoryHeatmap() {
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [heatmapData, setHeatmapData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [categoriesLoaded, setCategoriesLoaded] = useState(false);
  const [error, setError] = useState(null);
  const [plotlyReady, setPlotlyReady] = useState(false);
  const [viewportWidth, setViewportWidth] = useState(0);
  const plotDivRef = useRef(null);

  const isMobile = viewportWidth > 0 && viewportWidth < 640;

  // Load Plotly on client-side only
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const script = document.createElement('script');
    script.src = 'https://cdn.plot.ly/plotly-2.26.0.min.js';
    script.async = true;
    script.onload = () => setPlotlyReady(true);
    document.head.appendChild(script);
    
    return () => {
      if (document.head.contains(script)) {
        document.head.removeChild(script);
      }
    };
  }, []);

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
        const cats = data.categories || [];
        setCategories(cats);
        
        // Set first category only if categories loaded
        if (cats.length > 0) {
          console.log('🎯 Setting default category to:', cats[0]);
          setSelectedCategory(cats[0]);
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
        console.log('📊 Fetching heatmap for:', categoryParam);
        const response = await fetch(`/api/inventory-matrix/${categoryParam}`);
        if (!response.ok) throw new Error(`API returned ${response.status}`);
        
        const data = await response.json();
        console.log('✅ Heatmap data loaded');
        setHeatmapData(data);
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
  }, [selectedCategory, categoriesLoaded]);

  // Render Plotly chart when data changes
  useEffect(() => {
    if (!heatmapData || !plotDivRef.current || !plotlyReady || typeof window === 'undefined') return;

    const { weight_ranges, purities, matrix, category } = heatmapData;
    const compactMode = isMobile;

    const trace = {
      z: matrix,
      x: purities,
      y: weight_ranges,
      type: 'heatmap',
      colorscale: 'Viridis',
      hoverongaps: false,
      hovertemplate: '<b>Weight Range:</b> %{y}<br><b>Purity:</b> %{x}<br><b>Product Count:</b> %{z}<extra></extra>',
      colorbar: {
        title: 'Product<br>Count',
        thickness: 15,
        len: 0.7,
      },
    };

    const layout = {
      title: `<b>${category}</b> - Inventory Matrix (Weight × Purity)`,
      xaxis: {
        title: '<b>Purity</b>',
        side: 'bottom',
        tickfont: {
          size: compactMode ? 10 : 12,
        },
      },
      yaxis: {
        title: '<b>Weight Range (grams)</b>',
        autorange: 'reversed',
        tickfont: {
          size: compactMode ? 10 : 12,
        },
      },
      margin: compactMode
        ? { l: 72, r: 32, t: 72, b: 70 }
        : { l: 120, r: 100, t: 100, b: 100 },
      titlefont: {
        size: compactMode ? 14 : 18,
      },
      plot_bgcolor: 'rgba(0,0,0,0)',
      paper_bgcolor: 'rgba(255,255,255,1)',
      font: {
        family: 'var(--font-sans), Inter, system-ui, sans-serif',
        color: 'rgba(0,0,0,0.7)',
        size: compactMode ? 10 : 12,
      },
      hovermode: 'closest',
      responsive: true,
      autosize: true,
    };

    const config = {
      responsive: true,
      displayModeBar: !compactMode,
      displaylogo: false,
      modeBarButtonsToRemove: ['lasso2d', 'select2d', 'toImage'],
    };

    window.Plotly.newPlot(plotDivRef.current, [trace], layout, config);

    // Cleanup
    return () => {
      if (plotDivRef.current && window.Plotly) {
        window.Plotly.purge(plotDivRef.current);
      }
    };
  }, [heatmapData, plotlyReady]);

  if (loading || !plotlyReady || !heatmapData) {
    return (
      <div className="w-full flex items-center justify-center bg-linear-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 rounded-lg p-8 min-h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading inventory matrix...</p>
        </div>
      </div>
    );
  }

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

  if (!heatmapData) {
    return null;
  }

  const { total_products } = heatmapData;

  return (
    <div className="heatmap-section w-full bg-linear-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 rounded-2xl p-4 sm:p-6 md:p-8">
      {/* Header */}
      <div className="mb-5 sm:mb-8">
        <h2 className="heatmap-title text-xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-3 sm:mb-6">
          📊 Inventory Matrix Heatmap
        </h2>

        {/* Category Dropdown */}
        <div className="heatmap-controls flex flex-col sm:flex-row gap-3 sm:gap-4 sm:items-center">
          <label htmlFor="category-select" className="text-sm font-semibold text-gray-700 dark:text-gray-300">
            Select Category:
          </label>
          <select
            id="category-select"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="w-full sm:w-auto min-h-11 px-4 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-amber-500 focus:border-transparent cursor-pointer transition-all"
          >
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>

          {/* Stats */}
          <div className="ml-0 sm:ml-auto text-sm text-gray-600 dark:text-gray-400">
            <p>
              <span className="font-semibold text-amber-600 dark:text-amber-400">
                {total_products}
              </span>{' '}
              products
            </p>
          </div>
        </div>
      </div>

      {/* Heatmap */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-3 sm:p-6 overflow-hidden">
        <div
          ref={plotDivRef}
          className="heatmap-chart"
          style={{ width: '100%', height: isMobile ? '420px' : '600px' }}
        ></div>
      </div>

      {/* Legend */}
      <div className="heatmap-legend mt-5 sm:mt-8 grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-6 text-sm text-gray-600 dark:text-gray-400">
        <div>
          <p className="font-semibold text-gray-900 dark:text-white mb-2">📍 How to Read</p>
          <ul className="list-disc list-inside space-y-1">
            <li>X-axis: Purity levels (14K, 18K, 22K, 24K)</li>
            <li>Y-axis: Weight ranges (in grams)</li>
            <li>Color intensity: Product availability</li>
          </ul>
        </div>
        <div>
          <p className="font-semibold text-gray-900 dark:text-white mb-2">🎨 Interaction</p>
          <ul className="list-disc list-inside space-y-1">
            <li>Hover over cells to see exact counts</li>
            <li>Use dropdown to switch categories</li>
            <li>Pinch/zoom on touch devices for details</li>
          </ul>
        </div>
        <div>
          <p className="font-semibold text-gray-900 dark:text-white mb-2">💡 Tips</p>
          <ul className="list-disc list-inside space-y-1">
            <li>Brighter colors = more products</li>
            <li>Darker colors = fewer products</li>
            <li>Use toolbar for export/screenshots</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
