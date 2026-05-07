'use client';

import { useState, useEffect } from 'react';

export const useLiveRates = () => {
  const [liveRates, setLiveRates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cacheStatus, setCacheStatus] = useState('loading');
  const [lastUpdated, setLastUpdated] = useState(null);

  const loadCachedRates = () => {
    const cached = localStorage.getItem('cached_gold_rates');
    if (!cached) {
      return null;
    }

    const cachedData = JSON.parse(cached);
    if (!Array.isArray(cachedData.rates)) {
      return null;
    }

    return cachedData;
  };

  useEffect(() => {
    const fetchRates = async () => {
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${baseUrl}/api/live-rates`); 
        if (!response.ok) throw new Error('Network response was not ok');
        
        const data = await response.json();
        
        // 🔥 Extract rates from nested response structure
        const rates = data.rates || data; // Fallback for older API format
        
        // 🔥 Rename Candere to Kalyan(Candere)
        const processedRates = rates.map(rate => ({
          ...rate,
          Brand: rate.Brand === "Candere" ? "Kalyan(Candere)" : rate.Brand
        }));
        
        setLiveRates(processedRates);
        setCacheStatus(data.cache_status || 'active');
        setLastUpdated(data.last_updated || new Date().toLocaleString());
        
        // 🔥 CACHE RATES IN LOCALSTORAGE for persistence
        localStorage.setItem('cached_gold_rates', JSON.stringify({
          rates: processedRates,
          last_updated: data.last_updated || new Date().toLocaleString(),
          timestamp: Date.now()
        }));
        
      } catch (error) { 
        console.error("Failed to fetch live rates:", error);
        
        // 🔥 TRY TO LOAD FROM LOCALSTORAGE (last cached data)
        try {
          const cachedData = loadCachedRates();
          if (cachedData) {
            setLiveRates(cachedData.rates);
            setLastUpdated(cachedData.last_updated);
            setCacheStatus('offline - using last cached rates');
            console.log('✅ Using cached rates from localStorage:', cachedData);
          } else {
            setLiveRates([]);
            setLastUpdated(null);
            setCacheStatus('offline - no cached rates');
            console.log('⚠️ Backend offline and no cached rates available');
          }
        } catch (parseError) {
          console.error("Error parsing cached rates:", parseError);
          setLiveRates([]);
          setLastUpdated(null);
          setCacheStatus('error - no cached rates');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchRates();
  }, []);

  return { liveRates, loading, cacheStatus, lastUpdated };
};