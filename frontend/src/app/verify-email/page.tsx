'use client';

import React, { useState, useEffect, Suspense } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { CheckCircle2, AlertCircle, ArrowRight, ShieldCheck, Mail } from 'lucide-react';
import { apiFetch } from '@/lib/api';

function VerifyEmailContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get('token');

  const [loading, setLoading] = useState(true);
  const [success, setSuccess] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    async function verify() {
      if (!token) {
        setLoading(false);
        setMessage('No verification token provided in link.');
        return;
      }

      try {
        const res = await apiFetch(`/auth/verify-email?token=${encodeURIComponent(token)}`);
        setSuccess(true);
        setMessage(res.message || 'Email verified successfully!');
      } catch (err: any) {
        setSuccess(false);
        setMessage(err.message || 'Verification link is invalid or expired.');
      } finally {
        setLoading(false);
      }
    }

    verify();
  }, [token]);

  return (
    <div className="min-h-[70vh] flex items-center justify-center px-4 py-12">
      <div className="max-w-md w-full bg-white p-8 rounded-3xl border border-slate-200/80 shadow-lg text-center space-y-6">
        
        {loading ? (
          <div className="py-8 space-y-4">
            <div className="w-12 h-12 border-3 border-brand-500 border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-sm text-slate-600 font-medium">Verifying your email address...</p>
          </div>
        ) : success ? (
          <div className="space-y-4">
            <div className="w-14 h-14 bg-emerald-100 text-emerald-600 rounded-3xl flex items-center justify-center mx-auto shadow-sm">
              <CheckCircle2 className="w-8 h-8" />
            </div>
            <h1 className="text-2xl font-black text-navy-950">Email Verified!</h1>
            <p className="text-xs text-slate-500 max-w-xs mx-auto">
              {message}
            </p>
            <div className="pt-4">
              <Link
                href="/login"
                className="inline-flex items-center gap-1.5 px-6 py-3 bg-brand-500 hover:bg-brand-600 text-white font-bold text-xs rounded-xl shadow-md shadow-brand-500/20 transition-all"
              >
                Sign In to Your Account <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="w-14 h-14 bg-red-100 text-red-600 rounded-3xl flex items-center justify-center mx-auto shadow-sm">
              <AlertCircle className="w-8 h-8" />
            </div>
            <h1 className="text-2xl font-black text-navy-950">Verification Failed</h1>
            <p className="text-xs text-slate-500 max-w-xs mx-auto">
              {message}
            </p>
            <div className="pt-4 flex flex-col gap-2">
              <Link
                href="/login"
                className="px-6 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs rounded-xl shadow-sm transition-all"
              >
                Go to Sign In
              </Link>
              <Link
                href="/"
                className="text-xs text-slate-500 hover:text-slate-800 font-medium"
              >
                Back to Homepage
              </Link>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-sm text-slate-400">Loading verification...</div>}>
      <VerifyEmailContent />
    </Suspense>
  );
}

