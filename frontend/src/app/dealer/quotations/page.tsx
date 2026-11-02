'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { 
  FileText, Clock, CheckCircle2, AlertCircle, ArrowRight, 
  RotateCcw, ShieldCheck, MapPin 
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { apiFetch } from '@/lib/api';
import { Quotation } from '@/types';

export default function DealerQuotationsPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  const [quotations, setQuotations] = useState<Quotation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoading) {
      if (!user) {
        router.push('/login?redirect=/dealer/quotations');
        return;
      }
      if (user.role !== 'DEALER' && user.role !== 'ADMIN') {
        router.push('/dashboard');
        return;
      }
    }

    async function loadQuotes() {
      try {
        const data = await apiFetch<Quotation[]>('/dealers/quotations');
        setQuotations(data || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    if (user && (user.role === 'DEALER' || user.role === 'ADMIN')) {
      loadQuotes();
    }
  }, [user, isLoading, router]);

  if (isLoading || loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-sm text-slate-400">
        Loading quotations...
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <div className="text-xs font-bold uppercase tracking-wider text-blue-600">Dealership Bidding Registry</div>
          <h1 className="text-2xl sm:text-3xl font-black text-navy-950 mt-1">
            Submitted Quotations & Revisions
          </h1>
          <p className="text-xs sm:text-sm text-slate-500">
            Track quotation review status, revision history, and update offers before cohort bidding windows close.
          </p>
        </div>

        <Link
          href="/dealer/invitations"
          className="text-xs font-semibold text-slate-600 hover:text-navy-900 border border-slate-200 px-3 py-2 rounded-xl"
        >
          ← View New Invitations
        </Link>
      </div>

      {quotations.length === 0 ? (
        <div className="p-16 bg-white rounded-3xl border border-slate-200 text-center space-y-3">
          <FileText className="w-10 h-10 text-slate-300 mx-auto" />
          <h3 className="text-sm font-bold text-navy-950">No quotations submitted yet</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            Check your group invitations to find live cohort opportunities and submit your dealership&apos;s best quote.
          </p>
          <Link
            href="/dealer/invitations"
            className="inline-block px-4 py-2 bg-blue-600 text-white text-xs font-semibold rounded-xl"
          >
            Explore Invitations
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {quotations.map((quote) => {
            const totalDiscount = Number(quote.mfg_discount) + Number(quote.dealer_discount) + Number(quote.exchange_bonus) + Number(quote.corporate_discount);

            return (
              <div
                key={quote.id}
                className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between space-y-4"
              >
                <div className="space-y-3">
                  <div className="flex justify-between items-start">
                    <span className="font-mono text-xs font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                      Rev #{quote.revision_number}
                    </span>
                    <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                      quote.status === 'APPROVED'
                        ? 'bg-emerald-100 text-emerald-800'
                        : quote.status === 'REJECTED'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-amber-100 text-amber-800'
                    }`}>
                      {quote.status}
                    </span>
                  </div>

                  <div className="space-y-1">
                    <div className="text-xs text-slate-400">Dealership: {quote.dealership_name}</div>
                    <div className="text-2xl font-black text-navy-950">
                      ₹{Number(quote.final_on_road_price).toLocaleString('en-IN')}
                    </div>
                    <div className="text-xs text-slate-500">
                      Base Ex-showroom: ₹{Number(quote.base_ex_showroom).toLocaleString('en-IN')}
                    </div>
                  </div>

                  <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-100 text-xs flex justify-between items-center text-emerald-900">
                    <span>Total Net Discounts:</span>
                    <strong className="font-bold text-sm text-emerald-700">
                      -₹{totalDiscount.toLocaleString('en-IN')}
                    </strong>
                  </div>

                  <div className="text-xs text-slate-600 space-y-1">
                    <div>Delivery Timeline: <strong className="text-navy-900">{quote.delivery_timeline_days} Days</strong></div>
                    <div>Valid Until: <strong className="text-navy-900">{new Date(quote.offer_valid_until).toLocaleDateString()}</strong></div>
                    {quote.remarks && (
                      <div className="text-slate-500 italic mt-1">&ldquo;{quote.remarks}&rdquo;</div>
                    )}
                  </div>

                  {quote.admin_review_notes && (
                    <div className="p-3 bg-slate-50 rounded-xl text-xs text-slate-600 border border-slate-200/80">
                      <strong>Admin Notes:</strong> {quote.admin_review_notes}
                    </div>
                  )}
                </div>

                <div className="pt-2 border-t border-slate-100 flex items-center gap-2">
                  <Link
                    href={`/dealer/bid/${quote.group_id}`}
                    className="flex-1 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-xl transition-colors text-center flex items-center justify-center gap-1.5"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    Revise Pricing
                  </Link>
                  <Link
                    href={`/groups/${quote.group_id}`}
                    className="px-3.5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs rounded-xl transition-colors"
                  >
                    View Group
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}

    </div>
  );
}
