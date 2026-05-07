'use client';

import { BadgeIndianRupee, Info, ArrowRight } from 'lucide-react';
import { formatCurrency, formatPercent, getThemeStyles } from '@/lib/utils';

export const BrandCard = ({ item, isDarkMode, onSelect, weight, purity, category }) => {
  const styles = getThemeStyles(isDarkMode);
  
  // Format category name for display
  const categoryDisplayName = category
    ? category.charAt(0).toUpperCase() + category.slice(1).replace('_', ' ')
    : 'products';

  if (!item.breakdown) {
    return null;
  }

  return (
    <button
      type="button"
      className="group h-120 w-full cursor-pointer text-left"
      onClick={() => onSelect(item)}
      aria-label={`View summary for ${item.name}`}
    >
      <div
        className={`relative h-full w-full rounded-2xl border flex flex-col overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-1 ${styles.cardBg} ${item.borderColor}`}
      >
        <div className={`absolute inset-0 bg-linear-to-br opacity-50 ${item.accentColor}`}></div>

        <div className="relative z-10 flex flex-col h-full p-6">
          <div className="flex-1 flex flex-col items-center justify-center text-center">
            <div
              className={`w-16 h-16 rounded-full flex items-center justify-center mb-6 shadow-inner ${
                isDarkMode ? 'bg-stone-900' : 'bg-white'
              } ${item.iconColor}`}
            >
              <BadgeIndianRupee size={28} strokeWidth={1.5} />
            </div>
            <h3 className="font-serif font-medium text-3xl mb-3 tracking-tight">{item.name}</h3>
            <p className="text-[10px] font-bold uppercase tracking-[0.2em] opacity-60">{item.tagline}</p>
          </div>

          <div className={`py-6 border-t flex flex-col justify-end ${isDarkMode ? 'border-stone-800' : 'border-stone-200/60'}`}>
            {item.lowest_making_charge_in_range && (
              <div className={`mb-4 p-3 rounded-lg border-2 ${item.iconColor} bg-opacity-10 ${item.accentColor}`}>
                  <div className={`text-xs font-bold uppercase tracking-wide mb-1 ${isDarkMode ? item.iconColor : styles.textMain}`}>
                    Lowest Making Charge: {item.lowest_making_charge_in_range.lowest_making_charge}%
                  </div>
                  <div className={`text-[10px] opacity-80 ${styles.textMuted}`}>
                    (Available on {item.lowest_making_charge_in_range.product_count} items)
                  </div>
                </div>
            )}

            <div className="mb-4 flex flex-col justify-center">
              {item.metadata.isEmpty ? (
                <div className={`text-xs text-center border border-rose-500/30 bg-rose-500/10 p-2 rounded-lg ${
                  isDarkMode ? 'text-rose-500' : 'text-rose-700'
                }`}>
                  No {categoryDisplayName} found in range <br /> ({item.metadata.searchMin}g - {item.metadata.searchMax}g)
                </div>
              ) : null}
            </div>

            <div className={`text-xs font-bold uppercase tracking-wider mb-1 ${styles.textMuted}`}>
              Est. Average Price
            </div>
            <div className={`text-4xl font-sans font-normal tracking-tight ${item.metadata.isEmpty ? 'opacity-30' : ''}`}>
              {item.metadata.isEmpty ? 'N/A' : formatCurrency(item.breakdown.total)}
            </div>
          </div>

          <div className={`mt-3 flex items-center justify-center gap-2 text-xs font-medium ${styles.textMuted}`}>
            <span>Click to view summary</span>
            <ArrowRight size={12} />
          </div>

          <div className={`mt-4 pt-4 border-t ${isDarkMode ? 'border-stone-800' : 'border-stone-200/60'} space-y-3 text-sm`}>
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-1 relative group/tooltip cursor-help">
                <span className={`text-xs uppercase tracking-wide ${styles.textMuted}`}>Gold Value</span>
                <Info size={12} className={styles.textMuted} />
                <div
                  className={`absolute bottom-full left-0 mb-2 hidden group-hover/tooltip:block w-max max-w-50 p-2 rounded text-[10px] shadow-lg z-20 ${
                    isDarkMode ? 'bg-stone-800 text-stone-200' : 'bg-stone-800 text-stone-100'
                  }`}
                >
                  {weight}g × ₹{item.breakdown.appliedRate?.toLocaleString('en-IN')} ({purity} Rate)
                </div>
              </div>
              <span className="font-mono text-base">{formatCurrency(item.breakdown.goldValue)}</span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-xs uppercase tracking-wide text-rose-500">Making ({formatPercent(item.breakdown.makingPercent)})</span>
              <span className="font-mono text-base text-rose-500">+{formatCurrency(item.breakdown.makingCharges)}</span>
            </div>

            <div className={`h-px w-full my-1 ${styles.borderColor}`}></div>

            <div className="flex justify-between items-center">
              <span className={`text-xs uppercase tracking-wide ${styles.textMuted}`}>Before GST</span>
              <span className={`font-mono text-base ${styles.textMuted}`}>{formatCurrency(item.breakdown.subtotal)}</span>
            </div>

            <div className="flex justify-between items-center">
              <span className={`text-xs uppercase tracking-wide ${styles.textMuted}`}>GST (3%)</span>
              <span className={`font-mono text-base ${styles.textMuted}`}>+{formatCurrency(item.breakdown.gst)}</span>
            </div>

            <div className={`mt-auto pt-4 border-t ${styles.borderColor} flex justify-between items-end`}>
              <span className="text-xs font-bold uppercase">Total</span>
              <span className="font-mono text-xl font-bold">{formatCurrency(item.breakdown.total)}</span>
            </div>
          </div>
        </div>
      </div>
    </button>
  );
};
