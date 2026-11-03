'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { 
  Sparkles, RefreshCw, CheckCircle2, Clock, XCircle, 
  Database, FileText, ArrowRight, Layers, Eye, ShieldAlert, AlertCircle
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { apiFetch } from '@/lib/api';

export default function IntelligenceOverviewPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  const [stats, setStats] = useState<any>(null);
  const [recentRecords, setRecentRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [scanMessage, setScanMessage] = useState('');

  useEffect(() => {
    if (!isLoading) {
      if (!user || user.role !== 'ADMIN') {
        router.push('/login');
        return;
      }
    }

    async function loadData() {
      try {
        const [overview, queue] = await Promise.all([
          apiFetch('/intelligence/overview'),
          apiFetch('/intelligence/queue?limit=5')
        ]);
        setStats(overview);
        setRecentRecords(queue || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    if (user && user.role === 'ADMIN') {
      loadData();
    }
  }, [user, isLoading, router]);

  const handleTriggerScan = async () => {
    setScanning(true);
    setScanMessage('');
    try {
      const res = await apiFetch('/intelligence/scan-now', { method: 'POST' });
      setScanMessage(`Scan complete: Discovered ${res.new_vehicles_discovered} new vehicle candidate(s).`);
      // Reload stats
      const [overview, queue] = await Promise.all([
        apiFetch('/intelligence/overview'),
        apiFetch('/intelligence/queue?limit=5')
      ]);
      setStats(overview);
      setRecentRecords(queue || []);
    } catch (e: any) {
      setScanMessage(e.message || 'Scan failed');
    } finally {
      setScanning(false);
    }
  };

  if (isLoading || loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-sm text-slate-400">
        Loading Vehicle Intelligence Engine...
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 font-sans">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-orange-600 bg-orange-50 px-2.5 py-0.5 rounded border border-orange-200">
              Automated Vehicle Intelligence Engine
            </span>
            <span className="text-xs text-slate-400">• Indian Automotive Sourcing</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-navy-950 mt-1">
            Vehicle Discovery & Intelligence
          </h1>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleTriggerScan}
            disabled={scanning}
            className="px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs rounded-xl shadow-sm transition-all flex items-center gap-1.5 disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${scanning ? 'animate-spin' : ''}`} />
            <span>{scanning ? 'Scanning Sources...' : 'Scan Sources Now'}</span>
          </button>
          
          <Link
            href="/admin"
            className="px-3.5 py-2 border border-slate-200 hover:bg-slate-50 text-slate-700 font-semibold text-xs rounded-xl transition-colors"
          >
            Back to Admin Console
          </Link>
        </div>
      </div>

      {/* Navigation Sub-Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-2 text-xs font-bold text-slate-600">
        <Link href="/admin/intelligence" className="px-3 py-1.5 rounded-lg bg-slate-900 text-white">
          Overview
        </Link>
        <Link href="/admin/intelligence/catalogue" className="px-3 py-1.5 rounded-lg hover:bg-slate-100 text-slate-700">
          Catalogue & Provenance
        </Link>
        <Link href="/admin/intelligence/queue" className="px-3 py-1.5 rounded-lg hover:bg-slate-100 text-slate-700">
          Discovery Queue ({stats?.pending_review_count || 0})
        </Link>
        <Link href="/admin/intelligence/sources" className="px-3 py-1.5 rounded-lg hover:bg-slate-100 text-slate-700">
          Data Sources ({stats?.active_sources_count || 0})
        </Link>
        <Link href="/admin/intelligence/history" className="px-3 py-1.5 rounded-lg hover:bg-slate-100 text-slate-700">
          Change History
        </Link>
      </div>

      {scanMessage && (
        <div className="p-3 bg-emerald-50 text-emerald-800 text-xs rounded-xl border border-emerald-200 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
          <span>{scanMessage}</span>
        </div>
      )}

      {/* Primary Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <div className="text-xs font-semibold text-slate-400">Total Discovered</div>
          <div className="text-2xl font-black text-navy-950">{stats?.total_discovered_vehicles || 0}</div>
          <div className="text-[11px] text-slate-500">Vehicles indexed from OEM feeds</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <div className="text-xs font-semibold text-slate-400">Pending Review</div>
          <div className="text-2xl font-black text-orange-600">{stats?.pending_review_count || 0}</div>
          <div className="text-[11px] text-slate-500">Awaiting administrative publishing</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <div className="text-xs font-semibold text-slate-400">Published to Catalogue</div>
          <div className="text-2xl font-black text-emerald-600">{stats?.approved_count || 0}</div>
          <div className="text-[11px] text-slate-500">Live in buyer group creator</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <div className="text-xs font-semibold text-slate-400">Customer Requests</div>
          <div className="text-2xl font-black text-blue-600">{stats?.total_customer_discovery_requests || 0}</div>
          <div className="text-[11px] text-slate-500">Buyers waiting for notifications</div>
        </div>

      </div>

      {/* Recent Discovered Candidates Table */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
        
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold text-base text-navy-950">Recent Vehicle Discoveries</h3>
            <p className="text-xs text-slate-500">Candidates awaiting verification and catalogue integration</p>
          </div>
          <Link
            href="/admin/intelligence/queue"
            className="text-xs font-bold text-brand-600 hover:text-brand-700 flex items-center gap-1"
          >
            <span>View Full Queue</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {recentRecords.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-400">
            No pending vehicle discoveries. Click &ldquo;Scan Sources Now&rdquo; to query OEM newsrooms.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 font-bold uppercase">
                  <th className="py-2.5 px-3">Vehicle Model</th>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3">Source Provider</th>
                  <th className="py-2.5 px-3">Confidence</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {recentRecords.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50">
                    <td className="py-3 px-3 font-bold text-navy-950">
                      {r.discovered_brand} {r.discovered_model}
                      <span className="block text-[10px] text-slate-400 font-normal">
                        Model Year: {r.model_year || '2026'}
                      </span>
                    </td>
                    <td className="py-3 px-3 uppercase text-slate-600">{r.category_slug}</td>
                    <td className="py-3 px-3 text-slate-500">{r.primary_source_name || 'OEM Newsroom'}</td>
                    <td className="py-3 px-3">
                      <span className="font-mono font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
                        {(Number(r.confidence_score) * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        r.review_status === 'APPROVED' 
                          ? 'bg-emerald-100 text-emerald-800' 
                          : r.review_status === 'REJECTED'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-orange-100 text-orange-800'
                      }`}>
                        {r.review_status}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-right">
                      <Link
                        href={`/admin/intelligence/review/${r.id}`}
                        className="px-3 py-1 bg-navy-950 hover:bg-slate-800 text-white font-bold text-xs rounded-lg transition-colors inline-flex items-center gap-1"
                      >
                        <Eye className="w-3 h-3" />
                        <span>Inspect</span>
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

