'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { 
  ArrowLeft, Database, Plus, CheckCircle2, XCircle, 
  RefreshCw, AlertCircle, ExternalLink 
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { apiFetch } from '@/lib/api';

export default function SourceManagementPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  const [sources, setSources] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [sourceName, setSourceName] = useState('');
  const [sourceUrl, setSourceUrl] = useState('');
  const [sourceType, setSourceType] = useState('MANUFACTURER_WEBSITE');
  const [accessMethod, setAccessMethod] = useState('RSS_FEED');
  const [updateFreq, setUpdateFreq] = useState('DAILY');
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!isLoading) {
      if (!user || user.role !== 'ADMIN') {
        router.push('/login');
        return;
      }
    }

    async function loadSources() {
      try {
        const data = await apiFetch('/intelligence/sources');
        setSources(data || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    if (user && user.role === 'ADMIN') {
      loadSources();
    }
  }, [user, isLoading, router]);

  const handleAddSource = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage('');
    try {
      await apiFetch('/intelligence/sources', {
        method: 'POST',
        body: JSON.stringify({
          source_name: sourceName,
          source_url: sourceUrl,
          source_type: sourceType,
          access_method: accessMethod,
          update_frequency: updateFreq,
          licensing_status: 'OFFICIAL_PUBLIC',
          enabled: true,
        }),
      });
      setMessage('Source added successfully!');
      setShowAddForm(false);
      setSourceName('');
      setSourceUrl('');
      // Reload
      const data = await apiFetch('/intelligence/sources');
      setSources(data || []);
    } catch (e: any) {
      setMessage(e.message || 'Failed to add source');
    } finally {
      setSubmitting(false);
    }
  };

  const handleToggleSource = async (sourceId: string, currentEnabled: boolean) => {
    try {
      await apiFetch(`/intelligence/sources/${sourceId}`, {
        method: 'PUT',
        body: JSON.stringify({ enabled: !currentEnabled }),
      });
      setSources(prev => prev.map(s => s.id === sourceId ? { ...s, enabled: !currentEnabled } : s));
    } catch (e: any) {
      alert(e.message || 'Update failed');
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
        <span className="text-slate-800 font-bold">Data Source Management</span>
      </div>

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-black text-navy-950">Automotive Data Providers</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Configure permitted manufacturer pressrooms, licensed APIs, and automated scanning cadences.
          </p>
        </div>

        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs rounded-xl transition-colors flex items-center gap-1.5 self-start sm:self-auto shadow-xs"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>{showAddForm ? 'Cancel' : 'Add New Data Source'}</span>
        </button>
      </div>

      {message && (
        <div className="p-3 bg-emerald-50 text-emerald-800 text-xs rounded-xl border border-emerald-200 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
          <span>{message}</span>
        </div>
      )}

      {/* Add Source Form Modal / Collapse */}
      {showAddForm && (
        <form onSubmit={handleAddSource} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4 max-w-2xl">
          <h3 className="font-bold text-sm text-navy-950">Register New Automotive Data Provider</h3>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="space-y-1">
              <label className="font-bold text-slate-700">Source Name *</label>
              <input
                type="text"
                value={sourceName}
                onChange={(e) => setSourceName(e.target.value)}
                placeholder="e.g. Maruti Suzuki Official Newsroom"
                required
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
            </div>

            <div className="space-y-1">
              <label className="font-bold text-slate-700">Base URL / Feed Endpoint *</label>
              <input
                type="url"
                value={sourceUrl}
                onChange={(e) => setSourceUrl(e.target.value)}
                placeholder="https://press.marutisuzuki.com/feed"
                required
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
            </div>

            <div className="space-y-1">
              <label className="font-bold text-slate-700">Source Type</label>
              <select
                value={sourceType}
                onChange={(e) => setSourceType(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-800 focus:outline-none"
              >
                <option value="MANUFACTURER_WEBSITE">Manufacturer Official Website</option>
                <option value="PRESS_RELEASE">Official Press Release / Media Feed</option>
                <option value="LICENSED_API">Licensed Automotive API</option>
                <option value="PUBLIC_PORTAL">Permitted Public Sitemaps</option>
              </select>
            </div>

            <div className="space-y-1">
              <label className="font-bold text-slate-700">Update Frequency</label>
              <select
                value={updateFreq}
                onChange={(e) => setUpdateFreq(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-800 focus:outline-none"
              >
                <option value="DAILY">Daily Scan</option>
                <option value="WEEKLY">Weekly Scan</option>
                <option value="MANUAL">Manual Trigger Only</option>
              </select>
            </div>
          </div>

          <div className="pt-2 flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setShowAddForm(false)}
              className="px-4 py-2 border border-slate-200 text-xs font-bold text-slate-600 rounded-xl"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-5 py-2 bg-brand-600 text-white text-xs font-bold rounded-xl disabled:opacity-50"
            >
              {submitting ? 'Registering...' : 'Register Source'}
            </button>
          </div>
        </form>
      )}

      {/* Sources Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-16 text-center text-xs text-slate-400">Loading data sources...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 font-bold uppercase">
                  <th className="py-3 px-4">Source Name</th>
                  <th className="py-3 px-4">Type</th>
                  <th className="py-3 px-4">Licensing</th>
                  <th className="py-3 px-4">Cadence</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Toggle</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {sources.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-50">
                    <td className="py-3.5 px-4 font-bold text-navy-950">
                      {s.source_name}
                      <span className="block text-[10px] text-slate-400 font-normal truncate max-w-sm">
                        {s.source_url}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 uppercase text-slate-600">
                      {s.source_type.replace('_', ' ')}
                    </td>
                    <td className="py-3.5 px-4 text-slate-500">
                      <span className="text-[10px] bg-slate-100 px-2 py-0.5 rounded font-mono">
                        {s.licensing_status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-600 font-medium">
                      {s.update_frequency}
                    </td>
                    <td className="py-3.5 px-4">
                      {s.enabled ? (
                        <span className="text-emerald-700 font-bold flex items-center gap-1">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                          <span>Active</span>
                        </span>
                      ) : (
                        <span className="text-slate-400 font-semibold flex items-center gap-1">
                          <XCircle className="w-3.5 h-3.5 text-slate-400" />
                          <span>Disabled</span>
                        </span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => handleToggleSource(s.id, s.enabled)}
                        className={`px-3 py-1 rounded-lg text-xs font-bold transition-colors ${
                          s.enabled
                            ? 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                            : 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100'
                        }`}
                      >
                        {s.enabled ? 'Disable' : 'Enable'}
                      </button>
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

