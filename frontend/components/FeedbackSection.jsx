'use client';

import { useState } from 'react';
import { MessageSquareText, Send } from 'lucide-react';
import { getThemeStyles } from '@/lib/utils';

export const FeedbackSection = ({ isDarkMode }) => {
  const styles = getThemeStyles(isDarkMode);
  const [formState, setFormState] = useState({
    name: '',
    contact: '',
    issue: '',
  });
  const [statusMessage, setStatusMessage] = useState('');

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormState((current) => ({
      ...current,
      [name]: value,
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    setStatusMessage('Thanks. Your feedback has been captured locally and is ready to be sent to your team.');
    setFormState({ name: '', contact: '', issue: '' });
  };

  return (
    <section
      className={`mt-20 rounded-3xl border shadow-2xl p-6 md:p-10 transition-all duration-500 ${styles.cardBg} ${styles.borderColor}`}
    >
      <div className="flex items-center gap-3 mb-8">
        <div className={`h-8 w-1 rounded-full ${isDarkMode ? 'bg-cyan-500' : 'bg-amber-500'}`}></div>
        <div>
          <h2 className="text-2xl font-serif font-medium">Feedback</h2>
          <p className={`text-sm mt-1 ${styles.textMuted}`}>
            Send us your name, contact, and issue so we can review it.
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div>
            <label className={`block text-xs font-bold uppercase tracking-wider mb-2 ${styles.textMuted}`}>
              Name
            </label>
            <input
              type="text"
              name="name"
              value={formState.name}
              onChange={handleChange}
              placeholder="Your name"
              className={`w-full rounded-xl border px-4 py-3 outline-none transition-all duration-300 focus:ring-2 focus:ring-amber-400/40 ${styles.inputBg} ${styles.borderColor} ${styles.textMain}`}
            />
          </div>

          <div>
            <label className={`block text-xs font-bold uppercase tracking-wider mb-2 ${styles.textMuted}`}>
              Gmail / Number
            </label>
            <input
              type="text"
              name="contact"
              value={formState.contact}
              onChange={handleChange}
              placeholder="you@gmail.com or 98xxxxxx"
              className={`w-full rounded-xl border px-4 py-3 outline-none transition-all duration-300 focus:ring-2 focus:ring-amber-400/40 ${styles.inputBg} ${styles.borderColor} ${styles.textMain}`}
            />
          </div>
        </div>

        <div>
          <label className={`block text-xs font-bold uppercase tracking-wider mb-2 ${styles.textMuted}`}>
            Issue
          </label>
          <textarea
            name="issue"
            value={formState.issue}
            onChange={handleChange}
            placeholder="Tell us what went wrong or what we should improve."
            rows={5}
            className={`w-full rounded-2xl border px-4 py-3 outline-none transition-all duration-300 focus:ring-2 focus:ring-amber-400/40 resize-y ${styles.inputBg} ${styles.borderColor} ${styles.textMain}`}
          />
        </div>

        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 pt-2">
          <p className={`text-sm ${styles.textMuted}`}>
            We’ll review the feedback and use it to improve the estimate flow.
          </p>

          <button
            type="submit"
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-amber-500 px-5 py-3 text-white font-semibold shadow-lg transition-colors hover:bg-amber-600"
          >
            <Send size={18} />
            Send Feedback
          </button>
        </div>

        {statusMessage && (
          <div className={`flex items-center gap-2 rounded-xl border px-4 py-3 text-sm ${styles.borderColor} ${styles.textMain}`}>
            <MessageSquareText size={16} />
            <span>{statusMessage}</span>
          </div>
        )}
      </form>
    </section>
  );
};