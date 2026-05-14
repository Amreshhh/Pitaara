'use client';

import { useEffect, useRef, useState } from 'react';
import {
  Header,
  HeroSection,
  InputSection,
  BrandGrid,
  BrandModal,
  FeedbackSection,
  InventoryHeatmap,
  Disclaimer,
} from '@/components';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { useLiveRates } from '@/hooks/useLiveRates';
import { useGoldCalculator } from '@/hooks/useGoldCalculator';
import { CATEGORIES, SUBCATEGORIES, COIN_WEIGHT_OPTIONS } from '@/lib/constants';
import { getThemeStyles } from '@/lib/utils';

// File ke top par ise replace kar dijiye
const normalizeCategoryId = (value) => {
  if (typeof value !== 'string') return ''; // Agar string nahi hai toh empty return kar do
  const trimmed = value.trim();
  const lowered = trimmed.toLowerCase();

  // Preserve canonical IDs used by SUBCATEGORIES and calculator payload
  if (lowered === 'hoops' || lowered === 'hoops(a type of bali)') return 'Hoops';
  if (lowered === 'band or plain ring' || lowered === 'band(plain ring)') return 'Band or Plain Ring';

  return trimmed
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '');
};

const getCached24KRate = () => {
  if (typeof window === 'undefined') return 14620;
  try {
    const raw = window.localStorage.getItem('cached_gold_rates');
    if (!raw) return 14620;
    const parsed = JSON.parse(raw);
    const rates = Array.isArray(parsed) ? parsed : parsed?.rates;
    if (!Array.isArray(rates)) return 14620;
    const tanishq = rates.find((item) => item?.Brand === 'Tanishq');
    const rate = Number(tanishq?.['24K']);
    return Number.isFinite(rate) && rate > 0 ? rate : 14620;
  } catch {
    return 14620;
  }
};

const mapApiCategories = (categories) => {
  if (!Array.isArray(categories)) return [];

  const mapped = categories
    .map((entry) => {
      if (typeof entry === 'string') {
        const label = entry.trim();
        const id = normalizeCategoryId(label);
        return id ? { id, label } : null;
      }

      if (entry && typeof entry === 'object') {
        const rawLabel = entry.label || entry.name || entry.id;
        if (typeof rawLabel !== 'string') return null;
        const label = rawLabel.trim();
        const id = normalizeCategoryId(entry.id || label);
        return id ? { id, label } : null;
      }

      return null;
    })
    .filter(Boolean);

  // Keep IDs unique to avoid duplicate options.
  const seen = new Set();
  return mapped.filter((item) => {
    if (seen.has(item.id)) return false;
    seen.add(item.id);
    return true;
  });
};

const DEFAULT_INPUTS = {
  weight: 10,
  purity: '22K',
  category: 'chain',
  subcategory: 'gold',
  rate: getCached24KRate(),
};

