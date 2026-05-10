'use client';

import React from 'react';

export default function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="w-full border-t bg-white dark:bg-stone-900 dark:border-stone-700 mt-12">
      <div className="max-w-6xl mx-auto px-4 py-6 flex flex-col md:flex-row items-center- justify-between gap-4">
        <div className="text-sm-center text-stone-700 dark:text-stone-300">© {year} Om-Rani. All rights reserved.</div>

        <div className="flex items-center gap-6">
          <nav className="flex gap-4 text-sm">
            {/* <a href="/about" className="text-stone-600 dark:text-stone-300 hover:underline">About</a>
            <a href="/privacy" className="text-stone-600 dark:text-stone-300 hover:underline">Privacy</a> */}
            {/* <a href="/contact" className="text-stone-600 dark:text-stone-300 hover:underline">Contact</a> */}
          </nav>

          {/* <div className="text-sm text-stone-500 dark:text-stone-400">Made with <span aria-hidden>❤️</span></div> */}
        </div>
      </div>
    </footer>
  );
}
