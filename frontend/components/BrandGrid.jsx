'use client';

import { BrandCard } from './BrandCard';

export const BrandGrid = ({ results, isDarkMode, onBrandSelect ,weight,purity,category}) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {results.map((item) => (
        <BrandCard
          key={item.id}
          item={item}
          isDarkMode={isDarkMode}
          onSelect={onBrandSelect}
          weight={weight}
          purity={purity}
          category={category}
          logoUrl= 'https://theprint.in/wp-content/uploads/2022/01/Malabar-Logo.jpg' // URL of the image
          iconColor= 'text-orange-500'
        />
      ))}
    </div>
  );
};
