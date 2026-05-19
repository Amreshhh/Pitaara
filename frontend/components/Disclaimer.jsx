'use client';

import { getThemeStyles } from '@/lib/utils';

export const Disclaimer = ({ isDarkMode }) => {
  const styles = getThemeStyles(isDarkMode);

  return (
    <div className="mt-24 text-center pb-12">
      <p className={`text-xs max-w-2xl mx-auto leading-relaxed opacity-60 ${styles.textMuted}`}>
        <span className="font-bold">Disclaimer:</span> The prices, making charges, and inventory shown on this website are representations of data collected from publicly available brand websites. While we aim to keep this information highly accurate and updated, actual in-store making charges and final billing values may vary slightly,still not more than 1-2%.
      </p>
    </div>
  );
};
