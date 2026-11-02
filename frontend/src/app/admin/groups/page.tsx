'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { 
  Users, Sparkles, Clock, CheckCircle2, ArrowLeft, 
  Send, AlertCircle, ArrowRight, Building2, MapPin 
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { apiFetch } from '@/lib/api';

export default function AdminGroupsPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  const [groups, setGroups] = useState<any[]>([]);
  const [dealers, setDealers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const [feedback, setFeedback] = useState('');

  useEffect(() => {
    if (!isLoading) {
      if (!user) {
        router.push('/login?redirect=/admin/groups');
        return;
      }
      if (user.role !== 'ADMIN') {
        router.push('/dashboard');
        return;
      }
    }

    async function loadData() {
      try {
        const [gData, dData] = await Promise.all([
          apiFetch('/admin/groups'),
          apiFetch<any[]>('/admin/dealers'),
        ]);
        setGroups(gData || []);
        setDealers(dData?.filter((d: any) => d.verification_status === 'VERIFIED') || []);
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

  const handleStatusChange = async (groupId: string, newStatus: string) => {
    setUpdatingId(groupId);
    setFeedback('');
    try {
      const payload: any = { status: newStatus };
      if (newStatus === 'BIDDING_OPEN') {
        // Set bidding deadline 5 days out
        payload.bidding_end_time = new Date(Date.now() + 5 * 86400000).toISOString();
      }

      await apiFetch(`/admin/groups/${groupId}/status`, {
        method: 'PUT',
        body: JSON.stringify(payload),
      });

      setGroups(prev => prev.map(g => g.id === groupId ? { ...g, status: newStatus } : g));
      setFeedback(`Group status successfully transitioned to ${newStatus}.`);
    } catch (err: any) {
      setFeedback(err.message || 'Status transition failed');
    } finally {
      setUpdatingId(null);
    }
  };

  const handleInviteAllVerifiedDealers = async (groupId: string) => {
    setUpdatingId(groupId);
    setFeedback('');
    try {
      const verifiedDealerIds = dealers.map(d => d.id);
      if (verifiedDealerIds.length === 0) {
        setFeedback('No verified dealers available to invite.');
        return;
      }

      const res = await apiFetch(`/admin/groups/${groupId}/invite-dealers`, {
        method: 'POST',
        body: JSON.stringify({ dealer_ids: verifiedDealerIds }),
      });

      setFeedback(res.message || 'Dealership invitations dispatched.');
      // Refresh groups list
      const updated = await apiFetch('/admin/groups');
      setGroups(updated);
    } catch (err: any) {
      setFeedback(err.message || 'Failed to dispatch invitations');
    } finally {
      setUpdatingId(null);
    }
  };

  if (isLoading || loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-sm text-slate-400">
        Loading groups moderation console...
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
            Buying Group Moderation & Bidding Control
          </h1>
          <p className="text-xs sm:text-sm text-slate-500">
            Control group lifecycles, schedule bidding sessions, and dispatch dealership invitations.
          </p>
        </div>
      </div>

      {feedback && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-xl flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 flex-shrink-0 text-emerald-600" />
          <span>{feedback}</span>
        </div>
      )}

      {/* Buying Groups Table */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden overflow-x-auto">
        <table className="w-full text-xs text-left border-collapse min-w-[850px]">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200 text-slate-700">
              <th className="p-4 font-bold">Cohort Code & Vehicle</th>
              <th className="p-4 font-bold">Members / Target</th>
              <th className="p-4 font-bold">Timeline & Invites</th>
              <th className="p-4 font-bold">Status Machine</th>
              <th className="p-4 font-bold text-right">Moderator Actions</th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-100">
            {groups.map((g) => (
              <tr key={g.id} className="hover:bg-slate-50/50">
                <td className="p-4">
                  <span className="font-mono text-[10px] font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                    {g.group_code}
                  </span>
                  <div className="font-bold text-sm text-navy-950 mt-1">{g.vehicle_name}</div>
                  <div className="text-[11px] text-slate-400">{g.city_name}</div>
                </td>

                <td className="p-4">
                  <div className="font-bold text-navy-900 text-sm">
                    {g.current_members} / {g.target_members}
                  </div>
                  <div className="text-[11px] text-slate-400">
                    {g.current_members >= g.target_members ? 'Milestone Reached' : 'Gathering Members'}
                  </div>
                </td>

                <td className="p-4 space-y-1">
                  <div className="text-slate-600">{g.target_purchase_timeline.replace(/_/g, ' ')}</div>
                  <div className="text-[11px] text-purple-700 font-semibold">
                    {g.invited_dealers_count} Dealers Invited • {g.submitted_quotations_count} Quotes
                  </div>
                </td>

                <td className="p-4">
                  <select
                    value={g.status}
                    disabled={updatingId === g.id}
                    onChange={(e) => handleStatusChange(g.id, e.target.value)}
                    className="text-xs bg-slate-50 border border-slate-200 rounded-xl px-2.5 py-1.5 font-bold text-navy-900 focus:outline-none"
                  >
                    <option value="OPEN">OPEN (Accepting)</option>
                    <option value="QUALIFYING">QUALIFYING (Intent Check)</option>
                    <option value="READY_FOR_BIDDING">READY_FOR_BIDDING</option>
                    <option value="BIDDING_OPEN">BIDDING_OPEN (Active Quotes)</option>
                    <option value="OFFERS_AVAILABLE">OFFERS_AVAILABLE (Live to Buyers)</option>
                    <option value="COMPLETED">COMPLETED (Delivered)</option>
                    <option value="CANCELLED">CANCELLED</option>
                  </select>
                </td>

                <td className="p-4 text-right space-x-2">
                  <button
                    onClick={() => handleInviteAllVerifiedDealers(g.id)}
                    disabled={updatingId === g.id}
                    className="px-3 py-1.5 bg-brand-500 hover:bg-brand-600 disabled:opacity-50 text-white font-semibold text-xs rounded-xl shadow-sm transition-colors inline-flex items-center gap-1"
                    title="Invite verified dealerships in Indore"
                  >
                    <Send className="w-3 h-3" />
                    Invite Dealers
                  </button>
                  <Link
                    href={`/groups/${g.id}`}
                    className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-xl transition-colors inline-block"
                  >
                    View
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </div>
  );
}

