'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { 
  Building2, ShieldCheck, CheckCircle2, XCircle, ArrowLeft, 
  MapPin, Phone, Mail, AlertCircle, Clock 
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { apiFetch } from '@/lib/api';

export default function AdminDealersPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  const [dealers, setDealers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [feedback, setFeedback] = useState('');

  useEffect(() => {
    if (!isLoading) {
      if (!user) {
        router.push('/login?redirect=/admin/dealers');
        return;
      }
      if (user.role !== 'ADMIN') {
        router.push('/dashboard');
        return;
      }
    }

    async function loadDealers() {
      try {
        const data = await apiFetch('/admin/dealers');
        setDealers(data || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    if (user && user.role === 'ADMIN') {
      loadDealers();
    }
  }, [user, isLoading, router]);

  const handleVerify = async (dealerId: string, status: 'VERIFIED' | 'REJECTED') => {
    setActionLoading(dealerId);
    setFeedback('');
    try {
      const notes = status === 'VERIFIED' 
        ? 'Verified against MP OEM dealership franchise registry.' 
        : 'Missing required GSTIN documentation or dealership trade certificate.';

      await apiFetch(`/admin/dealers/${dealerId}/verify`, {
        method: 'PUT',
        body: JSON.stringify({
          verification_status: status,
          verification_notes: notes,
        }),
      });

      setDealers(prev => prev.map(d => d.id === dealerId ? { ...d, verification_status: status, verification_notes: notes } : d));
      setFeedback(`Dealership ${status === 'VERIFIED' ? 'verified' : 'rejected'} successfully.`);
    } catch (err: any) {
      setFeedback(err.message || 'Verification update failed');
    } finally {
      setActionLoading(null);
    }
  };

  if (isLoading || loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-sm text-slate-400">
        Loading dealerships...
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
            Dealership Verification & Governance
          </h1>
          <p className="text-xs sm:text-sm text-slate-500">
            Verify OEM trade franchises and authorized dealership partners in Indore pilot territory.
          </p>
        </div>
      </div>

      {feedback && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-xl flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 flex-shrink-0 text-emerald-600" />
          <span>{feedback}</span>
        </div>
      )}

      {/* Dealerships Table */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden overflow-x-auto">
        <table className="w-full text-xs text-left border-collapse min-w-[750px]">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200 text-slate-700">
              <th className="p-4 font-bold">Dealership Details</th>
              <th className="p-4 font-bold">GSTIN & Entity</th>
              <th className="p-4 font-bold">Authorized Brands</th>
              <th className="p-4 font-bold">Status</th>
              <th className="p-4 font-bold text-right">Verification Action</th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-100">
            {dealers.map((d) => (
              <tr key={d.id} className="hover:bg-slate-50/50">
                <td className="p-4">
                  <div className="font-bold text-sm text-navy-950">{d.dealership_name}</div>
                  <div className="text-[11px] text-slate-500 mt-0.5">{d.address}</div>
                  <div className="text-[10px] text-slate-400 mt-1">
                    Contact: {d.contact_name} ({d.contact_phone})
                  </div>
                </td>

                <td className="p-4">
                  <div className="font-mono font-bold text-slate-900">{d.gstin}</div>
                  <div className="text-[11px] text-slate-500 mt-0.5">{d.legal_entity_name}</div>
                </td>

                <td className="p-4">
                  <div className="flex flex-wrap gap-1">
                    {d.authorized_brands?.map((brand: string, i: number) => (
                      <span key={i} className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-[10px] font-semibold border border-blue-100">
                        {brand}
                      </span>
                    ))}
                  </div>
                </td>

                <td className="p-4">
                  <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                    d.verification_status === 'VERIFIED'
                      ? 'bg-emerald-100 text-emerald-800'
                      : d.verification_status === 'REJECTED'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-amber-100 text-amber-800'
                  }`}>
                    {d.verification_status}
                  </span>
                  {d.verification_notes && (
                    <div className="text-[10px] text-slate-500 mt-1 italic max-w-xs">
                      {d.verification_notes}
                    </div>
                  )}
                </td>

                <td className="p-4 text-right">
                  <div className="flex items-center justify-end gap-2">
                    <button
                      onClick={() => handleVerify(d.id, 'VERIFIED')}
                      disabled={actionLoading === d.id || d.verification_status === 'VERIFIED'}
                      className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-40 text-white font-semibold text-xs rounded-xl shadow-sm transition-colors flex items-center gap-1"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      Approve
                    </button>
                    <button
                      onClick={() => handleVerify(d.id, 'REJECTED')}
                      disabled={actionLoading === d.id || d.verification_status === 'REJECTED'}
                      className="px-3 py-1.5 bg-red-600 hover:bg-red-700 disabled:opacity-40 text-white font-semibold text-xs rounded-xl shadow-sm transition-colors flex items-center gap-1"
                    >
                      <XCircle className="w-3.5 h-3.5" />
                      Reject
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </div>
  );
}
