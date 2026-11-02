'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { 
  Building2, Clock, Users, ArrowRight, CheckCircle2, 
  AlertCircle, ShieldCheck, MapPin, Sparkles 
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { apiFetch } from '@/lib/api';

export default function DealerInvitationsPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  const [invitations, setInvitations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoading) {
      if (!user) {
        router.push('/login?redirect=/dealer/invitations');
        return;
      }
      if (user.role !== 'DEALER' && user.role !== 'ADMIN') {
        router.push('/dashboard');
        return;
      }
    }

    async function loadInvitations() {
      try {
        const data = await apiFetch('/dealers/invitations');
        setInvitations(data || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    if (user && (user.role === 'DEALER' || user.role === 'ADMIN')) {
      loadInvitations();
    }
  }, [user, isLoading, router]);

  if (isLoading || loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-sm text-slate-400">
        Loading invitations...
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <div className="text-xs font-bold uppercase tracking-wider text-blue-600">Dealership Bidding Center</div>
          <h1 className="text-2xl sm:text-3xl font-black text-navy-950 mt-1">
            Group Bidding Invitations
          </h1>
          <p className="text-xs sm:text-sm text-slate-500">
            Exclusive buying cohorts in Indore your dealership is authorized to quote for.
          </p>
        </div>

        <Link
          href="/dealer/dashboard"
          className="text-xs font-semibold text-slate-600 hover:text-navy-900 border border-slate-200 px-3 py-2 rounded-xl"
        >
          ← Return to Dashboard
        </Link>
      </div>

      {/* Invitations List */}
      {invitations.length === 0 ? (
        <div className="p-16 bg-white rounded-3xl border border-slate-200 text-center space-y-3">
          <Clock className="w-10 h-10 text-slate-300 mx-auto" />
          <h3 className="text-sm font-bold text-navy-950">No invitations received yet</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            When buying groups reach their member milestones and match your authorized OEM brands, platform administrators will dispatch bidding invitations.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {invitations.map((inv) => (
            <div
              key={inv.invitation_id}
              className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between space-y-4"
            >
              <div className="space-y-3">
                <div className="flex justify-between items-start">
                  <span className="font-mono text-[10px] font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                    {inv.group_code}
                  </span>
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                    inv.has_submitted_quote ? 'bg-emerald-100 text-emerald-800' : 'bg-blue-100 text-blue-800'
                  }`}>
                    {inv.has_submitted_quote ? 'Quotation Submitted' : 'Pending Quotation'}
                  </span>
                </div>

                <div>
                  <h3 className="font-bold text-base text-navy-950">
                    {inv.vehicle.name}
                  </h3>
                  <p className="text-xs text-slate-500">
                    Variant: {inv.vehicle.variant}
                  </p>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    Benchmark Ex-showroom: ₹{inv.vehicle.reference_ex_showroom.toLocaleString('en-IN')}
                  </p>
                </div>

                <div className="p-3 bg-slate-50 rounded-xl space-y-1 text-xs text-slate-600 border border-slate-200/60">
                  <div className="flex justify-between">
                    <span>Pooled Buyers:</span>
                    <strong className="text-navy-900">{inv.current_members} Buyers</strong>
                  </div>
                  <div className="flex justify-between">
                    <span>Timeline:</span>
                    <strong className="text-navy-900">{inv.target_purchase_timeline.replace(/_/g, ' ')}</strong>
                  </div>
                  <div className="flex justify-between">
                    <span>Territory:</span>
                    <strong className="text-navy-900">{inv.city_name}</strong>
                  </div>
                </div>

                {inv.has_submitted_quote && (
                  <div className="p-3 bg-emerald-50 rounded-xl text-xs text-emerald-800 space-y-1 border border-emerald-100">
                    <div className="flex justify-between">
                      <span>Submitted Price:</span>
                      <strong className="font-bold">₹{inv.submitted_quote_price?.toLocaleString('en-IN')}</strong>
                    </div>
                    <div className="text-[10px] text-emerald-700">
                      Status: {inv.submitted_quote_status}
                    </div>
                  </div>
                )}
              </div>

              <div className="pt-2">
                <Link
                  href={`/dealer/bid/${inv.group_id}`}
                  className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-xl transition-colors flex items-center justify-center gap-1.5"
                >
                  {inv.has_submitted_quote ? 'Revise Quotation' : 'Submit Quotation'}
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  );
}
