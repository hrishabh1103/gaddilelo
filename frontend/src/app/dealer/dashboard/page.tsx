'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { 
  Building2, Users, FileText, CheckCircle2, Clock, AlertCircle, 
  TrendingUp, PhoneCall, ArrowRight, ShieldCheck, Award
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { apiFetch } from '@/lib/api';
import { DealerDashboardStats } from '@/types';

export default function DealerDashboardPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  const [stats, setStats] = useState<DealerDashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoading) {
      if (!user) {
        router.push('/login?redirect=/dealer/dashboard');
        return;
      }
      if (user.role !== 'DEALER' && user.role !== 'ADMIN') {
        router.push('/dashboard');
        return;
      }
    }

    async function loadDealerStats() {
      try {
        const data = await apiFetch<DealerDashboardStats>('/dealers/dashboard');
        setStats(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }

    if (user && (user.role === 'DEALER' || user.role === 'ADMIN')) {
      loadDealerStats();
    }
  }, [user, isLoading, router]);

  if (isLoading || loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-sm text-slate-400">
        Loading dealership portal...
      </div>
    );
  }

  const isVerified = user?.dealer?.verification_status === 'VERIFIED' || user?.role === 'ADMIN';

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header & Verification Banner */}
      <div className="space-y-4 pb-6 border-b border-slate-200">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-2.5 py-0.5 rounded border border-blue-100">
                Authorized OEM Dealership Portal
              </span>
              <span className="text-xs text-slate-400">• Indore Territory</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-navy-950 mt-1">
              {user?.dealer?.dealership_name || user?.full_name}
            </h1>
          </div>

          <div className="flex items-center gap-2">
            <Link
              href="/dealer/invitations"
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-xl shadow-sm transition-colors flex items-center gap-1.5"
            >
              <Clock className="w-4 h-4" /> View Bidding Opportunities
            </Link>
          </div>
        </div>

        {/* Verification Status Banner */}
        <div className={`p-4 rounded-2xl border text-xs flex items-center justify-between gap-4 ${
          isVerified
            ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
            : 'bg-amber-50 border-amber-200 text-amber-900'
        }`}>
          <div className="flex items-center gap-3">
            {isVerified ? (
              <ShieldCheck className="w-5 h-5 text-emerald-600 flex-shrink-0" />
            ) : (
              <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0" />
            )}
            <div>
              <strong className="font-bold">
                Verification Status: {user?.dealer?.verification_status || 'VERIFIED'}
              </strong>
              <p className="text-[11px] opacity-80 mt-0.5">
                {isVerified
                  ? 'Your dealership is verified by the platform. You are authorized to submit competitive quotations on invited cohorts.'
                  : 'Your dealership verification documents are under review by platform administrators.'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Statistics Cards (Requirement 6) */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <div className="text-xs font-semibold text-slate-400">Invitations Received</div>
          <div className="text-2xl font-black text-navy-950">{stats?.invitations_count || 0}</div>
          <div className="text-[11px] text-slate-500">Total cohort invites</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <div className="text-xs font-semibold text-slate-400">Active Bidding</div>
          <div className="text-2xl font-black text-blue-600">{stats?.active_bidding_count || 0}</div>
          <div className="text-[11px] text-slate-500">Live opportunities</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <div className="text-xs font-semibold text-slate-400">Quotations Submitted</div>
          <div className="text-2xl font-black text-brand-600">{stats?.quotations_submitted_count || 0}</div>
          <div className="text-[11px] text-slate-500">Offers in market</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <div className="text-xs font-semibold text-slate-400">Customer Enquiries</div>
          <div className="text-2xl font-black text-purple-600">{stats?.leads_count || 0}</div>
          <div className="text-[11px] text-slate-500">Buyer callback requests</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <div className="text-xs font-semibold text-slate-400">Conversions</div>
          <div className="text-2xl font-black text-emerald-600">{stats?.conversions_count || 0}</div>
          <div className="text-[11px] text-slate-500">Purchases delivered</div>
        </div>
      </div>

      {/* Quick Navigation Panels */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-2">
        
        <Link
          href="/dealer/invitations"
          className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-blue-300 hover:shadow-md transition-all group space-y-3"
        >
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center group-hover:scale-105 transition-transform">
            <Clock className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-base text-navy-950">Group Bidding Invitations</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            View buying groups where your dealership has been invited to submit quotations for pooled Indore buyers.
          </p>
          <div className="text-xs font-semibold text-blue-600 flex items-center gap-1 pt-1">
            Open Invitations <ArrowRight className="w-3.5 h-3.5" />
          </div>
        </Link>

        <Link
          href="/dealer/quotations"
          className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-brand-300 hover:shadow-md transition-all group space-y-3"
        >
          <div className="w-10 h-10 rounded-xl bg-orange-50 text-brand-600 flex items-center justify-center group-hover:scale-105 transition-transform">
            <FileText className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-base text-navy-950">Manage Submitted Quotations</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            Review existing quotations, adjust pricing components before bidding deadlines, and inspect revision history.
          </p>
          <div className="text-xs font-semibold text-brand-600 flex items-center gap-1 pt-1">
            Review Quotations <ArrowRight className="w-3.5 h-3.5" />
          </div>
        </Link>

        <Link
          href="/dealer/leads"
          className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-purple-300 hover:shadow-md transition-all group space-y-3"
        >
          <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center group-hover:scale-105 transition-transform">
            <PhoneCall className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-base text-navy-950">Customer Enquiries & Leads</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            Track qualified buyers who requested a callback for your quotation. Update status from test drive to delivery.
          </p>
          <div className="text-xs font-semibold text-purple-600 flex items-center gap-1 pt-1">
            Manage Enquiries <ArrowRight className="w-3.5 h-3.5" />
          </div>
        </Link>

      </div>

    </div>
  );
}
