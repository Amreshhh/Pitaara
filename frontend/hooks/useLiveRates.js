'use client';

import { useState, useEffect } from 'react';

export const useLiveRates = () => {
  const [liveRates, setLiveRates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cacheStatus, setCacheStatus] = useState('loading');
  const [lastUpdated, setLastUpdated] = useState(null);

  const FALLBACK_RATE_24K = 14620;

  const buildFallbackRates = () => {
    const brands = ['Tanishq', 'Kalyan(Candere)', 'Malabar', 'Senco'];
    return brands.map((brand) => {
      const rate24K = FALLBACK_RATE_24K;
      return {
        Brand: brand,
        '24K': rate24K,
        '22K': Math.round(rate24K * (22 / 24)),
        '18K': Math.round(rate24K * (18 / 24)),
        '14K': Math.round(rate24K * (14 / 24)),
      };
    });
  };

  const loadCachedRates = () => {
    try {
      const cached = localStorage.getItem('cached_gold_rates');
      if (!cached) {
        return null;
      }

      const cachedData = JSON.parse(cached);
      const rates = Array.isArray(cachedData) ? cachedData : cachedData?.rates;
      if (!Array.isArray(rates)) {
        return null;
      }

      return {
        rates,
        last_updated: cachedData?.last_updated || null,
      };
    } catch {
      return null;
    }
  };

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
    const fetchRates = async () => {
      const cachedData = loadCachedRates();
      const fallbackRates = cachedData?.rates?.length ? cachedData.rates : buildFallbackRates();

      for (let attempt = 1; attempt <= 3; attempt += 1) {
        try {
          // Use Next.js API proxy route (works on mobile, handles CORS)
          const response = await fetch('/api/live-rates');
          if (!response.ok) throw new Error('Network response was not ok');

          const data = await response.json();
          const processedRates = normalizeLiveRates(data);

          setLiveRates(processedRates);
          setCacheStatus(data.cache_status || 'active');
          setLastUpdated(data.last_updated || new Date().toLocaleString());

          localStorage.setItem('cached_gold_rates', JSON.stringify({
            rates: processedRates,
            last_updated: data.last_updated || new Date().toLocaleString(),
            timestamp: Date.now(),
          }));

          setLoading(false);
          return;
        } catch (error) {
          console.error(`Failed to fetch live rates (attempt ${attempt}/3):`, error);
          setLiveRates(fallbackRates);
          setLastUpdated(cachedData?.last_updated || null);
          setCacheStatus(attempt < 3 ? `fallback - retry ${attempt}/2` : 'fallback - no live rates');

          if (attempt < 3) {
            continue;
          }
        }
      }

      setLoading(false);
    };

    fetchRates();
  }, []);

  return { liveRates, loading, cacheStatus, lastUpdated };
};