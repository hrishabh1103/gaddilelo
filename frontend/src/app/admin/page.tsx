'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { 
  Shield, Users, Building2, Car, Clock, FileText, 
  CheckCircle2, AlertCircle, ArrowRight, TrendingUp, History 
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { apiFetch } from '@/lib/api';

export default function AdminOverviewPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoading) {
      if (!user) {
        router.push('/login?redirect=/admin');
        return;
      }
      if (user.role !== 'ADMIN') {
        router.push('/dashboard');
        return;
      }
    }

    async function loadAdminStats() {
      try {
        const data = await apiFetch('/admin/overview');
        setStats(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    if (user && user.role === 'ADMIN') {
      loadAdminStats();
    }
  }, [user, isLoading, router]);

  if (isLoading || loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-sm text-slate-400">
        Loading admin console...
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-purple-600 bg-purple-50 px-2.5 py-0.5 rounded border border-purple-100">
              Platform Governance & Moderation
            </span>
            <span className="text-xs text-slate-400">• Pilot Hub: Indore, MP</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-navy-950 mt-1">
            GaadiLelo Administration Console
          </h1>
        </div>

        <div className="flex items-center gap-2">
          <Link
            href="/admin/dealers"
            className="px-3.5 py-2 bg-purple-600 hover:bg-purple-700 text-white font-semibold text-xs rounded-xl shadow-sm transition-colors"
          >
            Review Dealerships
          </Link>
          <Link
            href="/admin/quotations"
            className="px-3.5 py-2 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-xl shadow-sm transition-colors"
          >
            Moderate Quotations
          </Link>
        </div>
      </div>

      {/* Primary Metrics Grid (Requirement 7) */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <div className="text-xs font-semibold text-slate-400">Registered Buyers</div>
          <div className="text-2xl font-black text-navy-950">{stats?.total_buyers || 0}</div>
          <div className="text-[11px] text-slate-500">Consumer demand accounts</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <div className="text-xs font-semibold text-slate-400">Verified Dealerships</div>
          <div className="text-2xl font-black text-emerald-600">
            {stats?.verified_dealerships || 0}
            <span className="text-xs font-normal text-amber-600 ml-1">
              ({stats?.pending_dealerships || 0} pending)
            </span>
          </div>
          <div className="text-[11px] text-slate-500">Authorized OEM franchised partners</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <div className="text-xs font-semibold text-slate-400">Active Buying Groups</div>
          <div className="text-2xl font-black text-brand-600">{stats?.active_groups || 0}</div>
          <div className="text-[11px] text-slate-500">
            {stats?.bidding_open_groups || 0} in active bidding
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <div className="text-xs font-semibold text-slate-400">Approved Quotations</div>
          <div className="text-2xl font-black text-blue-600">
            {stats?.approved_quotations || 0} / {stats?.quotations_submitted || 0}
          </div>
          <div className="text-[11px] text-slate-500">
            {stats?.successful_conversions || 0} verified conversions
          </div>
        </div>

      </div>

      {/* Admin Operations Navigation Panels */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        
        <Link
          href="/admin/dealers"
          className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-purple-300 hover:shadow-md transition-all group space-y-3"
        >
          <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center group-hover:scale-105 transition-transform">
            <Building2 className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-sm text-navy-950">Dealer Verification</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            Verify OEM trade licenses, GSTIN credentials, and approve/reject dealership accounts.
          </p>
          <div className="text-xs font-semibold text-purple-600 flex items-center gap-1 pt-1">
            Manage Dealerships <ArrowRight className="w-3.5 h-3.5" />
          </div>
        </Link>

        <Link
          href="/admin/groups"
          className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-brand-300 hover:shadow-md transition-all group space-y-3"
        >
          <div className="w-10 h-10 rounded-xl bg-orange-50 text-brand-600 flex items-center justify-center group-hover:scale-105 transition-transform">
            <Users className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-sm text-navy-950">Buying Group Moderation</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            Supervise cohort lifecycles, schedule bidding sessions, and dispatch invitations to eligible dealerships.
          </p>
          <div className="text-xs font-semibold text-brand-600 flex items-center gap-1 pt-1">
            Manage Groups <ArrowRight className="w-3.5 h-3.5" />
          </div>
        </Link>

        <Link
          href="/admin/quotations"
          className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-blue-300 hover:shadow-md transition-all group space-y-3"
        >
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center group-hover:scale-105 transition-transform">
            <FileText className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-sm text-navy-950">Quotation Audit & Moderation</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            Review dealer quotation math, inspect discount sanity, and approve quotes before publishing to buyers.
          </p>
          <div className="text-xs font-semibold text-blue-600 flex items-center gap-1 pt-1">
            Moderate Quotes <ArrowRight className="w-3.5 h-3.5" />
          </div>
        </Link>

        <Link
          href="/admin/audit"
          className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-slate-400 hover:shadow-md transition-all group space-y-3"
        >
          <div className="w-10 h-10 rounded-xl bg-slate-100 text-slate-700 flex items-center justify-center group-hover:scale-105 transition-transform">
            <History className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-sm text-navy-950">System Audit Logs</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            Inspect immutable audit logs for administrative interventions, state changes, and pricing reviews.
          </p>
          <div className="text-xs font-semibold text-slate-700 flex items-center gap-1 pt-1">
            View Audit Trail <ArrowRight className="w-3.5 h-3.5" />
          </div>
        </Link>

      </div>

    </div>
  );
}

