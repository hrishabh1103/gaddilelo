'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { 
  FileText, CheckCircle2, XCircle, ArrowLeft, ShieldCheck, 
  IndianRupee, Clock, AlertCircle, Building2 
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { apiFetch } from '@/lib/api';
import { Quotation } from '@/types';

export default function AdminQuotationsPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  const [quotations, setQuotations] = useState<Quotation[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [feedback, setFeedback] = useState('');

  useEffect(() => {
    if (!isLoading) {
      if (!user) {
        router.push('/login?redirect=/admin/quotations');
        return;
      }
      if (user.role !== 'ADMIN') {
        router.push('/dashboard');
        return;
      }
    }

    async function loadQuotations() {
      try {
        const data = await apiFetch<Quotation[]>('/admin/quotations');
        setQuotations(data || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    if (user && user.role === 'ADMIN') {
      loadQuotations();
    }
  }, [user, isLoading, router]);

  const handleApprove = async (quoteId: string) => {
    setActionLoading(quoteId);
    setFeedback('');
    try {
      await apiFetch(`/admin/quotations/${quoteId}/approve`, {
        method: 'PUT',
        body: JSON.stringify({ notes: 'Verified compliance with state RTO statutory brackets and OEM margins.' }),
      });

      setQuotations(prev => prev.map(q => q.id === quoteId ? { ...q, status: 'APPROVED' } : q));
      setFeedback('Quotation verified & approved! It is now live for cohort comparison and buyers have been notified.');
    } catch (err: any) {
      setFeedback(err.message || 'Approval failed');
    } finally {
      setActionLoading(null);
    }
  };

  const handleReject = async (quoteId: string) => {
    setActionLoading(quoteId);
    setFeedback('');
    try {
      await apiFetch(`/admin/quotations/${quoteId}/reject`, {
        method: 'PUT',
        body: JSON.stringify({ notes: 'Discounts or statutory tax components require correction. Please verify RTO fees.' }),
      });

      setQuotations(prev => prev.map(q => q.id === quoteId ? { ...q, status: 'REJECTED' } : q));
      setFeedback('Quotation rejected with corrective feedback.');
    } catch (err: any) {
      setFeedback(err.message || 'Rejection failed');
    } finally {
      setActionLoading(null);
    }
  };

  if (isLoading || loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-sm text-slate-400">
        Loading quotation audit queue...
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <Link href="/admin" className="text-xs font-semibold text-slate-500 hover:text-navy-900 flex items-center gap-1 mb-1">
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Console
          </Link>
          <h1 className="text-2xl sm:text-3xl font-black text-navy-950">
            Quotation Audit & Moderation Desk
          </h1>
          <p className="text-xs sm:text-sm text-slate-500">
            Audit submitted dealer quotations to ensure transparent pricing, correct statutory taxes, and zero double-counting.
          </p>
        </div>
      </div>

      {feedback && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-xl flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 flex-shrink-0 text-emerald-600" />
          <span>{feedback}</span>
        </div>
      )}

      {/* Quotations List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {quotations.map((q) => {
          const totalDiscounts = Number(q.mfg_discount) + Number(q.dealer_discount) + Number(q.exchange_bonus) + Number(q.corporate_discount);

          return (
            <div
              key={q.id}
              className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4 flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-blue-700 bg-blue-50 px-2 py-0.5 rounded">
                      Rev #{q.revision_number}
                    </span>
                    <h3 className="font-bold text-base text-navy-950 mt-1">
                      {q.dealership_name}
                    </h3>
                    <p className="text-xs text-slate-400">{q.dealer_city || 'Indore, MP'}</p>
                  </div>
                  <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                    q.status === 'APPROVED'
                      ? 'bg-emerald-100 text-emerald-800'
                      : q.status === 'REJECTED'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-amber-100 text-amber-800'
                  }`}>
                    {q.status}
                  </span>
                </div>

                {/* Arithmetic Breakdown */}
                <div className="bg-slate-50 p-4 rounded-xl text-xs space-y-2 border border-slate-200/60 font-mono">
                  <div className="flex justify-between text-slate-600">
                    <span>Base Ex-Showroom:</span>
                    <strong>₹{Number(q.base_ex_showroom).toLocaleString('en-IN')}</strong>
                  </div>
                  <div className="flex justify-between text-slate-600">
                    <span>RTO + Insurance + TCS:</span>
                    <strong>₹{(Number(q.rto_road_tax) + Number(q.insurance_amount) + Number(q.tcs_amount)).toLocaleString('en-IN')}</strong>
                  </div>
                  <div className="flex justify-between text-emerald-700 font-bold">
                    <span>Total Net Discounts:</span>
                    <span>-₹{totalDiscounts.toLocaleString('en-IN')}</span>
                  </div>
                  <div className="flex justify-between text-navy-950 font-black text-sm pt-1 border-t border-slate-200">
                    <span>Final On-Road Price:</span>
                    <span className="text-brand-600">₹{Number(q.final_on_road_price).toLocaleString('en-IN')}</span>
                  </div>
                </div>

                <div className="text-xs text-slate-500 space-y-0.5">
                  <div>Delivery Commitment: <strong className="text-navy-900">{q.delivery_timeline_days} Days</strong></div>
                  <div>Valid Until: <strong className="text-navy-900">{new Date(q.offer_valid_until).toLocaleDateString()}</strong></div>
                  {q.remarks && <div className="italic text-slate-600 pt-1">&ldquo;{q.remarks}&rdquo;</div>}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-2 border-t border-slate-100 flex items-center gap-2">
                <button
                  onClick={() => handleApprove(q.id)}
                  disabled={actionLoading === q.id || q.status === 'APPROVED'}
                  className="flex-1 py-2.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-40 text-white font-bold text-xs rounded-xl shadow-sm transition-colors flex items-center justify-center gap-1.5"
                >
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  {q.status === 'APPROVED' ? 'Approved & Live' : 'Approve & Publish to Cohort'}
                </button>
                <button
                  onClick={() => handleReject(q.id)}
                  disabled={actionLoading === q.id || q.status === 'REJECTED'}
                  className="px-3.5 py-2.5 bg-red-100 hover:bg-red-200 disabled:opacity-40 text-red-700 font-semibold text-xs rounded-xl transition-colors"
                >
                  <XCircle className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          );
        })}
      </div>

    </div>
  );
}
