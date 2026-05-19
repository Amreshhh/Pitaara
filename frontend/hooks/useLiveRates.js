'use client';

import useSWR from 'swr';

// ---------------------------------------------------------
// 1. Helper Functions (Kept outside the hook to avoid recreation)
// ---------------------------------------------------------
const normalizeLiveRates = (payload, cachedByBrand = {}) => {
  const rates = Array.isArray(payload?.rates) ? payload.rates : Array.isArray(payload) ? payload : null;
  if (!Array.isArray(rates) || !rates.length) {
    throw new Error('Invalid live rates payload');
  }

  const result = [];
  for (const rate of rates) {
    try {
      if (!rate || typeof rate !== 'object') throw new Error('Invalid live rates row');
      const brandName = rate.Brand === 'Candere' ? 'Kalyan' : rate.Brand;
      const normalized = { ...rate, Brand: brandName };
      const hasAnyNumericRate = ['24K', '22K', '18K', '14K'].some((key) => Number.isFinite(Number(normalized[key])));

      if (!brandName || !hasAnyNumericRate) throw new Error('Unable to parse live rate values');

      normalized._stale = false;
      result.push(normalized);
    } catch (e) {
      const maybeBrand = rate && rate.Brand ? (rate.Brand === 'Candere' ? 'Kalyan' : rate.Brand) : null;
      if (maybeBrand && cachedByBrand[maybeBrand]) {
        result.push({ ...cachedByBrand[maybeBrand], _stale: true });
      } else {
        console.warn('[SWR Fetcher] Skipping brand due to parse failure', rate, e.message);
      }
    }
  }

  if (!result.length) throw new Error('No usable live rates in payload');
  return result;
};

const mergeTanishqRate = (rates, tanishqRate) => {
  if (!tanishqRate || typeof tanishqRate !== 'object') return rates;
  const normalizedBrand = tanishqRate.Brand === 'Candere' ? 'Kalyan' : tanishqRate.Brand;
  if (!normalizedBrand) return rates;

  const nextRates = rates.filter((rate) => {
    const brand = rate?.Brand === 'Candere' ? 'Kalyan' : rate?.Brand;
    return brand !== normalizedBrand;
  });

  nextRates.push({ ...tanishqRate, Brand: normalizedBrand, _stale: false });
  return nextRates;
};

// ---------------------------------------------------------
// 2. The SWR Fetcher (The heavy lifter)
// ---------------------------------------------------------
const fetchLiveRates = async (url) => {
  console.log('[SWR] Fetching live rates...');
  const response = await fetch(url);
  if (!response.ok) throw new Error(`API returned ${response.status}`);
  const data = await response.json();

  // Load fallback cache for parsing errors
  let cachedMap = {};
  if (typeof window !== 'undefined') {
    try {
      const raw = window.localStorage.getItem('cached_gold_rates');
      if (raw) {
        const parsed = JSON.parse(raw);
        (Array.isArray(parsed?.rates) ? parsed.rates : []).forEach((r) => {
          if (r && r.Brand) cachedMap[r.Brand] = r;
        });
      }
    } catch (e) {
      console.warn('[SWR] Failed to read cached rates:', e);
    }
  }

  // Normalize
  let processedRates = normalizeLiveRates(data, cachedMap);

  // Handle Missing Tanishq On-Demand
  const hasTanishq = processedRates.some((r) => r.Brand === 'Tanishq');
  if (!hasTanishq) {
    try {
      console.log('[SWR] Tanishq missing, attempting on-demand fetch...');
      const tanishqRes = await fetch('/api/live-rates/fetch-tanishq');
      if (tanishqRes.ok) {
        const tanishqData = await tanishqRes.json();
        if (tanishqData.rate) {
          processedRates = mergeTanishqRate(processedRates, tanishqData.rate);
        }
      }
    } catch (e) {
      console.error('[SWR] Tanishq on-demand fetch error:', e);
    }
  }

  // Fire a background check if we know the data is from yesterday
  if (data.is_previous_day) {
    // Fire and forget—backend will trigger its own refresh task
    fetch('/api/live-rates/check').catch(() => {});
  }

  // Save successful fetch to cache
  if (typeof window !== 'undefined') {
    try {
      window.localStorage.setItem(
        'cached_gold_rates',
        JSON.stringify({
          rates: processedRates,
          last_updated: data.last_updated || new Date().toISOString(),
        })
      );
    } catch (e) {
      console.warn('[SWR] Failed to write cached rates:', e);
    }
  }

  return {
    rates: processedRates,
    cacheStatus: data.cache_status || 'live',
    lastUpdated: data.last_updated || new Date().toLocaleString(),
    isPreviousDay: Boolean(data.is_previous_day),
  };
};

// ---------------------------------------------------------
// 3. The Hook
// ---------------------------------------------------------
export const useLiveRates = () => {
  const { data, error, isLoading, isValidating } = useSWR('/api/live-rates', fetchLiveRates, {
    // 🔥 If the data is from yesterday, poll every 10 seconds.
    // Once backend saves fresh rates, isPreviousDay becomes false, and polling drops to 0 (stops).
    refreshInterval: (currentData) => {
      if (currentData?.isPreviousDay) {
        return 10000; 
      }
      return 0;
    },
    
    // 🔥 Re-fetch transparently in background when user switches back to this browser tab
    revalidateOnFocus: true,
    
    // Keep the old UI populated (don't flash loading states) while background polling happens
    keepPreviousData: true,
  });

  return {
    liveRates: data?.rates || [],
    loading: isLoading,
    cacheStatus: data?.cacheStatus || 'loading',
    lastUpdated: data?.lastUpdated || null,
    isPreviousDay: data?.isPreviousDay || false,
    
    // Optional extras exposed by SWR:
    isError: !!error,
    isBackgroundUpdating: isValidating, // True if SWR is silently checking for new data
  };
};