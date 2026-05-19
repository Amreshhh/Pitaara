'use client';

import { useState, useEffect, useRef } from 'react';

// ---------------------------------------------------------
// 1. Helper Functions
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
        console.warn('[useLiveRates] Skipping brand due to parse failure', rate, e.message);
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
// 2. The Hook
// ---------------------------------------------------------
export const useLiveRates = () => {
  const [liveRates, setLiveRates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cacheStatus, setCacheStatus] = useState('loading');
  const [lastUpdated, setLastUpdated] = useState(null);
  const [isPreviousDay, setIsPreviousDay] = useState(false);
  const pollingIntervalRef = useRef(null);

  const fetchRates = async () => {
    try {
      console.log('[useLiveRates] Fetching live rates...');
      const response = await fetch('/api/live-rates');
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
          console.warn('[useLiveRates] Failed to read cached rates:', e);
        }
      }

      // Normalize
      let processedRates = normalizeLiveRates(data, cachedMap);

      // Handle Missing Tanishq On-Demand
      const hasTanishq = processedRates.some((r) => r.Brand === 'Tanishq');
      if (!hasTanishq) {
        try {
          console.log('[useLiveRates] Tanishq missing, attempting on-demand fetch...');
          const tanishqRes = await fetch('/api/live-rates/fetch-tanishq');
          if (tanishqRes.ok) {
            const tanishqData = await tanishqRes.json();
            if (tanishqData.rate) {
              processedRates = mergeTanishqRate(processedRates, tanishqData.rate);
            }
          }
        } catch (e) {
          console.error('[useLiveRates] Tanishq on-demand fetch error:', e);
        }
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
          console.warn('[useLiveRates] Failed to write cached rates:', e);
        }
      }

      setLiveRates(processedRates);
      setCacheStatus(data.cache_status || 'live');
      setLastUpdated(data.last_updated || new Date().toLocaleString());
      setIsPreviousDay(Boolean(data.is_previous_day));
      setLoading(false);
    } catch (error) {
      console.error('[useLiveRates] Fetch error:', error);
      // Try loading from localStorage as fallback
      if (typeof window !== 'undefined') {
        try {
          const cached = window.localStorage.getItem('cached_gold_rates');
          if (cached) {
            const parsed = JSON.parse(cached);
            setLiveRates(parsed.rates || []);
            setCacheStatus('offline-cache');
            setLastUpdated(parsed.last_updated || null);
          }
        } catch (e) {
          console.error('[useLiveRates] Failed to load from cache:', e);
        }
      }
      setLoading(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchRates();
  }, []);

  // Set up polling when displaying previous day rates
  useEffect(() => {
    // Clear any existing interval
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }

    // If showing previous day rates, poll every 10 seconds
    if (isPreviousDay) {
      console.log('[useLiveRates] Setting up 10s polling for fresh rates...');
      pollingIntervalRef.current = setInterval(() => {
        fetchRates();
      }, 10000);
    }

    // Cleanup on unmount
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, [isPreviousDay]);

  return {
    liveRates,
    loading,
    cacheStatus,
    lastUpdated,
    isPreviousDay,
  };
};