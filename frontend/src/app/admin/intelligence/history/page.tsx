'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ArrowLeft, History, IndianRupee, Layers, Tag, ExternalLink } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { apiFetch } from '@/lib/api';

export default function VehicleChangeHistoryPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoading) {
      if (!user || user.role !== 'ADMIN') {
        router.push('/login');
        return;
      }
    }

    async function loadHistory() {
      try {
        const data = await apiFetch('/intelligence/history');
        setHistory(data || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    if (user && user.role === 'ADMIN') {
      loadHistory();
    }
  }, [user, isLoading, router]);

  const getChangeTypeBadge = (type: string) => {
    switch (type) {
      case 'PRICE_REVISION':
        return <span className="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded text-[10px] font-bold">PRICE REVISION</span>;
      case 'NEW_VARIANT':
        return <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded text-[10px] font-bold">NEW VARIANT</span>;
      case 'SPECIFICATION_UPDATE':
        return <span className="bg-purple-100 text-purple-800 px-2 py-0.5 rounded text-[10px] font-bold">SPEC UPDATE</span>;
      default:
        return <span className="bg-slate-100 text-slate-800 px-2 py-0.5 rounded text-[10px] font-bold">{type}</span>;
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6 font-sans">
      
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs font-semibold text-slate-500">
        <Link href="/admin/intelligence" className="hover:text-brand-600 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Vehicle Intelligence</span>
        </Link>
        <span>/</span>
        <span className="text-slate-800 font-bold">Change & Price Audit Log</span>
      </div>

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-black text-navy-950">Vehicle Modification History</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Immutable log of price revisions, variant introductions, and OEM specification updates.
          </p>
        </div>

        <Link
          href="/admin/intelligence"
          className="px-3.5 py-2 border border-slate-200 hover:bg-slate-50 text-slate-700 font-semibold text-xs rounded-xl"
        >
          Intelligence Overview
        </Link>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-16 text-center text-xs text-slate-400">Loading audit history...</div>
        ) : history.length === 0 ? (
          <div className="p-16 text-center text-xs text-slate-400">
            No specification or price changes logged yet.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 font-bold uppercase">
                  <th className="py-3 px-4">Vehicle Model</th>
                  <th className="py-3 px-4">Change Event</th>
                  <th className="py-3 px-4">Modification Details</th>
                  <th className="py-3 px-4">Source Attribution</th>
                  <th className="py-3 px-4">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {history.map((h) => (
                  <tr key={h.id} className="hover:bg-slate-50">
                    <td className="py-3.5 px-4 font-bold text-navy-950">
                      {h.model_name || 'Vehicle Item'}
                    </td>
                    <td className="py-3.5 px-4">
                      {getChangeTypeBadge(h.change_type)}
                    </td>
                    <td className="py-3.5 px-4 text-slate-700">
                      {h.change_type === 'PRICE_REVISION' && h.previous_data && h.new_data ? (
                        <span>
                          ₹{Number(h.previous_data.reference_min || 0).toLocaleString('en-IN')} →{' '}
                          <strong className="text-emerald-700">
                            ₹{Number(h.new_data.reference_min || 0).toLocaleString('en-IN')}
                          </strong>
                        </span>
                      ) : h.new_data ? (
                        <span className="font-mono text-[11px] text-slate-600">
                          {JSON.stringify(h.new_data)}
                        </span>
                      ) : (
                        <span className="text-slate-400">Standard sync</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-slate-500">
                      {h.source_name || 'OEM Newsroom'}
                      {h.source_url && (
                        <a
                          href={h.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-0.5 text-brand-600 hover:underline ml-1.5"
                        >
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-slate-400">
                      {new Date(h.changed_at).toLocaleString('en-IN', {
                        day: 'numeric',
                        month: 'short',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
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