export default function App() {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [inputs, setInputs] = useState(DEFAULT_INPUTS);
  const [selectedBrand, setSelectedBrand] = useState(null);
  const [calcTrigger, setCalcTrigger] = useState(0);
  const [inputsDirty, setInputsDirty] = useState(false);
  const [apiCategories, setApiCategories] = useState(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [isHeatmapMinimized, setIsHeatmapMinimized] = useState(true);
  const estimatorRef = useRef(null);

  // 🔥 Destructure cache status and last updated time
  const { liveRates, loading, cacheStatus, lastUpdated } = useLiveRates();
  const results = useGoldCalculator(inputs, calcTrigger);
  const styles = getThemeStyles(isDarkMode);

  // Use API categories if available, otherwise fall back to static CATEGORIES
  const displayCategories = apiCategories || CATEGORIES;

  // Header ke liye 24K rate from the latest cached live data
  const currentRate24K = liveRates?.find((r) => r.Brand === 'Tanishq')?.['24K'] ?? null;

  // On first load, update DEFAULT_INPUTS.rate to use cached 24K rate
  useEffect(() => {
    if (currentRate24K && inputs.rate === DEFAULT_INPUTS.rate) {
      setInputs((prev) => ({ ...prev, rate: currentRate24K }));
    }
  }, [currentRate24K]);

  // Fetch categories from API
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await fetch('/api/inventory-categories');
        if (response.ok) {
          const data = await response.json();
          const incoming = data?.categories;
          const normalized = mapApiCategories(incoming);
          if (normalized.length) {
            setApiCategories(normalized);
          }
        }
      } catch (err) {
        console.error('Failed to fetch categories:', err);
        // Silently fail; use static CATEGORIES instead
      }
    };
    fetchCategories();
  }, []);

  const toggleTheme = () => setIsDarkMode((prev) => !prev);

  const scrollToEstimator = () => {
    estimatorRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleInputChange = (event) => {
    const { name, value } = event.target;

    // Category change par subcategory bhi reset karo
    if (name === 'category') {
      const subcategories = SUBCATEGORIES[value];
      const isCoinCategory = value === 'coin';
      setInputs((prev) => ({
        ...prev,
        category: value,
        subcategory: subcategories?.[0]?.id || '',
        weight: isCoinCategory ? COIN_WEIGHT_OPTIONS[0].id : prev.weight,
      }));
      setInputsDirty(true);
      return;
    }

    if (name === 'weight' && inputs.category === 'coin') {
      setInputs((prev) => ({ ...prev, weight: value }));
      setInputsDirty(true);
      return;
    }

    setInputs((prev) => {
      if (name === 'weight') {
        let num = parseFloat(value);
        if (!Number.isFinite(num)) num = 0;
        // clamp between 0 and 200
        num = Math.max(0, Math.min(200, num));
        return { ...prev, weight: num };
      }

      if (name === 'rate') {
        return { ...prev, rate: parseFloat(value) || 0 };
      }

      return { ...prev, [name]: value };
    });
    setInputsDirty(true);
  };

  const handleFind = () => {
    setInputsDirty(false);
    setCalcTrigger((t) => t + 1);
    setIsCalculating(true);
    // Simulate calculation time - turn off after results come in
    setTimeout(() => setIsCalculating(false), 800);
  };

  const handleBrandSelect = (brand) => {
    // Clear previous modal immediately to prevent overlapping
    setSelectedBrand(null);
    // Set new brand after a tick to ensure clean transition
    setTimeout(() => setSelectedBrand(brand), 0);
  };
  const handleModalClose = () => {
    setSelectedBrand(null);
  };

  return (
    <div id="top" className={`app-shell w-full font-sans transition-colors duration-500 pb-28 sm:pb-0 ${styles.bgMain} ${styles.textMain}`}>
      <Header
        isDarkMode={isDarkMode}
        currentRate={currentRate24K}
        onToggleTheme={toggleTheme}
      />

      {/* 🔥 Cache Status Indicator */}
      <div className={`fixed bottom-4 right-4 px-3 py-2 rounded text-xs font-medium z-50 ${
        cacheStatus?.includes('offline') 
          ? 'bg-orange-500 text-white' 
          : cacheStatus?.includes('error')
          ? 'bg-red-500 text-white'
          : 'bg-green-500 text-white'
      }`}>
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${
            cacheStatus?.includes('offline') 
              ? 'bg-orange-200 animate-pulse' 
              : cacheStatus?.includes('error')
              ? 'bg-red-200 animate-pulse'
              : 'bg-green-200'
          }`}></span>
          <span>
            {cacheStatus?.includes('offline') 
              ? '📦 Cached' 
              : cacheStatus?.includes('error')
              ? '⚠️ Default'
              : '✅ Live Cache'}
          </span>
          {lastUpdated && (
            <span className="text-xs opacity-80 ml-2">
              {lastUpdated.split(' ').slice(-2).join(' ')}
            </span>
          )}
        </div>
      </div>

      <HeroSection
        isDarkMode={isDarkMode}
        onScrollToEstimator={scrollToEstimator}
        liveRates={liveRates}
        loading={loading}
        heading="Pitaara"
        eyebrow="by"
        brandLine="Om-Rani"
        subheading="Find the best value. Compare live gold rates and making charges across India's leading jewelry brands."
      />

      <div id="estimator" ref={estimatorRef} className="relative z-20 w-full">
        <main className="max-w-7xl mx-auto px-4 py-12">
          <InputSection
            inputs={inputs}
            onInputChange={handleInputChange}
            isDarkMode={isDarkMode}
            categories={displayCategories}
            onFind={handleFind}
            inputsDirty={inputsDirty}
            isCalculating={isCalculating}
          />

          <BrandGrid
            results={results}
            isDarkMode={isDarkMode}
            onBrandSelect={handleBrandSelect}
            weight={inputs.weight}
            purity={inputs.purity}
            category={inputs.category}
          />

          {/* 🔥 Inventory Matrix Heatmap Section */}
          {/* <div className="mt-16 sm:mt-20 pt-10 sm:pt-12 border-t border-gray-300 dark:border-gray-700 overflow-hidden">
            Enhanced Description Section
            <div className={`mb-6 p-4 rounded-xl border ${
              isDarkMode
                ? 'bg-amber-950/30 border-amber-800/50'
                : 'bg-amber-50/40 border-amber-200/50'
            }`}>
              <p className={`mb-2 text-lg font-semibold ${styles.textMain}`}>📊 Inventory blueprint of all listed brands</p>
              <p className={`text-sm font-medium ${styles.textMuted}`}>Note: Data displayed is Highly accurate</p>
            </div>
            <div className="mb-6 border-b border-gray-300 dark:border-gray-700"></div>

            {/* Minimize Toggle Button 
            <button
              onClick={() => setIsHeatmapMinimized((s) => !s)}
              className={`flex items-center gap-3 mb-4 px-4 py-2 rounded-lg font-medium ${
                isDarkMode
                  ? 'bg-linear-to-r from-amber-700 to-amber-800 hover:from-amber-600 hover:to-amber-700 text-white'
                  : 'bg-linear-to-r from-amber-600 to-amber-700 hover:from-amber-500 hover:to-amber-600 text-white'
              } btn-press-animate`}
            >
              <span className={`inline-block transform transition-transform duration-300 ${isHeatmapMinimized ? '' : 'rotate-180'}`}>
                <ChevronDown size={18} />
              </span>
              <span>{isHeatmapMinimized ? 'Expand Inventory Matrix' : 'Collapse Inventory Matrix'}</span>
            </button>

            {/* Collapsible Heatmap Container (always present, toggles open class) *
            <div className={`mt-4 heatmap-collapsible ${isHeatmapMinimized ? '' : 'open'}`}>
              <div className="animation-fade-in">
                <InventoryHeatmap isDarkMode={isDarkMode} />
              </div>
            </div>
          </div> */}

          <FeedbackSection isDarkMode={isDarkMode} />

          <Disclaimer isDarkMode={isDarkMode} />
        </main>
      </div>

      <BrandModal
        selectedBrand={selectedBrand}
        isDarkMode={isDarkMode}
        onClose={handleModalClose}
        queryContext={{
          weight: inputs.weight,
          weightRange: inputs.category === 'coin' ? inputs.weight : null,
          purity: inputs.purity,
          category: inputs.category,
        }}
      />
    </div>
  );
}
