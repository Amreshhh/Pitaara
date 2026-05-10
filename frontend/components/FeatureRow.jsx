'use client';

import { TrendingUp, Store, Coins } from 'lucide-react';

const features = [
  {
    icon: TrendingUp,
    label: 'Live Rates',
    theme: {
      dark: 'bg-emerald-500/10 text-emerald-400 ring-emerald-500/20 group-hover:bg-emerald-500/20 group-hover:ring-emerald-500/40 group-hover:shadow-[0_0_15px_rgba(16,185,129,0.15)]',
      light: 'bg-emerald-100 text-emerald-600 ring-emerald-200 group-hover:bg-emerald-200 group-hover:ring-emerald-300',
    }
  },
  {
    icon: Store,
    label: 'Top Brands',
    theme: {
      dark: 'bg-amber-500/10 text-amber-400 ring-amber-500/20 group-hover:bg-amber-500/20 group-hover:ring-amber-500/40 group-hover:shadow-[0_0_15px_rgba(245,158,11,0.15)]',
      light: 'bg-amber-100 text-amber-600 ring-amber-200 group-hover:bg-amber-200 group-hover:ring-amber-300',
    }
  },
  {
    icon: Coins,
    label: 'Zero Hidden Cost',
    theme: {
      dark: 'bg-blue-500/10 text-blue-400 ring-blue-500/20 group-hover:bg-blue-500/20 group-hover:ring-blue-500/40 group-hover:shadow-[0_0_15px_rgba(59,130,246,0.15)]',
      light: 'bg-blue-100 text-blue-600 ring-blue-200 group-hover:bg-blue-200 group-hover:ring-blue-300',
    }
  },
];

export const FeatureRow = ({ isDarkMode }) => {
  // Brighten up the base text slightly so it doesn't get lost
  const textColor = isDarkMode ? 'text-stone-300' : 'text-stone-700';
  const textHoverColor = isDarkMode ? 'group-hover:text-white' : 'group-hover:text-stone-900';

  return (
    <div className="flex flex-wrap justify-center gap-8 md:gap-16 mt-24">
      {features.map((feature) => {
        const Icon = feature.icon;
        const themeClasses = isDarkMode ? feature.theme.dark : feature.theme.light;

        return (
          <div key={feature.label} className="group flex items-center gap-3 cursor-pointer">
            {/* Icon Container with glowing ring and hover scaling */}
            <div
              className={`p-2.5 rounded-full ring-1 transition-all duration-300 ease-out group-hover:scale-110 ${themeClasses}`}
            >
              <Icon size={18} strokeWidth={2.5} />
            </div>
            
            {/* Text with a slight brighten effect on hover */}
            <span
              className={`text-sm font-semibold tracking-wider uppercase transition-colors duration-300 ${textColor} ${textHoverColor}`}
            >
              {feature.label}
            </span>
          </div>
        );
      })}
    </div>
  );
};