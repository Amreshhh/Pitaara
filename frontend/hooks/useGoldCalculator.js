'use client';

import { useState, useEffect } from 'react';
import { BRANDS, CATEGORIES, PURITY_FACTORS } from '@/lib/constants';

const BRAND_UI = {
  'Tanishq': { accentColor: 'from-rose-500/20 to-rose-900/5', borderColor: 'border-rose-200/50 dark:border-rose-900/30', iconColor: 'text-rose-700 dark:text-rose-400', tagline: 'Premium Assurance' },
  'Kalyan': { accentColor: 'from-amber-500/20 to-amber-900/5', borderColor: 'border-amber-200/50 dark:border-amber-900/30', iconColor: 'text-amber-700 dark:text-amber-400', tagline: 'Trusted Legacy' },
  'Malabar': { accentColor: 'from-orange-500/20 to-orange-900/5', borderColor: 'border-orange-200/50 dark:border-orange-900/30', iconColor: 'text-orange-700 dark:text-orange-400', tagline: 'Fair Price Promise' },
  'Senco': { accentColor: 'from-yellow-500/20 to-yellow-900/5', borderColor: 'border-yellow-200/50 dark:border-yellow-900/30', iconColor: 'text-yellow-700 dark:text-yellow-400', tagline: "World's Favorite" }
};

export const useGoldCalculator = (inputs, trigger = 0) => {
  const [results, setResults] = useState([]);

  const buildFallbackResults = (numericWeight) => {
    const purityFactor = PURITY_FACTORS[inputs.purity] || 0.916;
    const perGramRate = Math.round((Number(inputs.rate) || 14620) * purityFactor);
    const categoryMod = CATEGORIES.find((c) => c.id === inputs.category)?.baseChargeMod || 0;

    return BRANDS.map((brand, index) => {
      const makingPercent = Math.max(0.01, (brand.baseMaking || 0.12) + categoryMod);
      const goldValue = Math.round(perGramRate * numericWeight);
      const makingCharges = Math.round(goldValue * makingPercent);
      const subtotal = goldValue + makingCharges;
      const gst = Math.round(subtotal * 0.03);
      const total = subtotal + gst;

      const uiStyles = BRAND_UI[brand.name === 'Kalyan(Candere)' ? 'Kalyan' : brand.name] || BRAND_UI.Kalyan;

      return {
        id: index + 1,
        name: brand.name,
        ...uiStyles,
        breakdown: {
          appliedRate: perGramRate,
          goldValue,
          makingCharges,
          makingPercent,
          wastageCharges: 0,
          subtotal,
          gst,
          total,
        },
        metadata: {
          isEmpty: false,
          count: 0,
          minMaking: makingPercent * 100,
          minWeight: numericWeight,
          maxMaking: makingPercent * 100,
          maxWeight: numericWeight,
          searchMin: numericWeight,
          searchMax: numericWeight,
          fallback: true,
        },
        lowest_making_charge_in_range: {
          lowest_making_charge: (makingPercent * 100).toFixed(1),
          product_count: 0,
        },
      };
    });
  };

  const parseRangeMin = (rangeValue) => {
    if (typeof rangeValue !== 'string') return null;
    const [minRaw] = rangeValue.split('-');
    const min = parseFloat(minRaw);
    return Number.isFinite(min) ? min : null;
  };

  useEffect(() => {
    // Only run when the external trigger increments
    const fetchCalculation = async () => {
      try {
        const isCoin = inputs.category === 'coin';
        const numericWeight = isCoin ? parseRangeMin(inputs.weight) : parseFloat(inputs.weight);

        if (!numericWeight || numericWeight <= 0) {
          setResults([]);
          return;
        }

        const payload = {
          weight: numericWeight,
          purity: inputs.purity,
          jewellery_type: inputs.category,
          metal_type: 'Gold',
          weight_range: isCoin ? String(inputs.weight) : null,
        };
        const response = await fetch('/api/calculate-price', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });

        if (!response.ok) throw new Error('API Calculation failed');
        const data = await response.json();

        const mappedResults = data.results.map((item, index) => {
          const uiStyles = BRAND_UI[item.brand] || BRAND_UI['Kalyan'];
          
          return {
            id: index + 1,
            name: item.brand === 'Kalyan' ? 'Kalyan(Candere)' : item.brand,
            ...uiStyles,
            breakdown: {
              appliedRate: item.per_gram_rate,
              goldValue: item.gold_value,
              makingCharges: item.making_charges,
              makingPercent: item.making_charges_percentage / 100, 
              wastageCharges: 0,
              subtotal: item.subtotal,
              gst: item.gst,
              total: item.total_estimated_price
            },
            metadata: {
              isEmpty: item.is_empty,
              count: item.db_product_count,
              minMaking: item.making_min_percent,
              minWeight: item.min_weight_found,
              maxMaking: item.making_max_percent,
              maxWeight: item.max_weight_found,
              searchMin: item.searched_min_w,
              searchMax: item.searched_max_w
            },
            // 🔥 NEW: Lowest making charge in range
            lowest_making_charge_in_range: item.lowest_making_charge_in_range || null
          };
        });

        setResults(mappedResults);
      } catch (error) {
        console.error("Error fetching calculation:", error);
        // Fallback keeps brand cards visible even if backend API is down.
        setResults(buildFallbackResults(numericWeight));
      }
    };

    // Trigger the calculation when 'trigger' changes
    if (trigger && Number.isFinite(trigger)) {
      const timeoutId = setTimeout(() => fetchCalculation(), 100);
      return () => clearTimeout(timeoutId);
    }
    // if trigger is 0 or falsy, clear results
    setResults([]);
  }, [trigger]);

  return results; 
};