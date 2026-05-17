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
  const [errorMessage, setErrorMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const isValidContact = (value) => {
    const trimmed = value.trim();
    // normalize to digits for phone check
    const digits = (trimmed || '').replace(/\D/g, '');
    const isPhone = digits.length === 10 && /^[6789]/.test(digits);
    return isPhone;
  };

  const handleChange = (event) => {
    const { name, value } = event.target;
    if (errorMessage) {
      setErrorMessage('');
    }
    setFormState((current) => ({
      ...current,
      [name]: value,
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    const name = formState.name.trim();
    const contact = formState.contact.trim();
    const issue = formState.issue.trim();

    if (!name || !contact || !issue) {
      setStatusMessage('');
      setErrorMessage('Please fill all three fields before sending feedback.');
      return;
    }

    if (!isValidContact(contact)) {
      setStatusMessage('');
      setErrorMessage('Enter a valid 10-digit mobile number ');
      return;
    }

    const sendFeedback = async () => {
      setIsSubmitting(true);
      setStatusMessage('');

      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const endpoints = [`${baseUrl}/api/feedback`, `${baseUrl}/feedback`];
        let lastError = null;

        for (const endpoint of endpoints) {
          const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, contact, issue }),
          });

          const result = await response.json();

          if (response.ok) {
            setStatusMessage(result?.message || 'Feedback sent successfully.');
            setFormState({ name: '', contact: '', issue: '' });
            setErrorMessage('');
            return;
          }

          lastError = result?.detail || 'Unable to send feedback';
        }

        throw new Error(lastError || 'Unable to send feedback');
      } catch (error) {
        setStatusMessage('');
        setErrorMessage(error.message || 'Failed to send feedback.');
      } finally {
        setIsSubmitting(false);
      }
    };

    sendFeedback();
  };

  return (
    <section
      className={`feedback-section mt-16 sm:mt-20 rounded-3xl border shadow-2xl p-5 sm:p-6 md:p-10 transition-all duration-500 ${styles.cardBg} ${styles.borderColor}`}
    >
      <div className="flex items-center gap-3 mb-6 sm:mb-8">
        <div className={`h-8 w-1 rounded-full ${isDarkMode ? 'bg-cyan-500' : 'bg-amber-500'}`}></div>
        <div>
          <h2 className="text-xl sm:text-2xl font-serif font-medium">Help us to improve more</h2>
          <p className={`text-sm mt-1 ${styles.textMuted}`}>
           Any Improvements you feel. Please do fill out
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-5">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-5">
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
              className={`w-full rounded-xl border px-4 py-3 text-base outline-none transition-all duration-300 focus:ring-2 focus:ring-amber-400/40 ${styles.inputBg} ${styles.borderColor} ${styles.textMain}`}
            />
          </div>

          <div>
            <label className={`block text-xs font-bold uppercase tracking-wider mb-2 ${styles.textMuted}`}>
              Mobile Number
            </label>
            <input
              type="text"
              name="contact"
              value={formState.contact}
              onChange={handleChange}
              placeholder="10-digit mobile number"
              inputMode="tel"
              autoComplete="off"
              required
              className={`w-full rounded-xl border px-4 py-3 text-base outline-none transition-all duration-300 focus:ring-2 focus:ring-amber-400/40 ${styles.inputBg} ${styles.borderColor} ${styles.textMain}`}
            />
            <p className={`mt-2 text-[11px] ${styles.textMuted}`}>
              Enter a 10-digit mobile number only.
            </p>
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
            required
            className={`w-full rounded-2xl border px-4 py-3 text-base outline-none transition-all duration-300 focus:ring-2 focus:ring-amber-400/40 resize-y ${styles.inputBg} ${styles.borderColor} ${styles.textMain}`}
          />
        </div>

        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 pt-2">
          <p className={`text-sm ${styles.textMuted}`}>
            We’ll review the feedback and use it to improve the estimate flow.
          </p>

          <button
            type="submit"
            disabled={isSubmitting}
            className="inline-flex w-full sm:w-auto items-center justify-center gap-2 rounded-xl bg-amber-600 px-5 py-3 text-white font-semibold shadow-lg transition-colors hover:bg-amber-700"
          >
            <Send size={18} />
            {isSubmitting ? 'Sending...' : 'Send Feedback'}
          </button>
        </div>

        {errorMessage && (
          <div className="rounded-xl border border-red-400/40 bg-red-500/10 px-4 py-3 text-sm text-red-500">
            {errorMessage}
          </div>
        )}

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