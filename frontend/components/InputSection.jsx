'use client';

import { ChevronDown, Gem, Filter } from 'lucide-react';
import { PURITY_FACTORS, CATEGORIES, SUBCATEGORIES, COIN_WEIGHT_OPTIONS } from '../lib/constants';
import { getThemeStyles } from '../lib/utils';
export const InputSection = ({ inputs, onInputChange, isDarkMode, categories = CATEGORIES, onFind, inputsDirty = false, isCalculating = false }) => {
  const styles = getThemeStyles(isDarkMode);
  const isCoinCategory = inputs.category === 'coin';

  return (
    <section
      className={`rounded-3xl border shadow-2xl p-6 md:p-10 mb-16 transition-all duration-500 ${styles.cardBg} ${styles.borderColor}`}
    >
      {/* Section Header */}
      <div className="flex items-center gap-3 mb-8">
        <div className={`h-8 w-1 rounded-full ${isDarkMode ? 'bg-cyan-500' : 'bg-amber-500'}`}></div>
        <h2 className="text-2xl font-serif font-medium">Configure Purchase</h2>
      </div>

      {/* Input Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
        {/* Weight Input */}
        <div className="group">
          <label className={`block text-xs font-bold uppercase tracking-wider mb-2 ${styles.textMuted}`}>
            Gold Weight
          </label>
          {isCoinCategory ? (
            <div
              className={`relative flex items-center border rounded-xl overflow-hidden transition-all duration-300 group-hover:border-stone-400 ${styles.borderColor} ${styles.inputBg}`}
            >
              <select
                name="weight"
                value={inputs.weight}
                onChange={onInputChange}
                className="w-full p-4 pr-10 outline-none font-serif text-lg bg-transparent appearance-none cursor-pointer z-10"
                aria-label="Coin weight range"
              >
                {COIN_WEIGHT_OPTIONS.map((option) => (
                  <option key={option.id} value={option.id} className={isDarkMode ? 'bg-stone-900' : 'bg-white'}>
                    {option.label}
                  </option>
                ))}
              </select>
              <ChevronDown className={`absolute right-4 pointer-events-none ${styles.textMuted}`} size={18} />
            </div>
          ) : (
            <div
              className={`flex items-center border rounded-xl overflow-hidden transition-all duration-300 group-hover:border-stone-400 ${styles.borderColor} ${styles.inputBg}`}
            >
              <input
                  type="Integer"
                name="weight"
                value={inputs.weight}
                onChange={onInputChange}
                  min={0}
                  max={200}
                  step={0.01}
                className="w-full p-4 outline-none font-serif text-lg bg-transparent"
                aria-label="Gold weight in grams"
              />
              <span className={`px-4 font-medium text-sm ${styles.textMuted}`}>grams</span>
            </div>
          )}
        </div>

        {/* Purity Select */}
        <div className="group relative">
          <label className={`block text-xs font-bold uppercase tracking-wider mb-2 ${styles.textMuted}`}>
            Purity
          </label>
          <div
            className={`relative flex items-center border rounded-xl overflow-hidden transition-all duration-300 group-hover:border-stone-400 ${styles.borderColor} ${styles.inputBg}`}
          >
            <select
              name="purity"
              value={inputs.purity}
              onChange={onInputChange}
              className="w-full p-4 pr-10 outline-none font-serif text-lg bg-transparent appearance-none cursor-pointer z-10"
              aria-label="Gold purity"
            >
              {Object.keys(PURITY_FACTORS).map((k) => (
                <option key={k} value={k} className={isDarkMode ? 'bg-stone-900' : 'bg-white'}>
                  {k}
                </option>
              ))}
            </select>
            <ChevronDown className={`absolute right-4 pointer-events-none ${styles.textMuted}`} size={18} />
          </div>
        </div>

        {/* Category Select */}
        <div className="group relative">
          <label className={`block text-xs font-bold uppercase tracking-wider mb-2 ${styles.textMuted}`}>
            Jewellery Type
          </label>
          <div
            className={`relative flex items-center border rounded-xl overflow-hidden transition-all duration-300 group-hover:border-stone-400 ${styles.borderColor} ${styles.inputBg}`}
          >
            <select
              name="category"
              value={inputs.category}
              onChange={onInputChange}
              className="w-full p-4 pr-10 outline-none font-serif text-lg bg-transparent appearance-none cursor-pointer z-10"
              aria-label="Jewellery category"
            >
              {categories.map((c) => (
                <option key={c.id} value={c.id} className={isDarkMode ? 'bg-stone-900' : 'bg-white'}>
                  {c.label}
                </option>
              ))}
            </select>
            <Gem className={`absolute right-4 pointer-events-none ${styles.textMuted}`} size={18} />
          </div>
        </div>

        {/* Sub-Category Select */}
        <div className="group relative">
          <label className={`block text-xs font-bold uppercase tracking-wider mb-2 ${styles.textMuted}`}>
            Complexity / Style
          </label>
          <div
            className={`relative flex items-center border rounded-xl overflow-hidden transition-all duration-300 group-hover:border-stone-400 ${styles.borderColor} ${styles.inputBg}`}
          >
            <select
              name="subcategory"
              value={inputs.subcategory}
              onChange={onInputChange}
              className="w-full p-4 pr-10 outline-none font-serif text-lg bg-transparent appearance-none cursor-pointer z-10"
              aria-label="Jewellery style"
            >
              {SUBCATEGORIES[inputs.category]?.map((s) => (
                <option key={s.id} value={s.id} className={isDarkMode ? 'bg-stone-900' : 'bg-white'}>
                  {s.label}
                </option>
              ))}
            </select>
            <Filter className={`absolute right-4 pointer-events-none ${styles.textMuted}`} size={18} />
          </div>
        </div>
      </div>
      <div className="mt-6 flex justify-center">
        <button
          type="button"
          onClick={onFind}
          disabled={isCalculating}
          className={`inline-flex items-center justify-center w-44 md:w-56 gap-2 px-6 py-3 rounded-xl text-white font-semibold shadow transition-all duration-150 disabled:opacity-75 disabled:cursor-not-allowed ${
            isCalculating
              ? 'bg-amber-600'
              : inputsDirty
              ? 'bg-amber-500 hover:bg-amber-600'
              : 'bg-amber-600 hover:bg-amber-700'
          }`}
        >
          {isCalculating ? (
            <>
              <svg
                className="w-5 h-5 animate-spin"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              <span>Calculating...</span>
            </>
          ) : (
            'FIND'
          )}
        </button>
      </div>
    </section>
  );
};
