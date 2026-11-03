'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { 
  Filter, Eye, ArrowRight, ExternalLink, CheckCircle2, Clock, 
  XCircle, ArrowLeft, RefreshCw, Sparkles 
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { apiFetch } from '@/lib/api';

export default function DiscoveryQueuePage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  const [records, setRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('PENDING_REVIEW');
  const [categoryFilter, setCategoryFilter] = useState('');

  useEffect(() => {
    if (!isLoading) {
      if (!user || user.role !== 'ADMIN') {
        router.push('/login');
        return;
      }
    }

    async function loadQueue() {
      setLoading(true);
      try {
        const params = new URLSearchParams();
        if (statusFilter && statusFilter !== 'ALL') params.append('review_status', statusFilter);
        if (categoryFilter) params.append('category', categoryFilter);

        const data = await apiFetch(`/intelligence/queue?${params.toString()}`);
        setRecords(data || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }

    if (user && user.role === 'ADMIN') {
      loadQueue();
    }
  }, [user, isLoading, router, statusFilter, categoryFilter]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6 font-sans">
      
      {/* Top Breadcrumb */}
      <div className="flex items-center gap-2 text-xs font-semibold text-slate-500">
        <Link href="/admin/intelligence" className="hover:text-brand-600 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Vehicle Intelligence</span>
        </Link>
        <span>/</span>
        <span className="text-slate-800 font-bold">Discovery Queue</span>
      </div>

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-black text-navy-950">Vehicle Discovery Queue</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Review discovered vehicle candidates, inspect extracted specifications, and approve publishing.
          </p>
        </div>

        <Link
          href="/admin/intelligence"
          className="px-3.5 py-2 border border-slate-200 hover:bg-slate-50 text-slate-700 font-semibold text-xs rounded-xl"
        >
          Intelligence Overview
        </Link>
      </div>

      {/* Filter Strip */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 flex flex-wrap items-center justify-between gap-4 text-xs">
        <div className="flex items-center gap-2">
          <span className="font-bold text-slate-600 uppercase text-[11px]">Status:</span>
          {['ALL', 'PENDING_REVIEW', 'APPROVED', 'REJECTED'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1.5 rounded-xl font-bold transition-all ${
                statusFilter === st
                  ? 'bg-slate-900 text-white shadow-xs'
                  : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
              }`}
            >
              {st.replace('_', ' ')}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <span className="font-bold text-slate-600 uppercase text-[11px]">Category:</span>
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-1.5 font-medium text-slate-700 focus:outline-none"
          >
            <option value="">All Categories</option>
            <option value="car">Cars & SUVs</option>
            <option value="electric-vehicle">Electric Vehicles</option>
            <option value="two-wheeler">Two-Wheelers</option>
            <option value="commercial-vehicle">Commercial</option>
          </select>
        </div>
      </div>

      {/* Records Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-16 text-center text-xs text-slate-400">Loading queue...</div>
        ) : records.length === 0 ? (
          <div className="p-16 text-center text-xs text-slate-400">
            No discovery records match the selected filters.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 font-bold uppercase">
                  <th className="py-3 px-4">Vehicle Model</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Source Provider</th>
                  <th className="py-3 px-4">Confidence</th>
                  <th className="py-3 px-4">Discovered Date</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Review Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {records.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50">
                    <td className="py-3.5 px-4 font-bold text-navy-950">
                      {r.discovered_brand} {r.discovered_model}
                      <span className="block text-[10px] text-slate-400 font-normal">
                        Model Year: {r.model_year || '2026'} • {r.body_type}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 uppercase text-slate-600 font-medium">
                      {r.category_slug}
                    </td>
                    <td className="py-3.5 px-4 text-slate-600">
                      {r.primary_source_name || 'Official OEM'}
                      {r.primary_source_url && (
                        <a
                          href={r.primary_source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-0.5 text-brand-600 hover:underline ml-1.5"
                        >
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="font-mono font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
                        {(Number(r.confidence_score) * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-500">
                      {new Date(r.created_at).toLocaleDateString('en-IN', {
                        day: 'numeric',
                        month: 'short',
                        year: 'numeric'
                      })}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`px-2.5 py-1 rounded text-[10px] font-bold uppercase ${
                        r.review_status === 'APPROVED' 
                          ? 'bg-emerald-100 text-emerald-800' 
                          : r.review_status === 'REJECTED'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-orange-100 text-orange-800'
                      }`}>
                        {r.review_status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <Link
                        href={`/admin/intelligence/review/${r.id}`}
                        className="px-3.5 py-1.5 bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs rounded-xl transition-colors inline-flex items-center gap-1 shadow-xs"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>Inspect & Approve</span>
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
}

