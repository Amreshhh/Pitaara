'use client';

import { getThemeStyles } from '@/lib/utils';

export const Disclaimer = ({ isDarkMode }) => {
  const styles = getThemeStyles(isDarkMode);

  return (
    <div className="mt-24 text-center pb-12">
      <p className={`text-xs max-w-2xl mx-auto leading-relaxed opacity-60 ${styles.textMuted}`}>
        <span className="font-bold">Disclaimer:</span> Sheetal hi Munni hai 
        Munni hi aditi hai
        aditi hi nisha hai
        par nisha munni hai 
      </p>
    </div>
  );
};
