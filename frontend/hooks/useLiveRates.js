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

const addStaleFallbackBrands = (rates, cachedByBrand = {}, requiredBrands = []) => {
  const nextRates = [...rates];
  const presentBrands = new Set(nextRates.map((rate) => rate?.Brand));

  for (const brand of requiredBrands) {
    if (presentBrands.has(brand)) continue;
    if (!cachedByBrand[brand]) continue;
    nextRates.push({ ...cachedByBrand[brand], _stale: true });
    presentBrands.add(brand);
  }

  return nextRates;
};

const readCachedLiveRates = () => {
  if (typeof window === 'undefined') return null;

  try {
    const raw = window.localStorage.getItem('cached_gold_rates');
    if (!raw) return null;

    const parsed = JSON.parse(raw);
    const rates = Array.isArray(parsed?.rates) ? parsed.rates : [];
    if (!rates.length) return null;

    return {
      rates,
      last_updated: parsed.last_updated || null,
    };
  } catch (error) {
    console.warn('[useLiveRates] Failed to read cached rates:', error);
    return null;
  }
};

const shouldTriggerRetry = (missingBrands, lastUpdated) => {
  if (!Array.isArray(missingBrands) || missingBrands.length === 0) return false;

  const signature = `${lastUpdated || 'no-ts'}:${missingBrands.join(',')}`;
  const storageKey = 'live_rates_retry_signature';
  const now = Date.now();
  const cooldownMs = 60 * 1000;

  try {
    const raw = window.localStorage.getItem(storageKey);
    if (raw) {
      const cached = JSON.parse(raw);
      if (cached?.signature === signature && typeof cached?.lastTriggeredAt === 'number') {
        return now - cached.lastTriggeredAt > cooldownMs ? { signature, storageKey, now } : false;
      }
    }
  } catch (error) {
    console.warn('[useLiveRates] Retry signature check failed:', error);
  }

  return { signature, storageKey, now };
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
  const [hasMissingBrands, setHasMissingBrands] = useState(false);
  const pollingIntervalRef = useRef(null);
  const missingBrandsPollingRef = useRef(null);

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
      const baseRates = normalizeLiveRates(data, cachedMap);

      // Keep stale fallback values visible if the fresh payload is incomplete.
      const requiredBrands = ['Tanishq', 'Kalyan', 'Malabar', 'Senco'];
      const livePresentBrands = new Set(baseRates.map((r) => r.Brand));
      const displayRates = addStaleFallbackBrands(baseRates, cachedMap, requiredBrands);
      const displayedTanishq = displayRates.find((rate) => rate?.Brand === 'Tanishq');
      const tanishqIsStale = Boolean(displayedTanishq?._stale);
      const backendMissingBrands = requiredBrands.filter((brand) => !livePresentBrands.has(brand));

      // Update missing brands state to control background polling
      const currentlyHasMissing = backendMissingBrands.length > 0 || tanishqIsStale;
      setHasMissingBrands(currentlyHasMissing);

      if (currentlyHasMissing) {
        const retryBrands = backendMissingBrands.length > 0 ? backendMissingBrands : ['Tanishq'];
        console.log(`[useLiveRates] Missing/stale brands detected: ${retryBrands.join(', ')}`);

        // Trigger backend retry once per incomplete payload snapshot
        try {
          const retryState = shouldTriggerRetry(retryBrands, data.last_updated);
          if (retryState) {
            console.log('[useLiveRates] Triggering backend scrape retry...');
            const triggerRes = await fetch('/api/live-rates/fetch-tanishq', {
              cache: 'no-store',
            });
            const triggerResult = await triggerRes.json();
            console.log('[useLiveRates] Tanishq fetch result:', triggerResult);

            if (typeof window !== 'undefined') {
              window.localStorage.setItem(
                retryState.storageKey,
                JSON.stringify({ signature: retryState.signature, lastTriggeredAt: retryState.now })
              );
            }
          }

          console.log('[useLiveRates] Calling /api/live-rates/check for diagnostics...');
          const checkRes = await fetch('/api/live-rates/check');
          if (checkRes.ok) {
            const checkResult = await checkRes.json();
            console.log('[useLiveRates] Check result:', checkResult);
          }
        } catch (e) {
          console.error('[useLiveRates] Check endpoint error:', e);
        }
      }

      // Save successful fetch to cache
      if (typeof window !== 'undefined') {
        try {
          window.localStorage.setItem(
            'cached_gold_rates',
            JSON.stringify({
              rates: displayRates,
              last_updated: data.last_updated || new Date().toISOString(),
            })
          );
        } catch (e) {
          console.warn('[useLiveRates] Failed to write cached rates:', e);
        }
      }

      setLiveRates(displayRates);
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
    const cachedSnapshot = readCachedLiveRates();
    if (cachedSnapshot) {
      setLiveRates(cachedSnapshot.rates);
      setCacheStatus('stale-cache');
      setLastUpdated(cachedSnapshot.last_updated);
      setLoading(false);
    }

    fetchRates();
  }, []);

  // Set up polling for previous day rates
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

  // Set up polling for missing/stale brands (e.g., Tanishq being updated in background)
  useEffect(() => {
    // Clear any existing missing brands polling interval
    if (missingBrandsPollingRef.current) {
      clearInterval(missingBrandsPollingRef.current);
      missingBrandsPollingRef.current = null;
    }

    // If we have missing/stale brands, poll every 5 seconds to check for updates
    if (hasMissingBrands) {
      console.log('[useLiveRates] Setting up 5s polling for missing/stale brands...');
      missingBrandsPollingRef.current = setInterval(() => {
        console.log('[useLiveRates] Polling for missing/stale brand updates...');
        fetchRates();
      }, 5000);
    }

    // Cleanup on unmount or when missing brands change
    return () => {
      if (missingBrandsPollingRef.current) {
        clearInterval(missingBrandsPollingRef.current);
        missingBrandsPollingRef.current = null;
      }
    };
  }, [hasMissingBrands]);

  return {
    liveRates,
    loading,
    cacheStatus,
    lastUpdated,
    isPreviousDay,
  };
};