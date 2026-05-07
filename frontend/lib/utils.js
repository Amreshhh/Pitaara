/**
 * Formats a number as Indian currency (INR)
 */
export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);
};

/**
 * Formats a decimal value as percentage string
 */
export const formatPercent = (val) => `${(val * 100).toFixed(1)}%`;

export const calculatePrice = async (weight, purity) => {
  try {
    const res = await fetch(
      `http://127.0.0.1:8000/calculate?weight=${weight}&purity=${purity}`
    );

    const data = await res.json();
    return data;
  } catch (error) {
    console.error("API error:", error);
    return null;
  }
};

/**
 * Common theme-related style classes for consistency
 */
export const getThemeStyles = (isDarkMode) => ({
  bgMain: isDarkMode ? 'bg-stone-950' : 'bg-stone-50',
  textMain: isDarkMode ? 'text-stone-100' : 'text-stone-800',
  textMuted: isDarkMode ? 'text-stone-400' : 'text-stone-500',
  cardBg: isDarkMode ? 'bg-stone-900/60 backdrop-blur-md' : 'bg-white/80 backdrop-blur-md',
  borderColor: isDarkMode ? 'border-stone-800' : 'border-stone-200',
  inputBg: isDarkMode ? 'bg-stone-950/50' : 'bg-stone-50',
  headerBg: isDarkMode ? 'bg-stone-950/80' : 'bg-white/80',
});
