// Powered by geinni 3.5 falsh
'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { X } from 'lucide-react';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, Title, Tooltip, Legend } from 'chart.js';
import { Scatter } from 'react-chartjs-2';
import { getThemeStyles } from '@/lib/utils';

ChartJS.register(CategoryScale, LinearScale, PointElement, Title, Tooltip, Legend);

export const BrandModal = ({ selectedBrand, isDarkMode, onClose, queryContext }) => {
  const styles = getThemeStyles(isDarkMode);
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState('');
  const hasBrand = Boolean(selectedBrand && selectedBrand.breakdown);
  const isCoinCategory = queryContext?.category === 'coin';

  // Memoize parseRange to prevent recreating on every render
  const parseRange = useCallback((rangeValue) => {
    if (typeof rangeValue !== 'string') return null;
    const parts = rangeValue.split('-').map((p) => p.trim());
    if (parts.length < 2) return null;
    const [minRaw, maxRaw] = parts;
    const min = Number(minRaw);
    const max = Number(maxRaw);
    if (!Number.isFinite(min) || !Number.isFinite(max)) return null;
    return { min, max };
  }, []);

  // Memoize selectedRange to prevent recreating on every render
  const selectedRange = useMemo(() => {
    return parseRange(queryContext?.weightRange || queryContext?.weight);
  }, [queryContext?.weightRange, queryContext?.weight, parseRange]);

  // Derive numeric target weight robustly: if weight is a range string, parse its min
  const targetWeight = useMemo(() => {
    const rawWeight = queryContext?.weight;
    if (typeof rawWeight === 'number') {
      return Number(rawWeight) || 0;
    } else if (typeof rawWeight === 'string') {
      const maybeRange = rawWeight.split('-');
      const parsed = Number(maybeRange[0]);
      return Number.isFinite(parsed) ? parsed : 0;
    }
    return 0;
  }, [queryContext?.weight]);

  // Extract display weight (minimum for coins, actual weight for others)
  const getDisplayWeight = useCallback(() => {
    if (isCoinCategory && selectedRange) {
      return selectedRange.min;
    }
    return targetWeight;
  }, [isCoinCategory, selectedRange, targetWeight]);

  const apiBrand = useMemo(() => {
    if (!selectedBrand?.name) {
      return '';
    }
    if (selectedBrand.name === 'Kalyan(Candere)') {
      return 'Kalyan';
    }
    return selectedBrand.name;
  }, [selectedBrand?.name]);

  useEffect(() => {
    if (!hasBrand || !apiBrand) {
      return;
    }

    // Create abort controller to cancel previous requests
    const abortController = new AbortController();

    const fetchSummary = async () => {
      setLoading(true);
      setError('');
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${baseUrl}/api/brand-summary`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          signal: abortController.signal,
          body: JSON.stringify({
            brand: apiBrand,
            weight: isCoinCategory && selectedRange ? selectedRange.min : targetWeight,
            weight_range: isCoinCategory ? (queryContext?.weightRange || queryContext?.weight) : null,
            purity: queryContext.purity,
            category: queryContext.category,
          }),
        });

        if (!response.ok) {
          throw new Error('Unable to load brand summary');
        }

        const data = await response.json();
        setSummary(data);
      } catch (fetchError) {
        if (fetchError.name !== 'AbortError') {
          console.error(fetchError);
          const categoryName = queryContext.category?.charAt(0).toUpperCase() + queryContext.category?.slice(1).replace('_', ' ') || 'products';
          setError(`No ${categoryName} found in range.`);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();

    // Cleanup: abort previous request when effect reruns
    return () => abortController.abort();
  }, [
    apiBrand,
    hasBrand,
    isCoinCategory,
    queryContext.category,
    queryContext.purity,
    queryContext.weightRange,
    queryContext.weight,
    selectedRange,
    targetWeight,
  ]);

  const scatterData = summary?.scatter_points || [];
  const topDeals = summary?.top_5_deals || [];
  const distribution = summary?.frequency_distribution || [];
  const coinWeightSummary = summary?.coin_weight_summary || [];

  const xDomain = useMemo(() => {
    if (!scatterData.length) {
      if (isCoinCategory && selectedRange) {
        return [selectedRange.min - 0.2, selectedRange.max + 0.2];
      }
      return [targetWeight - 1, targetWeight + 1];
    }
    const weights = scatterData.map((point) => point.weight);
    const min = Math.min(...weights);
    const max = Math.max(...weights);
    return [Math.floor(min * 10) / 10 - 0.2, Math.ceil(max * 10) / 10 + 0.2];
  }, [isCoinCategory, scatterData, selectedRange, targetWeight]);

  const yDomain = useMemo(() => {
    if (!scatterData.length) {
      return [0, 30];
    }
    const values = scatterData.map((point) => point.mc);
    const min = Math.min(...values);
    const max = Math.max(...values);
    return [Math.max(0, Math.floor(min - 2)), Math.ceil(max + 2)];
  }, [scatterData]);

  // Compute a local, authoritative breakdown from API values to ensure UI consistency
  const computedBreakdown = useMemo(() => {
    const appliedRate = Number(selectedBrand?.breakdown?.appliedRate) || 0;
    const displayWeight = getDisplayWeight();

    const goldValue = Math.round((appliedRate * displayWeight) * 100) / 100;

    // makingPercent may be stored as fraction or percent in different places
    let makingPercent = 0;
    if (selectedBrand?.breakdown?.makingPercent !== undefined) {
      makingPercent = Number(selectedBrand.breakdown.makingPercent) || 0; // fraction (e.g. 0.15)
    } else if (selectedBrand?.breakdown?.making_charges_percentage !== undefined) {
      makingPercent = (Number(selectedBrand.breakdown.making_charges_percentage) || 0) / 100;
    } else if (selectedBrand?.lowest_making_charge_in_range?.lowest_making_charge) {
      makingPercent = (Number(selectedBrand.lowest_making_charge_in_range.lowest_making_charge) || 0) / 100;
    }

    const makingCharges = Math.round((goldValue * makingPercent) * 100) / 100;
    const subtotal = Math.round((goldValue + makingCharges) * 100) / 100;
    const gst = Math.round((subtotal * 0.03) * 100) / 100;
    const total = Math.round((subtotal + gst) * 100) / 100;

    return {
      appliedRate,
      displayWeight,
      goldValue,
      makingCharges,
      makingPercent,
      subtotal,
      gst,
      total,
    };
  }, [selectedBrand, getDisplayWeight]);

  // Derive the lowest making charge percentage (for display as percent)
  const mcPercentage = (computedBreakdown.makingPercent * 100).toFixed(1);

  if (!hasBrand) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-0 sm:p-4 bg-stone-950/60 backdrop-blur-sm animation-backdrop">
      <div
        className={`rounded-none sm:rounded-3xl shadow-2xl w-full h-full sm:h-auto sm:max-h-[92vh] max-w-6xl overflow-hidden animation-modal border ${styles.bgMain} ${styles.borderColor}`}
      >
        <div className="relative p-5 sm:p-8 overflow-hidden border-b border-stone-800/70">
          <div className={`absolute inset-0 bg-linear-to-br opacity-20 ${selectedBrand.accentColor}`}></div>
          <div className="relative z-10 flex justify-between items-start">
            <div>
              <h3 className="font-serif font-medium text-2xl sm:text-3xl mb-1">{selectedBrand.name} Summary</h3>
              <p className={`text-sm sm:text-base tracking-wide ${styles.textMuted}`}>
                Target {isCoinCategory && selectedRange ? `${selectedRange.min}g-${selectedRange.max}g` : `${targetWeight}g`}, {queryContext.purity}, {queryContext.category}
              </p>
            </div>
            <button
              onClick={onClose}
              className={`p-2 rounded-full transition-colors ${
                isDarkMode ? 'bg-stone-900 hover:bg-stone-800' : 'bg-white hover:bg-stone-100'
              }`}
              aria-label="Close modal"
            >
              <X size={20} className={styles.textMuted} />
            </button>
          </div>
        </div>

        <div className="px-4 sm:px-8 pb-6 sm:pb-8 pt-5 sm:pt-6 space-y-5 sm:space-y-6 h-[calc(100%-96px)] sm:h-auto max-h-[calc(100vh-96px)] sm:max-h-[78vh] overflow-y-auto">
          {loading ? (
            <div className={`rounded-2xl border p-8 text-sm animation-content ${styles.borderColor} ${styles.textMuted}`}
              style={{ animationDelay: '0.1s' }}
            >
              Loading brand summary...
            </div>
          ) : null}

          {!loading && error ? (
            <div 
              className="rounded-2xl border border-rose-500/40 bg-rose-500/10 p-6 text-sm text-rose-400 animation-content"
              style={{ animationDelay: '0.1s' }}
            >
              {error}
            </div>
          ) : null}

          {!loading && !error ? (
            <>
              <div className={`rounded-2xl border overflow-x-auto animation-content ${styles.borderColor}`}
                style={{ animationDelay: '0.15s' }}
              >
                <table className="w-full min-w-140 text-xs sm:text-sm">
                  <thead>
                    <tr className={`border-b ${styles.borderColor} ${isDarkMode ? 'bg-stone-900/50' : 'bg-stone-50'}`}>
                      <th className={`text-left py-3 px-3 sm:px-4 font-semibold uppercase text-[10px] sm:text-xs tracking-wider ${styles.textMuted}`}>
                        Product Details
                      </th>
                      <th className={`text-center py-3 px-3 sm:px-4 font-semibold uppercase text-[10px] sm:text-xs tracking-wider ${styles.textMuted}`}>
                        Rate
                      </th>
                      <th className={`text-center py-3 px-3 sm:px-4 font-semibold uppercase text-[10px] sm:text-xs tracking-wider ${styles.textMuted}`}>
                        Weight
                      </th>
                      <th className={`text-right py-3 px-3 sm:px-4 font-semibold uppercase text-[10px] sm:text-xs tracking-wider ${styles.textMuted}`}>
                        Value
                      </th>
                    </tr>
                  </thead>
                  <tbody className={`divide-y ${styles.borderColor}`}>
                    <tr>
                      <td className="py-3 sm:py-4 px-3 sm:px-4 font-medium">Gold Value</td>
                      <td className="py-3 sm:py-4 px-3 sm:px-4 text-center">₹{computedBreakdown.appliedRate.toLocaleString('en-IN')}/g</td>
                      <td className="py-3 sm:py-4 px-3 sm:px-4 text-center">{computedBreakdown.displayWeight}g</td>
                      <td className="py-3 sm:py-4 px-3 sm:px-4 text-right font-semibold relative group/tooltip cursor-help whitespace-nowrap">
                        ₹{computedBreakdown.goldValue.toLocaleString('en-IN')}
                        <div
                          className={`absolute bottom-full right-0 mb-2 hidden group-hover/tooltip:block w-max p-2 rounded text-[10px] shadow-lg z-20 ${isDarkMode ? 'bg-stone-800 text-stone-200' : 'bg-stone-800 text-stone-100'}`}
                        >
                          {computedBreakdown.displayWeight}g × ₹{computedBreakdown.appliedRate.toLocaleString('en-IN')}
                        </div>
                      </td>
                    </tr>

                    <tr className={`border-t ${styles.borderColor} ${isDarkMode ? 'bg-stone-500/5' : 'bg-stone-500/15'}`}>
                      <td className="py-3 sm:py-4 px-3 sm:px-4 font-medium">Making Charges</td>
                      <td className="py-3 sm:py-4 px-3 sm:px-4 text-center text-sm sm:text-base font-semibold text-stone-600 dark:text-stone-500 whitespace-nowrap" colSpan={2}>
                        <span className="text-base sm:text-lg font-bold">{mcPercentage}%</span> × ₹{computedBreakdown.goldValue.toLocaleString('en-IN')}
                      </td>
                      <td className="py-3 sm:py-4 px-3 sm:px-4 text-right font-semibold text-rose-500 whitespace-nowrap">
                        ₹{computedBreakdown.makingCharges.toLocaleString('en-IN')}
                      </td>
                    </tr>

                    <tr className={`border-t-2 ${styles.borderColor}`}>
                      <td className="py-3 sm:py-4 px-3 sm:px-4 font-medium">Sub Total</td>
                      <td className="py-3 sm:py-4 px-3 sm:px-4 text-center">-</td>
                      <td className="py-3 sm:py-4 px-3 sm:px-4 text-center text-xs sm:text-sm">
                        <div className="font-medium">{computedBreakdown.displayWeight}g</div>
                        <div className={`text-xs ${styles.textMuted}`}>Gross Wt.</div>
                      </td>
                      <td className="py-3 sm:py-4 px-3 sm:px-4 text-right font-semibold whitespace-nowrap">
                        ₹{computedBreakdown.subtotal.toLocaleString('en-IN')}
                      </td>
                    </tr>

                    <tr className={`border-t ${styles.borderColor}`}>
                      <td className="py-3 sm:py-4 px-3 sm:px-4 font-medium">GST</td>
                      {/* Here is the updated GST center cell spanning 2 columns */}
                      <td className="py-3 sm:py-4 px-3 sm:px-4 text-center text-xs sm:text-sm font-medium text-stone-500 whitespace-nowrap" colSpan={2}>
                        3% × ₹{computedBreakdown.subtotal.toLocaleString('en-IN')}
                      </td>
                      <td className="py-3 sm:py-4 px-3 sm:px-4 text-right font-semibold whitespace-nowrap">
                        ₹{computedBreakdown.gst.toLocaleString('en-IN')}
                      </td>
                    </tr>

                    <tr className={`border-t-2 ${styles.borderColor} font-serif text-lg`}>
                      <td className="py-3 sm:py-4 px-3 sm:px-4 font-bold">Grand Total</td>
                      <td className="py-3 sm:py-4 px-3 sm:px-4 text-center">-</td>
                      <td className="py-3 sm:py-4 px-3 sm:px-4 text-center">-</td>
                      <td className="py-3 sm:py-4 px-3 sm:px-4 text-right font-bold whitespace-nowrap">
                        ₹{computedBreakdown.total.toLocaleString('en-IN')}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* Remainder of modal graphs and distributions... */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className={`rounded-xl border p-4 animation-content ${styles.borderColor}`} style={{ animationDelay: '0.2s' }}>
                  <p className={`text-[11px] uppercase tracking-[0.2em] ${styles.textMuted}`}>Target</p>
                  <p className="text-2xl font-semibold mt-1">
                    {isCoinCategory && summary?.target_range
                      ? `${summary.target_range.min}g - ${summary.target_range.max}g`
                      : `${summary?.target_weight}g`}
                  </p>
                </div>
                <div className={`rounded-xl border p-4 animation-content ${styles.borderColor}`} style={{ animationDelay: '0.25s' }}>
                  <p className={`text-[11px] uppercase tracking-[0.2em] ${styles.textMuted}`}>Range</p>
                  <p className="text-2xl font-semibold mt-1">
                    {summary?.searched_range?.min}g - {summary?.searched_range?.max}g
                  </p>
                </div>
                <div className={`rounded-xl border p-4 animation-content ${styles.borderColor}`} style={{ animationDelay: '0.3s' }}>
                  <p className={`text-[11px] uppercase tracking-[0.2em] ${styles.textMuted}`}>Items</p>
                  <p className="text-2xl font-semibold mt-1">{summary?.total_items || 0}</p>
                </div>
              </div>

              <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                <div className={`rounded-2xl border p-4 animation-content ${styles.borderColor}`} style={{ animationDelay: '0.35s' }}>
                  <h4 className="text-lg font-semibold mb-3">Weight vs Making Charge</h4>
                  <div className="h-80 flex items-center justify-center">
                    {scatterData && scatterData.length > 0 ? (
                      <Scatter
                        data={{
                          datasets: [
                            {
                              label: 'Products',
                              data: scatterData.map((point) => ({ x: point.weight, y: point.mc })),
                              backgroundColor: isDarkMode ? 'rgba(96, 165, 250, 0.6)' : 'rgba(37, 99, 235, 0.6)',
                              borderColor: isDarkMode ? 'rgba(59, 130, 246, 1)' : 'rgba(29, 78, 216, 1)',
                              borderWidth: 1.5,
                              pointRadius: 5,
                              pointHoverRadius: 7,
                              tension: 0.1,
                            },
                          ],
                        }}
                        options={{
                          responsive: true,
                          maintainAspectRatio: false,
                          plugins: {
                            legend: {
                              display: true,
                              labels: {
                                color: isDarkMode ? '#d6d3d1' : '#374151',
                                font: { size: 12, weight: 500 },
                              },
                            },
                            tooltip: {
                              backgroundColor: isDarkMode ? '#1c1917' : '#ffffff',
                              titleColor: isDarkMode ? '#f5f5f4' : '#000000',
                              bodyColor: isDarkMode ? '#d6d3d1' : '#374151',
                              borderColor: isDarkMode ? '#44403c' : '#d6d3d1',
                              borderWidth: 1,
                              padding: 8,
                              displayColors: false,
                              callbacks: {
                                label: function (context) {
                                  return `Weight: ${context.parsed.x}g, MC: ${context.parsed.y}%`;
                                },
                              },
                            },
                          },
                          scales: {
                            x: {
                              type: 'linear',
                              position: 'bottom',
                              title: {
                                display: true,
                                text: 'Weight (g)',
                                color: isDarkMode ? '#d6d3d1' : '#374151',
                                font: { size: 12, weight: 600 },
                              },
                              ticks: {
                                color: isDarkMode ? '#d6d3d1' : '#374151',
                              },
                              grid: {
                                color: isDarkMode ? '#2f2f35' : '#e5e7eb',
                              },
                            },
                            y: {
                              title: {
                                display: true,
                                text: 'Making Charge (%)',
                                color: isDarkMode ? '#d6d3d1' : '#374151',
                                font: { size: 12, weight: 600 },
                              },
                              ticks: {
                                color: isDarkMode ? '#d6d3d1' : '#374151',
                              },
                              grid: {
                                color: isDarkMode ? '#2f2f35' : '#e5e7eb',
                              },
                            },
                          },
                        }}
                      />
                    ) : (
                      <p className={`text-sm ${styles.textMuted}`}>No weight/MC data available.</p>
                    )}
                  </div>
                </div>

                <div className={`rounded-2xl border p-4 ${styles.borderColor}`}>
                  <h4 className="text-lg font-semibold mb-3">
                    {isCoinCategory ? 'Coin Weight Summary' : 'Frequency Distribution by MC%'}
                  </h4>
                  <div className="space-y-3 max-h-80 overflow-y-auto pr-1">
                    {isCoinCategory ? (
                      coinWeightSummary.length ? (
                        coinWeightSummary.map((row) => (
                          <div key={`${row.weight}-${row.mc}`} className={`rounded-lg border px-4 py-3 ${styles.borderColor}`}>
                            <p className="text-sm font-medium">
                              {row.weight}g coin at {row.mc}%
                            </p>
                            <p className={`text-xs mt-1 ${styles.textMuted}`}>
                              {row.count} product{row.count > 1 ? 's' : ''}
                            </p>
                          </div>
                        ))
                      ) : (
                        <p className={`text-sm ${styles.textMuted}`}>No coin summary available for selected range.</p>
                      )
                    ) : (
                      distribution.length ? (
                        distribution.map((row) => (
                          <div key={row.mc_bucket} className={`rounded-lg border px-4 py-3 ${styles.borderColor}`}>
                            <p className="text-sm font-medium">
                              {row.count} products at {row.mc_bucket}% (appx)
                            </p>
                            <p className={`text-xs mt-1 ${styles.textMuted}`}>
                              [{row.sample_weights.map((value) => `${value}g`).join(', ')}]
                            </p>
                          </div>
                        ))
                      ) : (
                        <p className={`text-sm ${styles.textMuted}`}>No items found in selected range.</p>
                      )
                    )}
                  </div>
                </div>
              </div>

              <div className={`rounded-2xl border p-4 ${styles.borderColor}`}>
                <h4 className="text-lg font-semibold mb-3">Top 5 Deals (Lowest Making charge)</h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className={`border-b ${styles.borderColor}`}>
                        <th className="text-left py-2">Verification Link</th>
                        <th className="text-left py-2">Net Weight</th>
                        <th className="text-left py-2">Making charge %</th>
                      </tr>
                    </thead>
                    <tbody>
                      {topDeals.length ? (
                        topDeals.map((deal) => (
                          <tr key={`${deal.verification_link}-${deal.weight}-${deal.mc}`} className={`border-b ${styles.borderColor}`}>
                            <td className="py-2 pr-3 font-medium">
                              <a 
                              href={deal.verification_link} 
                              target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                               View Link
                              </a>
                              </td>
                            <td className="py-2 pr-3">{deal.weight}g</td>
                            <td className="py-2 text-emerald-500 font-semibold">{deal.mc}%</td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td className={`py-3 ${styles.textMuted}`} colSpan={3}>No deals available for this range.</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          ) : null}

          <div className="flex justify-end pt-2">
            <button
              onClick={onClose}
              className={`px-8 py-3 rounded-xl font-medium transition-all ${
                isDarkMode ? 'bg-stone-100 text-stone-900 hover:bg-white' : 'bg-stone-900 text-white hover:bg-stone-800'
              }`}
            >
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};