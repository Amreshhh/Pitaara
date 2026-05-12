'use client';

import { BrandCard } from './BrandCard';

export const BrandGrid = ({ results, isDarkMode, onBrandSelect ,weight,purity,category}) => {
  return (
    <div className="brand-grid grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 sm:gap-6">
      {results.map((item, index) => (
        <div
          key={item.id}
          style={{
            animation: `cardFadeUp 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards`,
            animationDelay: `${index * 0.1}s`,
            opacity: 0,
          }}
          className="animation-card-enter"
        >
          <BrandCard
            item={item}
            isDarkMode={isDarkMode}
            onSelect={onBrandSelect}
            weight={weight}
            purity={purity}
            category={category}
            logoUrl= 'https://theprint.in/wp-content/uploads/2022/01/Malabar-Logo.jpg' // URL of the image
            iconColor= 'text-orange-500'
          />
        </div>
      ))}
    </div>
  );
};
