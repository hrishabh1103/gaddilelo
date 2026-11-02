'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { 
  Users, Sparkles, Bell, PhoneCall, ChevronRight, CheckCircle2, 
  Clock, ShieldCheck, MapPin, IndianRupee, ArrowRight 
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { apiFetch } from '@/lib/api';
import { BuyingGroup, NotificationItem } from '@/types';

export default function BuyerDashboardPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  const [joinedGroups, setJoinedGroups] = useState<BuyingGroup[]>([]);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login?redirect=/dashboard');
      return;
    }

    async function loadDashboard() {
      try {
        const [allGroups, notifs] = await Promise.all([
          apiFetch<BuyingGroup[]>('/groups').catch(() => []),
          apiFetch<NotificationItem[]>('/notifications').catch(() => []),
        ]);

        // Filter groups where user is member
        const myGroups = allGroups?.filter(g => g.is_current_user_member) || [];
        setJoinedGroups(myGroups);
        setNotifications(notifs || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }

    if (user) loadDashboard();
  }, [user, isLoading, router]);

  if (isLoading || loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-sm text-slate-400">
        Loading dashboard...
      </div>
    );
  }

  const createdGroups = joinedGroups.filter(g => g.created_by_user_id === user?.id);
  const biddingGroups = joinedGroups.filter(g => g.status === 'BIDDING_OPEN' || g.status === 'OFFERS_AVAILABLE');

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-navy-950">
            Welcome back, {user?.full_name}
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Buyer Dashboard • Pilot Market: Indore, Madhya Pradesh
          </p>
        </div>

        <Link
          href="/groups/create"
          className="self-start sm:self-auto px-4 py-2.5 bg-brand-500 hover:bg-brand-600 text-white font-semibold text-xs rounded-xl shadow-md shadow-brand-500/20 transition-all flex items-center gap-1.5"
        >
          <Sparkles className="w-4 h-4" /> Start a New Group
        </Link>
      </div>

      {/* Overview Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <div className="text-xs font-semibold text-slate-400">Joined Cohorts</div>
          <div className="text-2xl font-black text-navy-950">{joinedGroups.length}</div>
          <div className="text-[11px] text-slate-500">Active group memberships</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <div className="text-xs font-semibold text-slate-400">Created by You</div>
          <div className="text-2xl font-black text-brand-600">{createdGroups.length}</div>
          <div className="text-[11px] text-slate-500">Initiated cohorts</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <div className="text-xs font-semibold text-slate-400">Active Bidding</div>
          <div className="text-2xl font-black text-blue-600">{biddingGroups.length}</div>
          <div className="text-[11px] text-slate-500">Quotes being submitted</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <div className="text-xs font-semibold text-slate-400">Notifications</div>
          <div className="text-2xl font-black text-purple-600">
            {notifications.filter(n => !n.is_read).length}
          </div>
          <div className="text-[11px] text-slate-500">Unread updates</div>
        </div>
      </div>

      {/* Main Content: Joined Groups List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-navy-950">Your Active Buying Cohorts</h2>
          <Link href="/groups" className="text-xs font-semibold text-brand-600 hover:underline">
            Explore more cohorts
          </Link>
        </div>

        {joinedGroups.length === 0 ? (
          <div className="p-12 bg-white rounded-3xl border border-slate-200 text-center space-y-3">
            <Users className="w-10 h-10 text-slate-300 mx-auto" />
            <h3 className="text-sm font-bold text-navy-950">You haven&apos;t joined any buying groups yet.</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Browse vehicle models in Indore or start your own cohort to trigger dealership bulk bidding.
            </p>
            <div className="flex justify-center gap-3 pt-2">
              <Link href="/vehicles" className="px-4 py-2 bg-slate-900 text-white text-xs font-semibold rounded-xl">
                Browse Vehicles
              </Link>
              <Link href="/groups" className="px-4 py-2 bg-brand-500 text-white text-xs font-semibold rounded-xl">
                Explore Groups
              </Link>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {joinedGroups.map((g) => {
              const progress = Math.min(100, Math.round((g.current_members_count / g.target_members) * 100));

              return (
                <div
                  key={g.id}
                  className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between space-y-4"
                >
                  <div className="space-y-2">
                    <div className="flex justify-between items-start">
                      <span className="font-mono text-[10px] text-slate-400 bg-slate-100 px-2 py-0.5 rounded">
                        {g.group_code}
                      </span>
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase bg-brand-100 text-brand-700">
                        {g.status.replace('_', ' ')}
                      </span>
                    </div>

                    <h3 className="font-bold text-base text-navy-950">
                      {g.vehicle_name}
                    </h3>
                    <p className="text-xs text-slate-500">
                      {g.variant_name} • {g.city_name}
                    </p>
                  </div>

                  {/* Progress Meter */}
                  <div className="space-y-1.5 pt-2 border-t border-slate-100">
                    <div className="flex justify-between text-xs">
                      <span className="text-slate-500">Cohort Members:</span>
                      <strong className="text-navy-900">{g.current_members_count} / {g.target_members}</strong>
                    </div>
                    <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                      <div className="bg-brand-500 h-full rounded-full" style={{ width: `${progress}%` }} />
                    </div>
                  </div>

                  {/* Offers Notice */}
                  {g.status === 'OFFERS_AVAILABLE' && (
                    <div className="p-2.5 bg-emerald-50 rounded-xl text-xs text-emerald-800 font-semibold border border-emerald-100">
                      ✓ Approved dealer quotations available!
                    </div>
                  )}

                  <div className="pt-2">
                    <Link
                      href={`/groups/${g.id}`}
                      className="w-full py-2 bg-navy-900 hover:bg-navy-800 text-white font-semibold text-xs rounded-xl text-center block transition-colors"
                    >
                      {g.status === 'OFFERS_AVAILABLE' ? 'Compare Offers' : 'View Group Details'}
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Notifications Section */}
      <div className="space-y-4 pt-6 border-t border-slate-200">
        <h2 className="text-lg font-bold text-navy-950">Recent Updates & Activity</h2>

        {notifications.length === 0 ? (
          <div className="p-6 bg-white rounded-2xl border border-slate-200 text-center text-xs text-slate-400">
            No notifications yet
          </div>
        ) : (
          <div className="bg-white rounded-2xl border border-slate-200 divide-y divide-slate-100 overflow-hidden">
            {notifications.slice(0, 5).map((n) => (
              <div key={n.id} className="p-4 text-xs flex items-start justify-between gap-4">
                <div className="space-y-0.5">
                  <div className="font-bold text-navy-950">{n.title}</div>
                  <div className="text-slate-600">{n.message}</div>
                  <div className="text-[10px] text-slate-400">
                    {new Date(n.created_at).toLocaleDateString()} at {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
                {n.link_url && (
                  <Link href={n.link_url} className="text-brand-600 font-semibold hover:underline flex-shrink-0">
                    View
                  </Link>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
}

