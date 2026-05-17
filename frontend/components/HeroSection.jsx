  'use client';

  import { ArrowDown } from 'lucide-react';
  import { getThemeStyles } from '../lib/utils';
  import { FeatureRow } from './FeatureRow';

  const RoyalWheel = () => (
    <svg viewBox="0 0 500 500" className="w-full h-full animate-[spin_60s_linear_infinite]">
      <defs>
        <linearGradient id="gold-base" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#bf953f" />
          <stop offset="25%" stopColor="#fcf6ba" />
          <stop offset="50%" stopColor="#b38728" />
          <stop offset="75%" stopColor="#fbf5b7" />
          <stop offset="100%" stopColor="#aa771c" />
        </linearGradient>
        <linearGradient id="gold-dark" x1="100%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#593b0b" />
          <stop offset="50%" stopColor="#b38728" />
          <stop offset="100%" stopColor="#301f05" />
        </linearGradient>
        <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="3" result="blur" />
          <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>

        <g id="petal">
          <path d="M 250 180 Q 265 200 250 215 Q 235 200 250 180" fill="url(#gold-base)" stroke="url(#gold-dark)" strokeWidth="1.5" />
        </g>

        <g id="spoke">
          <rect x="244" y="55" width="12" height="135" fill="url(#gold-base)" stroke="url(#gold-dark)" strokeWidth="1" />
          <path d="M 235 190 L 265 190 L 255 160 L 245 160 Z" fill="url(#gold-dark)" />
          <path d="M 235 55 L 265 55 L 252 80 L 248 80 Z" fill="url(#gold-dark)" />
          <rect x="240" y="95" width="20" height="10" fill="url(#gold-dark)" rx="3" />
          <rect x="242" y="125" width="16" height="6" fill="url(#gold-dark)" rx="2" />
          <rect x="240" y="150" width="20" height="8" fill="url(#gold-dark)" rx="3" />
          <circle cx="250" cy="100" r="3" fill="url(#gold-base)" />
        </g>
      </defs>

      <circle cx="250" cy="250" r="240" fill="none" stroke="url(#gold-dark)" strokeWidth="16" filter="url(#glow)" />
      <circle cx="250" cy="250" r="228" fill="none" stroke="url(#gold-base)" strokeWidth="10" />
      <circle cx="250" cy="250" r="212" fill="none" stroke="url(#gold-base)" strokeWidth="12" strokeDasharray="4 16" strokeLinecap="round" />
      <circle cx="250" cy="250" r="202" fill="none" stroke="url(#gold-dark)" strokeWidth="4" />
      <circle cx="250" cy="250" r="192" fill="none" stroke="url(#gold-base)" strokeWidth="6" />

      {Array.from({ length: 16 }).map((_, i) => (
        <use key={`spoke-${i}`} href="#spoke" transform={`rotate(${i * 22.5} 250 250)`} />
      ))}

      <circle cx="250" cy="250" r="75" fill="url(#gold-dark)" filter="url(#glow)" />
      <circle cx="250" cy="250" r="68" fill="url(#gold-base)" />

      {Array.from({ length: 16 }).map((_, i) => (
        <use key={`petal-${i}`} href="#petal" transform={`rotate(${i * 22.5} 250 250)`} />
      ))}

      <circle cx="250" cy="250" r="48" fill="url(#gold-dark)" />
      <circle cx="250" cy="250" r="40" fill="url(#gold-base)" />
      <circle cx="250" cy="250" r="30" fill="none" stroke="url(#gold-dark)" strokeWidth="4" strokeDasharray="3 3" />
      <circle cx="250" cy="250" r="20" fill="url(#gold-dark)" />
      <circle cx="250" cy="250" r="12" fill="url(#gold-base)" />
      <circle cx="250" cy="250" r="4" fill="url(#gold-dark)" />
    </svg>
  );

  const GoldFlourish = ({ mirrored = false }) => (
    <svg
      viewBox="0 0 220 70"
      className={`w-24 h-8 md:w-32 md:h-10 ${mirrored ? 'scale-x-[-1]' : ''}`}
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="flourish-gold" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#9b6b16" />
          <stop offset="40%" stopColor="#f3d36a" />
          <stop offset="70%" stopColor="#fff0a5" />
          <stop offset="100%" stopColor="#a46d15" />
        </linearGradient>
      </defs>

      <path
        d="M8 52 C34 24, 66 15, 110 26 C135 32, 165 30, 205 12"
        fill="none"
        stroke="url(#flourish-gold)"
        strokeWidth="5"
        strokeLinecap="round"
      />
      <path
        d="M48 35 C66 28, 78 14, 82 8 C90 22, 81 34, 67 36"
        fill="none"
        stroke="url(#flourish-gold)"
        strokeWidth="4"
        strokeLinecap="round"
      />
      <path
        d="M84 34 C95 30, 105 18, 109 12 C116 24, 111 35, 99 38"
        fill="none"
        stroke="url(#flourish-gold)"
        strokeWidth="3.5"
        strokeLinecap="round"
      />
    </svg>
  );

  export const HeroSection = ({
    isDarkMode,
    onScrollToEstimator,
    liveRates = [],
    loading = false,
    heading = 'Pitaara',
    eyebrow = 'by',
    brandLine = 'Om-Rani',
    subheading = 'Find the best value. Compare live gold rates and making charges across India\'s leading jewelry brands.',
  }) => {
    const styles = getThemeStyles(isDarkMode);

    return (
      <section className="hero-section relative min-h-[10vh] flex flex-col items-center justify-center overflow-hidden px-4 text-center">
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div
            className={`absolute top-[-5%] left-1/2 -translate-x-1/2 w-225 md:w-300 h-200 rounded-full blur-[150px] opacity-40 transition-colors duration-700 ${isDarkMode ? 'bg-cyan-800/50' : 'bg-amber-200/70'}`}
          ></div>
          <div
            className={`absolute bottom-0 right-0 w-100 h-100 rounded-full blur-[100px] opacity-20 transition-colors duration-700 ${isDarkMode ? 'bg-purple-900/20' : 'bg-orange-100'}`}
          ></div>
        </div>

        <div className="max-w-5xl mx-auto relative z-10 flex flex-col items-center">
          <div className="relative flex flex-col items-center justify-center w-full my-40">
            <div className="hero-wheel absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-87.5 h-87.5 md:w-137.5 md:h-137.5 pointer-events-none opacity-50 dark:opacity-40">
              <RoyalWheel />
            </div>

            <div
              className={`relative z-10 w-24 h-px mb-8 transition-colors duration-500 ${isDarkMode ? 'bg-linear-to-r from-transparent via-cyan-500 to-transparent' : 'bg-linear-to-r from-transparent via-amber-600 to-transparent'}`}
            ></div>

            <h1 className="relative z-10 font-serif tracking-tight mb-8 leading-[1.1] text-center">
              <span
                className="text-8xl md:text-9xl leading-none block mb-6 drop-shadow-xl"
                style={{ fontFamily: "'Samarkan', sans-serif", fontWeight: 'normal' }}
              >
                {heading}
              </span>
              <span className={`text-3xl md:text-3xl italic font-light drop-shadow-md ${isDarkMode ? 'text-amber-100/90' : 'text-amber-800/90'}`}>
                {eyebrow}
              </span>
              <span className={`text-3xl md:text-5xl italic font-light drop-shadow-md ${isDarkMode ? 'text-amber-100/90' : 'text-amber-800/90'}`}>
                {' '}
                {brandLine}
              </span>
            </h1>
          </div>

          <p className={`text-lg md:text-xl max-w-2xl mb-10 font-light leading-relaxed relative z-10 ${styles.textMuted}`}>
            {subheading}
          </p>

          <button
            onClick={onScrollToEstimator}
            className={`hidden sm:inline-flex group relative px-8 py-4 rounded-full overflow-hidden transition-all shadow-xl hover:shadow-2xl ${isDarkMode ? 'bg-stone-100 text-stone-900' : 'bg-stone-900 text-stone-100'}`}
          >
            <div className="absolute inset-0 w-full h-full opacity-0 group-hover:opacity-20 transition-opacity bg-linear-to-r from-transparent via-stone-400 to-transparent -skew-x-12 -translate-x-full group-hover:translate-x-full duration-1000"></div>
            <div className="relative flex items-center gap-3 font-medium tracking-wide">
              Start Estimating <ArrowDown size={18} className="group-hover:translate-y-1 transition-transform" />
            </div>
          </button>

          <div className="relative mt-16 mb-4 flex items-center justify-center gap-2 md:gap-6 w-screen -mx-4 px-4 md:px-8">
            <div className="absolute left-4 md:left-8 top-1/2 -translate-y-1/2 pointer-events-none opacity-90 z-10">
              <GoldFlourish />
            </div>

            <span className={`h-px flex-1 ${isDarkMode ? 'bg-amber-500/50' : 'bg-amber-700/40'}`}></span>
            <h2 className={`text-base md:text-lg font-semibold tracking-[0.22em] uppercase shrink-0 ${isDarkMode ? 'text-amber-300' : 'text-amber-800'}`}>
              Live Rates
            </h2>
            <span className={`h-px flex-1 ${isDarkMode ? 'bg-amber-500/50' : 'bg-amber-700/40'}`}></span>

            <div className="absolute right-4 md:right-8 top-1/2 -translate-y-1/2 pointer-events-none opacity-90 z-10">
              <GoldFlourish mirrored />
            </div>
          </div>

          <div className={`hero-rates-panel mt-3 w-screen -mx-4 overflow-hidden border-y backdrop-blur-md shadow-2xl transition-all duration-500 ${isDarkMode ? 'bg-stone-900/40 border-stone-800 shadow-black/50' : 'bg-white/60 border-stone-200 shadow-stone-200/50'}`}>
            {/* Mobile: stacked cards */}
            <div className="block sm:hidden px-4 py-4 space-y-3">
              {loading ? (
                <div className="animate-pulse text-center py-6">
                  <span className={styles.textMuted}>Fetching live gold rates...</span>
                </div>
              ) : (
                liveRates.map((rateData, idx) => (
                  <div key={idx} className={`p-4 rounded-2xl border ${isDarkMode ? 'bg-stone-900/60 border-stone-800' : 'bg-white border-stone-100'}`}>
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-bold text-lg">
                      {rateData._stale && rateData.Brand === 'Tanishq' ? (
                        <span title="Today rate updating soon" className="inline-flex items-center gap-2">
                          {rateData.Brand}
                          <span className="text-[11px] text-amber-400">(updating)</span>
                        </span>
                      ) : (
                        rateData.Brand
                      )}
                    </h3>
                      <span className={`text-[11px] uppercase tracking-[0.14em] ${styles.textMuted}`}>Per 1g</span>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div className={`rounded-xl border px-3 py-2 ${isDarkMode ? 'border-stone-800 bg-stone-950/40' : 'border-stone-200 bg-stone-50/80'}`}>
                        <div className={`text-[10px] uppercase tracking-[0.14em] ${styles.textMuted}`}>24K</div>
                        <div className={`mt-1 font-semibold ${isDarkMode ? 'text-amber-400' : 'text-amber-700'}`}>₹{rateData['24K']?.toLocaleString('en-IN') || 'N/A'}</div>
                      </div>
                      <div className={`rounded-xl border px-3 py-2 ${isDarkMode ? 'border-stone-800 bg-stone-950/40' : 'border-stone-200 bg-stone-50/80'}`}>
                        <div className={`text-[10px] uppercase tracking-[0.14em] ${styles.textMuted}`}>22K</div>
                        <div className="mt-1 font-semibold">₹{rateData['22K']?.toLocaleString('en-IN') || 'N/A'}</div>
                      </div>
                      <div className={`rounded-xl border px-3 py-2 ${isDarkMode ? 'border-stone-800 bg-stone-950/40' : 'border-stone-200 bg-stone-50/80'}`}>
                        <div className={`text-[10px] uppercase tracking-[0.14em] ${styles.textMuted}`}>18K</div>
                        <div className="mt-1 font-semibold">₹{rateData['18K']?.toLocaleString('en-IN') || 'N/A'}</div>
                      </div>
                      <div className={`rounded-xl border px-3 py-2 ${isDarkMode ? 'border-stone-800 bg-stone-950/40' : 'border-stone-200 bg-stone-50/80'}`}>
                        <div className={`text-[10px] uppercase tracking-[0.14em] ${styles.textMuted}`}>14K</div>
                        <div className="mt-1 font-semibold">₹{rateData['14K']?.toLocaleString('en-IN') || 'N/A'}</div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Desktop: table */}
            <div className="hidden sm:block overflow-x-auto">
              <table className="hero-rates-table w-full text-left whitespace-nowrap">
                <thead className={`text-sm uppercase tracking-widest ${isDarkMode ? 'bg-stone-950/80 text-stone-500' : 'bg-stone-100/80 text-stone-500'}`}>
                  <tr>
                    <th className="px-4 py-4 md:px-8 md:py-5 font-medium">Brand</th>
                    <th className="px-4 py-4 md:px-8 md:py-5 font-medium text-right  text-amber-600 dark:text-amber-500">24K</th>
                    <th className="px-4 py-4 md:px-8 md:py-5 font-medium text-right">22K</th>
                    <th className="px-4 py-4 md:px-8 md:py-5 font-medium text-right">18K</th>
                    <th className="px-4 py-4 md:px-8 md:py-5 font-medium text-right">14K</th>
                  </tr>
                </thead>
                <tbody className={`divide-y font-mono text-lg ${isDarkMode ? 'divide-stone-800/60' : 'divide-stone-200/60'}`}>
                  {loading ? (
                    <tr>
                      <td colSpan="5" className="px-4 py-8 md:px-8 md:py-10 text-center animate-pulse">
                        <span className={styles.textMuted}>Fetching live gold rates...</span>
                      </td>
                    </tr>
                  ) : (
                    liveRates.map((rateData, index) => (
                      <tr key={index} className={`transition-colors hover:${isDarkMode ? 'bg-stone-800/40' : 'bg-white/80'}`}>
                        <td className="px-4 py-4 md:px-8 md:py-6 font-serif text-lg md:text-xl font-medium">
                          {rateData._stale && rateData.Brand === 'Tanishq' ? (
                            <span title="Today rate updating soon" className="inline-flex items-center gap-2">
                              {rateData.Brand}
                              <span className="text-[12px] text-amber-400">(updating)</span>
                            </span>
                          ) : (
                            rateData.Brand || 'Unknown'
                          )}
                        </td>
                        <td className={`px-4 py-4 md:px-8 md:py-6 text-right text-lg md:text-xl font-bold ${isDarkMode ? 'text-amber-400' : 'text-amber-700'}`}>
                          ₹{rateData['24K']?.toLocaleString('en-IN') || 'N/A'}
                        </td>
                        <td className="px-4 py-4 md:px-8 md:py-6 text-right">₹{rateData['22K']?.toLocaleString('en-IN') || 'N/A'}</td>
                        <td className="px-4 py-4 md:px-8 md:py-6 text-right">₹{rateData['18K']?.toLocaleString('en-IN') || 'N/A'}</td>
                        <td className="px-4 py-4 md:px-8 md:py-6 text-right">₹{rateData['14K']?.toLocaleString('en-IN') || 'N/A'}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <FeatureRow isDarkMode={isDarkMode} />
        </div>
      </section>
    );
  };
