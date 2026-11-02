'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { User, Phone, Mail, MapPin, CheckCircle2, ShieldCheck, ArrowRight } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { apiFetch } from '@/lib/api';

export default function ProfilePage() {
  const { user, isLoading, refreshUser } = useAuth();
  const router = useRouter();

  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [language, setLanguage] = useState('en');
  const [consent, setConsent] = useState(true);
  const [saving, setSaving] = useState(false);
  const [feedback, setFeedback] = useState('');

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login?redirect=/profile');
      return;
    }
    if (user) {
      setFullName(user.full_name || '');
      setPhone(user.phone || '');
    }
  }, [user, isLoading, router]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setFeedback('');
    try {
      await apiFetch('/auth/profile', {
        method: 'PUT',
        body: JSON.stringify({
          full_name: fullName,
          phone: phone,
          preferred_language: language,
          communication_consent: consent,
        }),
      });

      await refreshUser();
      setFeedback('Profile preferences saved successfully.');
    } catch (err: any) {
      setFeedback(err.message || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-xl mx-auto px-4 py-16 text-center text-sm text-slate-400">
        Loading profile...
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      
      <div className="space-y-1 pb-6 border-b border-slate-200">
        <h1 className="text-2xl font-black text-navy-950">Profile & Settings</h1>
        <p className="text-xs text-slate-500">Manage your contact details, privacy consent, and preferences.</p>
      </div>

      {feedback && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-xl flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
          <span>{feedback}</span>
        </div>
      )}

      <form onSubmit={handleSave} className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200/80 shadow-sm space-y-6">
        
        <div className="space-y-4 text-xs">
          <div className="space-y-1">
            <label className="font-bold text-slate-700">Full Name</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-slate-900 focus:outline-none"
            />
          </div>

          <div className="space-y-1">
            <label className="font-bold text-slate-700">Email Address (Immutable)</label>
            <input
              type="email"
              disabled
              value={user?.email || ''}
              className="w-full bg-slate-100 border border-slate-200 rounded-xl px-3 py-2.5 text-slate-500 cursor-not-allowed"
            />
          </div>

          <div className="space-y-1">
            <label className="font-bold text-slate-700">Phone Number</label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              required
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-slate-900 focus:outline-none"
            />
          </div>

          <div className="space-y-1">
            <label className="font-bold text-slate-700">Preferred Language</label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-slate-900 focus:outline-none"
            >
              <option value="en">English</option>
              <option value="hi">Hindi (हिंदी)</option>
            </select>
          </div>

          <div className="pt-2">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={consent}
                onChange={(e) => setConsent(e.target.checked)}
                className="rounded border-slate-300 text-brand-500 focus:ring-brand-500"
              />
              <span className="text-slate-700 font-medium">
                I consent to receive cohort milestone updates and verified dealership quotations via in-app & SMS.
              </span>
            </label>
          </div>
        </div>

        <button
          type="submit"
          disabled={saving}
          className="w-full py-3 bg-navy-900 hover:bg-navy-800 disabled:opacity-50 text-white font-bold text-xs rounded-xl transition-all"
        >
          {saving ? 'Saving Changes...' : 'Save Profile Settings'}
        </button>

      </form>

    </div>
  );
}

