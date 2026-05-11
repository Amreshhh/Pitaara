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
    const fetchRates = async () => {
      try {
        const response = await fetch('/api/live-rates');
        if (!response.ok) throw new Error('Network response was not ok');

        const data = await response.json();
        const processedRates = normalizeLiveRates(data);

        setLiveRates(processedRates);
        setCacheStatus(data.cache_status || 'live');
        setLastUpdated(data.last_updated || new Date().toLocaleString());
      } catch (error) {
        console.error('Failed to fetch live rates:', error);
        setLiveRates([]);
        setCacheStatus('error');
        setLastUpdated(null);
      }

      setLoading(false);
    };

    fetchRates();
  }, []);

  return { liveRates, loading, cacheStatus, lastUpdated };
};