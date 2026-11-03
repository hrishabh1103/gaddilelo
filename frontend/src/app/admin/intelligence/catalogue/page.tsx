'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { 
  Database, RefreshCw, CheckCircle2, AlertTriangle, XCircle, 
  Layers, ShieldCheck, Eye, ArrowRight, Clock, FileText, Check, Car
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { apiFetch } from '@/lib/api';

export default function AdminCatalogueManagementPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [syncLoading, setSyncLoading] = useState(false);
  const [previewData, setPreviewData] = useState<any>(null);
  const [syncResult, setSyncResult] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    if (!isLoading) {
      if (!user || user.role !== 'ADMIN') {
        router.push('/login');
        return;
      }
    }

    async function loadSummary() {
      try {
        const data = await apiFetch('/intelligence/admin/catalogue-summary');
        setSummary(data);
      } catch (err: any) {
        console.error(err);
        setErrorMsg(err.message || 'Failed to load catalogue summary');
      } finally {
        setLoading(false);
      }
    }

    if (user && user.role === 'ADMIN') {
      loadSummary();
    }
  }, [user, isLoading, router]);

  const handleFetchPreview = async () => {
    setPreviewLoading(true);
    setErrorMsg('');
    try {
      const res = await apiFetch('/intelligence/meterapp/preview', { method: 'POST' });
      setPreviewData(res);
    } catch (e: any) {
      setErrorMsg(e.message || 'Failed to generate preview');
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleExecuteSync = async () => {
    if (!confirm('Are you sure you want to run the MeterApp Canonical Catalogue synchronization? Existing variants and groups will be safely preserved.')) {
      return;
    }
    setSyncLoading(true);
    setErrorMsg('');
    try {
      const res = await apiFetch('/intelligence/meterapp/sync', { method: 'POST' });
      setSyncResult(res);
      // Reload summary
      const updated = await apiFetch('/intelligence/admin/catalogue-summary');
      setSummary(updated);
    } catch (e: any) {
      setErrorMsg(e.message || 'Sync failed');
    } finally {
      setSyncLoading(false);
    }
  };

  if (isLoading || loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-sm text-slate-400">
        Loading Catalogue Management Console...
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 font-sans">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-2.5 py-0.5 rounded border border-blue-200">
              MeterApp Canonical Integration
            </span>
            <span className="text-xs text-slate-400">• ISC License • Zero-Loss Deduplication</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-navy-950 mt-1">
            Indian Vehicle Catalogue Management
          </h1>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleFetchPreview}
            disabled={previewLoading || syncLoading}
            className="px-4 py-2 border border-slate-300 hover:bg-slate-50 text-slate-800 font-bold text-xs rounded-xl shadow-sm transition-all flex items-center gap-1.5 disabled:opacity-50"
          >
            <Eye className="w-3.5 h-3.5 text-blue-600" />
            <span>{previewLoading ? 'Generating Preview...' : 'Preview Ingestion'}</span>
          </button>

          <button
            onClick={handleExecuteSync}
            disabled={syncLoading || previewLoading}
            className="px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs rounded-xl shadow-sm transition-all flex items-center gap-1.5 disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${syncLoading ? 'animate-spin' : ''}`} />
            <span>{syncLoading ? 'Synchronizing...' : 'Sync MeterApp Catalogue'}</span>
          </button>
          
          <Link
            href="/admin/intelligence"
            className="px-3.5 py-2 border border-slate-200 hover:bg-slate-50 text-slate-700 font-semibold text-xs rounded-xl transition-colors"
          >
            Intelligence Overview
          </Link>
        </div>
      </div>

      {/* Navigation Sub-Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-2 text-xs font-bold text-slate-600">
        <Link href="/admin/intelligence" className="px-3 py-1.5 rounded-lg hover:bg-slate-100 text-slate-700">
          Overview
        </Link>
        <Link href="/admin/intelligence/catalogue" className="px-3 py-1.5 rounded-lg bg-slate-900 text-white">
          Catalogue & Provenance
        </Link>
        <Link href="/admin/intelligence/queue" className="px-3 py-1.5 rounded-lg hover:bg-slate-100 text-slate-700">
          Discovery Queue
        </Link>
        <Link href="/admin/intelligence/sources" className="px-3 py-1.5 rounded-lg hover:bg-slate-100 text-slate-700">
          Data Sources
        </Link>
      </div>

      {errorMsg && (
        <div className="p-4 bg-red-50 text-red-800 text-xs rounded-xl border border-red-200 flex items-center gap-2">
          <XCircle className="w-4 h-4 text-red-600 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {syncResult && (
        <div className="p-4 bg-emerald-50 text-emerald-900 text-xs rounded-xl border border-emerald-200 space-y-1">
          <div className="flex items-center gap-2 font-bold text-sm">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>Synchronization Succeeded!</span>
          </div>
          <p>
            Processed <strong>{syncResult.records_processed}</strong> records, imported <strong>{syncResult.records_imported}</strong> new models, 
            deduplicated and updated <strong>{syncResult.records_updated}</strong> models, and created <strong>{syncResult.variants_created}</strong> verified OEM variants in {syncResult.duration_seconds}s.
          </p>
        </div>
      )}

      {/* Primary Telemetry Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <div className="text-xs font-semibold text-slate-400">Total Brands</div>
          <div className="text-2xl font-black text-navy-950">{summary?.totals?.brands || 0}</div>
          <div className="text-[11px] text-slate-500">Across 2W, 3W, 4W & CVs</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <div className="text-xs font-semibold text-slate-400">Total Models</div>
          <div className="text-2xl font-black text-blue-600">{summary?.totals?.models || 0}</div>
          <div className="text-[11px] text-slate-500">Canonical vehicle identities</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <div className="text-xs font-semibold text-slate-400">Active Variants</div>
          <div className="text-2xl font-black text-emerald-600">{summary?.totals?.variants || 0}</div>
          <div className="text-[11px] text-slate-500">Powertrains, trims & pricing</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <div className="text-xs font-semibold text-slate-400">MeterApp Canonical</div>
          <div className="text-2xl font-black text-purple-600">{summary?.provenance?.meterapp_canonical_models || 0}</div>
          <div className="text-[11px] text-slate-500">Under verified ISC License</div>
        </div>

      </div>

      {/* Preview Ingestion Modal / Drawer */}
      {previewData && (
        <div className="bg-blue-50/50 rounded-2xl border border-blue-200 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Eye className="w-5 h-5 text-blue-600" />
              <h3 className="font-bold text-base text-navy-950">MeterApp Ingestion Preview (Dry Run)</h3>
            </div>
            <button
              onClick={() => setPreviewData(null)}
              className="text-xs text-slate-400 hover:text-slate-600"
            >
              Close Preview
            </button>
          </div>

          <p className="text-xs text-slate-600">
            Previewing analysis of <strong>{previewData.total_records_analyzed}</strong> vehicle models from MeterApp dataset.
            Zero records will be deleted or modified until synchronization is confirmed.
          </p>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div className="p-3 bg-white rounded-xl border border-blue-100">
              <div className="text-slate-400">New Brands to Create</div>
              <div className="text-lg font-black text-blue-700">{previewData.brands?.to_create_count}</div>
              <div className="text-[10px] text-slate-400 truncate">{previewData.brands?.to_create?.join(', ')}</div>
            </div>
            <div className="p-3 bg-white rounded-xl border border-blue-100">
              <div className="text-slate-400">Existing Brands Enriched</div>
              <div className="text-lg font-black text-emerald-700">{previewData.brands?.to_update_count}</div>
            </div>
            <div className="p-3 bg-white rounded-xl border border-blue-100">
              <div className="text-slate-400">New Models to Import</div>
              <div className="text-lg font-black text-blue-700">{previewData.models?.to_create_count}</div>
            </div>
            <div className="p-3 bg-white rounded-xl border border-blue-100">
              <div className="text-slate-400">Deduplicated Models</div>
              <div className="text-lg font-black text-purple-700">{previewData.models?.deduplicated_existing_count}</div>
            </div>
          </div>

          {/* Sample Models to Create */}
          {previewData.sample_new_models?.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-xs font-bold text-slate-700">Sample Candidate Models to Import:</h4>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                {previewData.sample_new_models.slice(0, 6).map((m: any, idx: number) => (
                  <div key={idx} className="p-2.5 bg-white rounded-lg border border-slate-200 text-xs flex justify-between items-center">
                    <div>
                      <div className="font-bold text-navy-950">{m.brand_name} {m.model_name}</div>
                      <div className="text-[10px] text-slate-400 capitalize">{m.category}</div>
                    </div>
                    {m.has_verified_oem_variants && (
                      <span className="text-[9px] bg-emerald-100 text-emerald-800 font-bold px-1.5 py-0.5 rounded">
                        OEM Specs
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="pt-2 flex justify-end">
            <button
              onClick={handleExecuteSync}
              disabled={syncLoading}
              className="px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs rounded-xl shadow-sm transition-all flex items-center gap-1.5"
            >
              <Check className="w-3.5 h-3.5" />
              <span>Confirm & Execute Synchronization</span>
            </button>
          </div>
        </div>
      )}

      {/* Catalogue Health & Diagnostics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Data Quality & Missing Attributes */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-base text-navy-950 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-orange-500" />
              <span>Specification & Image Completeness</span>
            </h3>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex justify-between items-center p-3 bg-slate-50 rounded-xl">
              <div>
                <span className="font-bold text-slate-800">Models Missing Trims/Variants</span>
                <p className="text-[11px] text-slate-500">Will use baseline pricing until OEM specs verified</p>
              </div>
              <span className="font-bold text-orange-600 px-2 py-0.5 bg-orange-100 rounded-md">
                {summary?.data_health?.models_missing_variants || 0}
              </span>
            </div>

            <div className="flex justify-between items-center p-3 bg-slate-50 rounded-xl">
              <div>
                <span className="font-bold text-slate-800">Models Missing Dimensions</span>
                <p className="text-[11px] text-slate-500">Length, width, height, wheelbase</p>
              </div>
              <span className="font-bold text-slate-700 px-2 py-0.5 bg-slate-200 rounded-md">
                {summary?.data_health?.models_missing_specs || 0}
              </span>
            </div>

            <div className="flex justify-between items-center p-3 bg-slate-50 rounded-xl">
              <div>
                <span className="font-bold text-slate-800">Models Using Image Placeholders</span>
                <p className="text-[11px] text-slate-500">Auto-fallback active; Wikimedia search ready</p>
              </div>
              <span className="font-bold text-blue-600 px-2 py-0.5 bg-blue-100 rounded-md">
                {summary?.data_health?.models_missing_images || 0}
              </span>
            </div>
          </div>
        </div>

        {/* Provenance & Synchronization Logs */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-base text-navy-950 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>Legal Provenance & Sync History</span>
            </h3>
          </div>

          <div className="text-xs space-y-3">
            <div className="p-3 bg-slate-50 rounded-xl space-y-1">
              <div className="font-bold text-slate-800">Master Dataset License</div>
              <div className="text-[11px] text-slate-600">
                Primary Identity: <strong className="text-emerald-700">{summary?.provenance?.meterapp_license}</strong>
              </div>
              <div className="text-[11px] text-slate-500 italic">
                {summary?.provenance?.attribution}
              </div>
            </div>

            <div className="space-y-2">
              <div className="font-bold text-slate-700 text-xs">Recent Synchronization Runs:</div>
              {summary?.recent_syncs?.map((s: any, idx: number) => (
                <div key={idx} className="p-2.5 bg-slate-50 rounded-lg text-xs flex justify-between items-center">
                  <div>
                    <span className="font-bold text-slate-800">{s.dataset_name}</span>
                    <span className="text-[10px] text-slate-400 ml-2">
                      {s.completed_at ? new Date(s.completed_at).toLocaleDateString() : 'Active'}
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="font-bold text-emerald-600">+{s.imported} new</span>
                    <span className="text-[10px] text-slate-400 ml-1.5">({s.updated} deduplicated)</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>

    </div>
  );
}

