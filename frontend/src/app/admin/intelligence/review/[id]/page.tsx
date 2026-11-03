'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { 
  ArrowLeft, CheckCircle2, XCircle, ShieldCheck, ExternalLink, 
  Car, Layers, AlertCircle, Building2, Sparkles, Send, Users, Eye
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { apiFetch } from '@/lib/api';

export default function VehicleReviewDetailPage() {
  const { id } = useParams() as { id: string };
  const { user, isLoading } = useAuth();
  const router = useRouter();

  const [record, setRecord] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [adminNotes, setAdminNotes] = useState('');
  const [actionLoading, setActionLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    if (!isLoading) {
      if (!user || user.role !== 'ADMIN') {
        router.push('/login');
        return;
      }
    }

    async function loadRecord() {
      try {
        const data = await apiFetch(`/intelligence/records/${id}`);
        setRecord(data);
        if (data.admin_notes) setAdminNotes(data.admin_notes);
      } catch (e: any) {
        setMessage({ type: 'error', text: e.message || 'Failed to load record' });
      } finally {
        setLoading(false);
      }
    }

    if (user && user.role === 'ADMIN' && id) {
      loadRecord();
    }
  }, [user, isLoading, router, id]);

  const handleApprove = async () => {
    setActionLoading(true);
    setMessage(null);
    try {
      const res = await apiFetch(`/intelligence/records/${id}/approve`, {
        method: 'POST',
        body: JSON.stringify({ admin_notes: adminNotes }),
      });
      setMessage({
        type: 'success',
        text: `Vehicle '${res.model_name}' approved and published to live catalogue! Subscribed buyers have been notified.`
      });
      // Refresh record
      const updated = await apiFetch(`/intelligence/records/${id}`);
      setRecord(updated);
    } catch (e: any) {
      setMessage({ type: 'error', text: e.message || 'Approval failed' });
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    setActionLoading(true);
    setMessage(null);
    try {
      await apiFetch(`/intelligence/records/${id}/reject`, {
        method: 'POST',
        body: JSON.stringify({ admin_notes: adminNotes }),
      });
      setMessage({ type: 'success', text: 'Discovery record has been rejected.' });
      const updated = await apiFetch(`/intelligence/records/${id}`);
      setRecord(updated);
    } catch (e: any) {
      setMessage({ type: 'error', text: e.message || 'Rejection failed' });
    } finally {
      setActionLoading(false);
    }
  };

  if (isLoading || loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-xs text-slate-400 font-sans">
        Loading vehicle verification dossier...
      </div>
    );
  }

  if (!record) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-xs text-slate-500 font-sans">
        Record not found or failed to load.
      </div>
    );
  }

  const extracted = record.extracted_data || {};
  const variants = extracted.variants || [];

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6 font-sans">
      
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs font-semibold text-slate-500">
        <Link href="/admin/intelligence/queue" className="hover:text-brand-600 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Discovery Queue</span>
        </Link>
        <span>/</span>
        <span className="text-slate-800 font-bold">{record.discovered_brand} {record.discovered_model}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold uppercase ${
              record.review_status === 'APPROVED' 
                ? 'bg-emerald-100 text-emerald-800' 
                : record.review_status === 'REJECTED'
                ? 'bg-red-100 text-red-800'
                : 'bg-orange-100 text-orange-800'
            }`}>
              {record.review_status}
            </span>
            <span className="text-xs text-slate-400">
              Confidence: <strong>{(Number(record.confidence_score) * 100).toFixed(0)}%</strong>
            </span>
            {record.subscribers_count > 0 && (
              <span className="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded border border-blue-200 flex items-center gap-1">
                <Users className="w-3 h-3" />
                {record.subscribers_count} Customer(s) Subscribed
              </span>
            )}
          </div>
          
          <h1 className="text-2xl sm:text-3xl font-black text-navy-950 mt-1">
            {record.discovered_brand} {record.discovered_model}
          </h1>
        </div>

        <div className="flex items-center gap-2">
          {record.published_model_id && (
            <Link
              href={`/vehicles/${record.published_model_id}`}
              className="px-3.5 py-2 bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs rounded-xl flex items-center gap-1.5"
            >
              <Eye className="w-3.5 h-3.5" />
              <span>View Live Catalogue</span>
            </Link>
          )}
        </div>
      </div>

      {message && (
        <div className={`p-4 rounded-xl text-xs flex items-center gap-2 border ${
          message.type === 'success' 
            ? 'bg-emerald-50 text-emerald-800 border-emerald-200' 
            : 'bg-red-50 text-red-800 border-red-200'
        }`}>
          {message.type === 'success' ? <CheckCircle2 className="w-4 h-4 flex-shrink-0" /> : <AlertCircle className="w-4 h-4 flex-shrink-0" />}
          <span>{message.text}</span>
        </div>
      )}

      {/* Main Dossier Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left 2 Cols: Extracted Details & Variants */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Metadata Card */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <h3 className="font-bold text-sm text-navy-950 border-b border-slate-100 pb-2">
              Vehicle Classification & Source Attribution
            </h3>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Brand</span>
                <span className="font-bold text-navy-900">{record.discovered_brand}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Model</span>
                <span className="font-bold text-navy-900">{record.discovered_model}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Category</span>
                <span className="font-bold uppercase text-navy-900">{record.category_slug}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Body Type</span>
                <span className="font-bold text-navy-900">{record.body_type}</span>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-100 grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Source Provider</span>
                <span className="font-semibold text-slate-800">{record.primary_source_name || 'Official OEM'}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Source URL</span>
                {record.primary_source_url ? (
                  <a
                    href={record.primary_source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-brand-600 hover:underline truncate block"
                  >
                    {record.primary_source_url}
                  </a>
                ) : (
                  <span className="text-slate-400">Direct Newsroom Docket</span>
                )}
              </div>
            </div>
          </div>

          {/* Variants Table */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-2">
              <h3 className="font-bold text-sm text-navy-950">
                Extracted Variants ({variants.length})
              </h3>
              <span className="text-xs text-slate-400">Normalized Powertrain & Pricing</span>
            </div>

            {variants.length === 0 ? (
              <p className="text-xs text-slate-400">No variant records extracted.</p>
            ) : (
              <div className="space-y-3">
                {variants.map((v: any, idx: number) => (
                  <div key={idx} className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-sm text-navy-950">{v.variant_name || v.name}</span>
                      <span className="font-black text-brand-700">
                        ₹{Number(v.reference_ex_showroom || v.price || 0).toLocaleString('en-IN')}*
                      </span>
                    </div>

                    <div className="flex flex-wrap gap-2 text-[11px] text-slate-600">
                      <span className="bg-white px-2 py-0.5 rounded border border-slate-200 font-semibold">
                        Fuel: {v.fuel_type}
                      </span>
                      <span className="bg-white px-2 py-0.5 rounded border border-slate-200 font-semibold">
                        Transmission: {v.transmission}
                      </span>
                      {v.engine_cc_or_battery_kwh && (
                        <span className="bg-white px-2 py-0.5 rounded border border-slate-200 font-semibold">
                          Capacity: {v.engine_cc_or_battery_kwh}
                        </span>
                      )}
                    </div>

                    {v.specifications && Object.keys(v.specifications).length > 0 && (
                      <div className="pt-1.5 border-t border-slate-200/60 text-[10px] text-slate-500 grid grid-cols-2 sm:grid-cols-3 gap-1">
                        {Object.entries(v.specifications).map(([k, val]: [string, any]) => (
                          <div key={k}>
                            <span className="font-semibold capitalize">{k.replace('_', ' ')}:</span> {String(val)}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Field Attribution Sources */}
          {record.spec_sources && record.spec_sources.length > 0 && (
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
              <h3 className="font-bold text-sm text-navy-950 border-b border-slate-100 pb-2">
                Field-Level Citations & Verification Audit
              </h3>
              <div className="space-y-2 max-h-60 overflow-y-auto text-xs">
                {record.spec_sources.map((s: any, idx: number) => (
                  <div key={idx} className="p-2.5 bg-slate-50 rounded-xl flex items-center justify-between">
                    <div>
                      <span className="font-bold text-slate-700">{s.field_name}</span>
                      <span className="text-slate-500 ml-2">= {s.field_value}</span>
                    </div>
                    <span className="text-[10px] bg-slate-200 text-slate-700 px-2 py-0.5 rounded font-mono">
                      {s.source_name}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>

        {/* Right Col: Admin Verification Controls */}
        <div className="space-y-6">
          
          {/* Action Box */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <h3 className="font-bold text-sm text-navy-950 border-b border-slate-100 pb-2">
              Administrative Action
            </h3>

            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-700">Verification Notes</label>
              <textarea
                value={adminNotes}
                onChange={(e) => setAdminNotes(e.target.value)}
                placeholder="e.g. Cross-verified with official OEM launch docket and RTO tax slabs in MP."
                rows={4}
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
            </div>

            <div className="pt-2 space-y-2">
              <button
                onClick={handleApprove}
                disabled={actionLoading || record.review_status === 'APPROVED'}
                className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs uppercase tracking-wider rounded-xl shadow-md transition-all flex items-center justify-center gap-1.5 disabled:opacity-50"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>{record.review_status === 'APPROVED' ? 'Already Approved' : 'Approve & Publish to Catalogue'}</span>
              </button>

              <button
                onClick={handleReject}
                disabled={actionLoading || record.review_status === 'REJECTED'}
                className="w-full py-2.5 bg-red-50 hover:bg-red-100 text-red-700 font-bold text-xs uppercase tracking-wider rounded-xl transition-all flex items-center justify-center gap-1.5 disabled:opacity-50"
              >
                <XCircle className="w-4 h-4" />
                <span>Reject Candidate</span>
              </button>
            </div>

            <p className="text-[10px] text-slate-400 text-center leading-relaxed">
              Approval will create the Brand, Model, and Variants in the live database and automatically dispatch notifications to all interested customers.
            </p>
          </div>

          {/* Vehicle Imagery */}
          {record.images && record.images.length > 0 && (
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
              <h3 className="font-bold text-sm text-navy-950">Extracted Imagery</h3>
              <div className="rounded-xl overflow-hidden aspect-[16/10] bg-slate-100 border border-slate-200">
                <img
                  src={record.images[0].image_url}
                  alt={record.discovered_model}
                  className="w-full h-full object-cover"
                />
              </div>
              <p className="text-[10px] text-slate-400">
                Usage Rights: {record.images[0].usage_rights_status || 'OFFICIAL_OEM_PRESS'}
              </p>
            </div>
          )}

        </div>

      </div>

    </div>
  );
}

