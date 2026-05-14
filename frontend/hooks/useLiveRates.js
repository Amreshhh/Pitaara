'use client';

import { useState, useEffect } from 'react';

export const useLiveRates = () => {
  const [liveRates, setLiveRates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cacheStatus, setCacheStatus] = useState('loading');
  const [lastUpdated, setLastUpdated] = useState(null);

  const normalizeLiveRates = (payload) => {
    const rates = Array.isArray(payload?.rates) ? payload.rates : Array.isArray(payload) ? payload : null;
    if (!Array.isArray(rates) || !rates.length) {
      throw new Error('Invalid live rates payload');
    }

    return rates.map((rate) => {
      if (!rate || typeof rate !== 'object') {
        throw new Error('Invalid live rates row');
      }

      // Handle both old "Candere" and new "Kalyan" brand names (backward compatibility)
      const brandName = rate.Brand === 'Candere' ? 'Kalyan' : rate.Brand;
      const normalized = { ...rate, Brand: brandName };
      const hasAnyNumericRate = ['24K', '22K', '18K', '14K'].some((key) => Number.isFinite(Number(normalized[key])));

      if (!brandName || !hasAnyNumericRate) {
        throw new Error('Unable to parse live rate values');
      }

      return normalized;
    });
  };

  useEffect(() => {
    let retryTimer = null;
    let isMounted = true;

    const scheduleRetry = (ms) => {
      if (retryTimer) clearTimeout(retryTimer);
      retryTimer = setTimeout(() => {
        if (isMounted) fetchRates();
      }, ms);
    };

    const fetchRates = async () => {
      try {
        console.log('[useLiveRates] Fetching live rates...');
        const response = await fetch('/api/live-rates');
        
        if (!response.ok) {
          throw new Error(`API returned ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('[useLiveRates] Received data:', data);
        
        const processedRates = normalizeLiveRates(data);
        console.log('[useLiveRates] Processed rates:', processedRates);

        if (isMounted) {
          setLiveRates(processedRates);
          setCacheStatus(data.cache_status || 'live');
          setLastUpdated(data.last_updated || new Date().toLocaleString());
        }

        // After loading stored payload, call checker to see if any brand is missing
        try {
          const chk = await fetch('/api/live-rates/check');
          if (chk && chk.ok) {
            const chkJson = await chk.json();
            // If checker indicates missing brands or missing rates, retry after 5 minutes
            if (chkJson.needs_fetch === true || (Array.isArray(chkJson.missing_brands) && chkJson.missing_brands.length > 0)) {
              // Keep displaying stored payload; schedule retry in 5 minutes
              console.log('[useLiveRates] Checker found missing data, scheduling retry in 5 min');
              scheduleRetry(5 * 60 * 1000);
            }
          }
        } catch (e) {
          // Checker failed — try again later
          console.warn('[useLiveRates] Checker failed:', e);
          scheduleRetry(5 * 60 * 1000);
        }
      } catch (error) {
        console.error('[useLiveRates] Failed to fetch live rates:', error);
        if (isMounted) {
          setLiveRates([]);
          setCacheStatus('error');
          setLastUpdated(null);
        }
        // On network error, retry after 5 minutes
        scheduleRetry(5 * 60 * 1000);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchRates();

    return () => {
      isMounted = false;
      if (retryTimer) clearTimeout(retryTimer);
    };
  }, []);

  return { liveRates, loading, cacheStatus, lastUpdated };
};