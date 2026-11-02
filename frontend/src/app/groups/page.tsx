'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  Users, Sparkles, Filter, ChevronRight, CheckCircle2, 
  MapPin, Clock, Search, ArrowRight, ShieldCheck 
} from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { BuyingGroup } from '@/types';
import { useAuth } from '@/context/AuthContext';

export default function GroupsDiscoveryPage() {
  const { user } = useAuth();
  const [groups, setGroups] = useState<BuyingGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [search, setSearch] = useState('');

  useEffect(() => {
    async function loadGroups() {
      setLoading(true);
      try {
        const params = new URLSearchParams();
        if (statusFilter) params.append('status', statusFilter);
        if (search) params.append('search', search);

        const data = await apiFetch<BuyingGroup[]>(`/groups?${params.toString()}`);
        setGroups(data || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    loadGroups();
  }, [statusFilter, search]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'OFFERS_AVAILABLE':
        return <span className="bg-emerald-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-full uppercase">Offers Available</span>;
      case 'BIDDING_OPEN':
        return <span className="bg-blue-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-full uppercase">Bidding Open</span>;
      case 'QUALIFYING':
        return <span className="bg-purple-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-full uppercase">Qualifying Intent</span>;
      default:
        return <span className="bg-brand-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-full uppercase">Accepting Members</span>;
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl sm:text-3xl font-black text-navy-950">Active Buying Cohorts</h1>
            <span className="bg-slate-100 text-slate-700 text-xs font-semibold px-2.5 py-0.5 rounded-full border border-slate-200">
              Indore Pilot
            </span>
          </div>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Join pooled vehicle buyers in Indore to trigger competitive dealership bidding and locked-in bulk savings.
          </p>
        </div>

        <Link
          href="/groups/create"
          className="self-start sm:self-auto px-4 py-2.5 bg-brand-500 hover:bg-brand-600 text-white font-semibold text-xs rounded-xl shadow-md shadow-brand-500/20 transition-all flex items-center gap-1.5"
        >
          <Sparkles className="w-4 h-4" /> Start a Buying Group
        </Link>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Search */}
        <div className="flex items-center gap-2 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search cohort or vehicle..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="bg-transparent text-xs text-slate-800 placeholder-slate-400 focus:outline-none w-full"
          />
        </div>

        {/* Status Filter Chips */}
        <div className="flex flex-wrap items-center gap-1.5 w-full md:w-auto text-xs">
          <span className="text-slate-400 text-[11px] font-semibold mr-1">Status:</span>
          {[
            { id: '', label: 'All Active' },
            { id: 'OPEN', label: 'Accepting' },
            { id: 'QUALIFYING', label: 'Qualifying' },
            { id: 'BIDDING_OPEN', label: 'Bidding Open' },
            { id: 'OFFERS_AVAILABLE', label: 'Offers Live' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setStatusFilter(tab.id)}
              className={`px-3 py-1.5 rounded-xl font-medium transition-colors ${
                statusFilter === tab.id
                  ? 'bg-navy-900 text-white font-semibold'
                  : 'bg-slate-100 hover:bg-slate-200 text-slate-600'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

      </div>

      {/* Group Cards Grid */}
      {loading ? (
        <div className="p-16 text-center text-sm text-slate-400 bg-white rounded-2xl border border-slate-200">
          Loading cohorts...
        </div>
      ) : groups.length === 0 ? (
        <div className="p-16 text-center text-sm text-slate-500 bg-white rounded-2xl border border-slate-200 space-y-3">
          <Users className="w-10 h-10 text-slate-300 mx-auto" />
          <p className="font-semibold text-navy-900">No buying groups found for this filter.</p>
          <p className="text-xs text-slate-400">Be the pioneer and initiate a new cohort for your chosen vehicle!</p>
          <Link
            href="/groups/create"
            className="inline-block px-4 py-2 bg-brand-500 text-white text-xs font-semibold rounded-xl"
          >
            Start Cohort Now
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {groups.map((group) => {
            const progress = Math.min(100, Math.round((group.current_members_count / group.target_members) * 100));

            return (
              <div
                key={group.id}
                className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between"
              >
                {/* Image and Header */}
                <div className="relative h-44 bg-slate-100 overflow-hidden">
                  <img
                    src={group.vehicle_image_url || 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=600'}
                    alt={group.vehicle_name || 'Vehicle'}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute top-3 left-3">
                    {getStatusBadge(group.status)}
                  </div>
                  <div className="absolute bottom-3 right-3 bg-navy-950/80 backdrop-blur-md text-white px-2.5 py-0.5 rounded text-[10px] font-mono">
                    {group.group_code}
                  </div>
                </div>

                {/* Details */}
                <div className="p-5 flex-1 flex flex-col justify-between space-y-4">
                  <div>
                    <div className="flex justify-between items-center text-[11px] text-slate-400">
                      <span>{group.brand_name}</span>
                      <span className="flex items-center gap-1 text-slate-500">
                        <MapPin className="w-3 h-3 text-brand-500" /> {group.city_name}
                      </span>
                    </div>

                    <h3 className="font-bold text-base text-navy-950 mt-1">
                      {group.vehicle_name}
                    </h3>
                    <p className="text-xs text-slate-500 mt-0.5 font-medium line-clamp-1">
                      {group.variant_name}
                    </p>

                    <div className="mt-2 text-xs text-slate-600">
                      Timeline: <strong className="text-navy-900">{group.target_purchase_timeline.replace(/_/g, ' ')}</strong>
                    </div>
                  </div>

                  {/* Progress Meter */}
                  <div className="space-y-1.5 pt-3 border-t border-slate-100">
                    <div className="flex justify-between text-xs">
                      <span className="text-slate-500">Cohort Readiness</span>
                      <span className="font-bold text-navy-900">
                        {group.current_members_count} / {group.target_members} Buyers
                      </span>
                    </div>
                    <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                      <div
                        className="bg-brand-500 h-full rounded-full transition-all duration-300"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                  </div>

                  {/* Offers notice if available */}
                  {group.status === 'OFFERS_AVAILABLE' && (
                    <div className="p-2.5 bg-emerald-50 rounded-xl border border-emerald-100 flex items-center justify-between text-xs">
                      <span className="font-bold text-emerald-800">
                        {group.approved_quotations_count || 1} Competing Quotations Live
                      </span>
                      <span className="text-emerald-700 text-[11px] font-semibold underline">
                        Compare
                      </span>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="pt-2">
                    <Link
                      href={`/groups/${group.id}`}
                      className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-xl transition-colors flex items-center justify-center gap-1.5"
                    >
                      {group.status === 'OFFERS_AVAILABLE' ? 'Compare Competing Offers' : 'View Cohort & Join'}
                      <ChevronRight className="w-4 h-4" />
                    </Link>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

    </div>
  );
}
