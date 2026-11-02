'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { History, ArrowLeft, Shield } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { apiFetch } from '@/lib/api';

export default function AdminAuditPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoading) {
      if (!user) {
        router.push('/login?redirect=/admin/audit');
        return;
      }
      if (user.role !== 'ADMIN') {
        router.push('/dashboard');
        return;
      }
    }

    async function loadLogs() {
      try {
        const data = await apiFetch('/admin/audit-logs');
        setLogs(data || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    if (user && user.role === 'ADMIN') {
      loadLogs();
    }
  }, [user, isLoading, router]);

  if (isLoading || loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-sm text-slate-400">
        Loading audit trail...
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
            System Audit Trail
          </h1>
          <p className="text-xs sm:text-sm text-slate-500">
            Immutable log of state machine updates, dealership verifications, and pricing interventions.
          </p>
        </div>
      </div>

      {logs.length === 0 ? (
        <div className="p-16 bg-white rounded-3xl border border-slate-200 text-center text-xs text-slate-400">
          No audit logs recorded yet
        </div>
      ) : (
        <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden overflow-x-auto">
          <table className="w-full text-xs text-left border-collapse min-w-[700px]">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-700">
                <th className="p-4 font-bold">Timestamp</th>
                <th className="p-4 font-bold">Action</th>
                <th className="p-4 font-bold">Entity Type</th>
                <th className="p-4 font-bold">Entity ID</th>
                <th className="p-4 font-bold">Payload Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-mono text-[11px]">
              {logs.map((l) => (
                <tr key={l.id} className="hover:bg-slate-50/50">
                  <td className="p-4 text-slate-500 font-sans">
                    {new Date(l.created_at).toLocaleString()}
                  </td>
                  <td className="p-4">
                    <span className="px-2 py-0.5 rounded font-bold bg-purple-50 text-purple-700 border border-purple-100">
                      {l.action}
                    </span>
                  </td>
                  <td className="p-4 font-semibold text-slate-700 font-sans">{l.entity_type}</td>
                  <td className="p-4 text-slate-500">{l.entity_id.slice(0, 8)}...</td>
                  <td className="p-4 text-slate-600 font-sans">
                    {JSON.stringify(l.payload)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

    </div>
  );
}
