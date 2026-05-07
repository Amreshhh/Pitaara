'use client';

import { TrendingUp, Store, Coins } from 'lucide-react';

const features = [
  { icon: TrendingUp, label: 'Live Rates' },
  { icon: Store, label: 'Top Brands' },
  { icon: Coins, label: 'Zero Hidden Cost' },
];

export const FeatureRow = ({ isDarkMode }) => {
  const textMuted = isDarkMode ? 'text-stone-500' : 'text-stone-400';
  const bgIcon = isDarkMode ? 'bg-stone-900' : 'bg-stone-100';

  return (
    <div className={`flex flex-wrap justify-center gap-8 md:gap-16 mt-24 transition-colors duration-500 ${textMuted}`}>
      {features.map((feature) => {
        const Icon = feature.icon;
        return (
          <div key={feature.label} className="flex items-center gap-3">
            <div className={`p-2 rounded-full ${bgIcon}`}>
              <Icon size={16} />
            </div>
            <span className="text-sm font-medium tracking-wide uppercase">{feature.label}</span>
          </div>
        );
      })}
    </div>
  );
};
