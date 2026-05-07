// lib/constants.js

export const PURITY_FACTORS = {
  '24K': 1.0,
  '22K': 0.916,
  '18K': 0.750,
  '14K': 0.583
};

export const COIN_WEIGHT_OPTIONS = [
  { id: '1-5', label: '1-5' },
  { id: '5-10', label: '5-10' },
  { id: '10-25', label: '10-25' },
  { id: '25-50', label: '25-50' },
  { id: '50-100', label: '50-100' },
];

export const CATEGORIES = [
  { id: 'earring', label: 'Earring', baseChargeMod: 0.05 },
  { id: 'bali', label: 'Bali', baseChargeMod: 0.04 },
  { id: 'ring', label: 'Ring', baseChargeMod: 0.04 },
  { id: 'choker', label: 'Choker', baseChargeMod: 0.08 },
  { id: 'necklace', label: 'Necklace', baseChargeMod: 0.07 },
  { id: 'chain', label: 'Chain', baseChargeMod: 0.02 },
  { id: 'bangle', label: 'Bangle', baseChargeMod: 0.03 },
  { id: 'bracelet', label: 'Bracelet', baseChargeMod: 0.04 },
  { id: 'kada', label: 'Kada', baseChargeMod: 0.03 },
  { id: 'coin', label: 'Coin', baseChargeMod: 0 },
  { id: 'set', label: 'Set', baseChargeMod: 0.08 },
  { id: 'pendant', label: 'Pendant', baseChargeMod: 0.05 },
  { id: 'mangalsutra', label: 'Mangalsutra', baseChargeMod: 0.06 },
  { id: 'nose_pin', label: 'Nose Pin', baseChargeMod: 0.02 },
  { id: 'nath', label: 'Nath', baseChargeMod: 0.05 },
  { id: 'payal', label: 'Payal', baseChargeMod: 0.04 },
];

// Sabme sirf 'Gold' subcategory
export const SUBCATEGORIES = {
  earring: [{ id: 'gold', label: 'Gold', chargeMod: 0 }],
  bali: [{ id: 'gold', label: 'Gold', chargeMod: 0 }],
  ring: [{ id: 'gold', label: 'Gold', chargeMod: 0 }],
  choker: [{ id: 'gold', label: 'Gold', chargeMod: 0 }],
  necklace: [{ id: 'gold', label: 'Gold', chargeMod: 0 }],
  chain: [{ id: 'gold', label: 'Gold', chargeMod: 0 }],
  bangle: [{ id: 'gold', label: 'Gold', chargeMod: 0 }],
  bracelet: [{ id: 'gold', label: 'Gold', chargeMod: 0 }],
  kada: [{ id: 'gold', label: 'Gold', chargeMod: 0 }],
  coin: [{ id: 'gold', label: 'Gold', chargeMod: 0 }],
  set: [{ id: 'gold', label: 'Gold', chargeMod: 0 }],
  pendant: [{ id: 'gold', label: 'Gold', chargeMod: 0 }],
  mangalsutra: [{ id: 'gold', label: 'Gold', chargeMod: 0 }],
  nose_pin: [{ id: 'gold', label: 'Gold', chargeMod: 0 }],
  nath: [{ id: 'gold', label: 'Gold', chargeMod: 0 }],
  payal: [{ id: 'gold', label: 'Gold', chargeMod: 0 }],
};

export const BRANDS = [
  {
    id: 1,
    name: 'Tanishq',
    baseMaking: 0.18,
    accentColor: 'from-rose-500/20 to-rose-900/5',
    borderColor: 'border-rose-200/50 dark:border-rose-900/30',
    iconColor: 'text-rose-700 dark:text-rose-400',
    tagline: 'Premium Assurance',
    distance: '4.2 km',
    storeType: 'Corporate Showroom',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Tanishq_Logo.svg/2560px-Tanishq_Logo.svg.png',
  },
  {
    id: 2,
    name: 'Kalyan(Candere)',
    baseMaking: 0.14,
    accentColor: 'from-amber-500/20 to-amber-900/5',
    borderColor: 'border-amber-200/50 dark:border-amber-900/30',
    iconColor: 'text-amber-700 dark:text-amber-400',
    tagline: 'Trusted Legacy',
    distance: '2.8 km',
    storeType: 'Authorized Dealer',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Kalyan_Jewellers_Logo.svg/1200px-Kalyan_Jewellers_Logo.svg.png',
  },
  {
    id: 3,
    name: 'Malabar',
    baseMaking: 0.12,
    accentColor: 'from-orange-500/20 to-orange-900/5',
    borderColor: 'border-orange-200/50 dark:border-orange-900/30',
    iconColor: 'text-orange-700 dark:text-orange-400',
    tagline: 'Fair Price Promise',
    distance: '5.1 km',
    storeType: 'Large Format Store',
    image: 'https://upload.wikimedia.org/wikipedia/commons/e/ec/Malabar_Gold_and_Diamonds_Logo.jpg',
  },
  {
    id: 4,
    name: 'Senco',
    baseMaking: 0.13,
    accentColor: 'from-yellow-500/20 to-yellow-900/5',
    borderColor: 'border-yellow-200/50 dark:border-yellow-900/30',
    iconColor: 'text-yellow-700 dark:text-yellow-400',
    tagline: "World's Favorite",
    distance: '3.5 km',
    storeType: 'Flagship Store',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Joyalukkas_Logo.svg/2560px-Joyalukkas_Logo.svg.png',
  },
];