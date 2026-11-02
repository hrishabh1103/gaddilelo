'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { 
  Users, Sparkles, MapPin, Clock, ShieldCheck, CheckCircle2, 
  Share2, ArrowRight, AlertCircle, Award, Check, UserMinus, LogIn
} from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { BuyingGroup, Quotation } from '@/types';
import { useAuth } from '@/context/AuthContext';

export default function GroupDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params?.id as string;

  const { user } = useAuth();
  const [group, setGroup] = useState<any>(null);
  const [offers, setOffers] = useState<Quotation[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState('');

  useEffect(() => {
    async function loadGroupData() {
      try {
        const [gData, oData] = await Promise.all([
          apiFetch(`/groups/${id}`),
          apiFetch<Quotation[]>(`/groups/${id}/offers`).catch(() => []),
        ]);
        setGroup(gData);
        setOffers(oData || []);
      } catch (err) {
        console.error('Failed to load group:', err);
      } finally {
        setLoading(false);
      }
    }
    if (id) loadGroupData();
  }, [id, user]);

  const handleJoin = async () => {
    if (!user) {
      router.push(`/login?redirect=/groups/${id}`);
      return;
    }
    setActionLoading(true);
    setFeedback('');
    try {
      await apiFetch(`/groups/${id}/join`, { method: 'POST' });
      setFeedback('Successfully joined group!');
      // Reload group data
      const gData = await apiFetch(`/groups/${id}`);
      setGroup(gData);
    } catch (err: any) {
      setFeedback(err.message || 'Failed to join group');
    } finally {
      setActionLoading(false);
    }
  };

  const handleLeave = async () => {
    setActionLoading(true);
    setFeedback('');
    try {
      await apiFetch(`/groups/${id}/leave`, { method: 'POST' });
      setFeedback('You have left the group.');
      const gData = await apiFetch(`/groups/${id}`);
      setGroup(gData);
    } catch (err: any) {
      setFeedback(err.message || 'Failed to leave group');
    } finally {
      setActionLoading(false);
    }
  };

  const copyShareLink = () => {
    if (typeof window !== 'undefined') {
      navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-sm text-slate-400">
        Loading buying cohort...
      </div>
    );
  }

  if (!group) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-sm text-slate-500">
        Group not found. <Link href="/groups" className="text-brand-600 underline">Browse active cohorts</Link>
      </div>
    );
  }

  const progressPct = Math.min(100, Math.round((group.current_members_count / group.target_members) * 100));

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Top Banner & Group Code */}
      <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200/80 shadow-sm space-y-6">
        
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-100">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-bold text-slate-500 bg-slate-100 px-2.5 py-1 rounded-lg">
                {group.group_code}
              </span>
              <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                group.status === 'OFFERS_AVAILABLE'
                  ? 'bg-emerald-500 text-white'
                  : group.status === 'BIDDING_OPEN'
                  ? 'bg-blue-600 text-white'
                  : 'bg-brand-500 text-white'
              }`}>
                {group.status.replace('_', ' ')}
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-navy-950">
              {group.vehicle.brand_name} {group.vehicle.model_name}
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 font-medium">
              Variant: <strong className="text-navy-900">{group.vehicle.variant_name}</strong> • City: <strong className="text-navy-900">{group.city_name}</strong>
            </p>
          </div>

          {/* Share Button */}
          <div className="flex items-center gap-2">
            <button
              onClick={copyShareLink}
              className="px-3.5 py-2 border border-slate-200 hover:border-slate-300 rounded-xl text-xs font-semibold text-slate-700 bg-slate-50 flex items-center gap-1.5 transition-colors"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Share2 className="w-3.5 h-3.5" />}
              {copied ? 'Link Copied!' : 'Share Group'}
            </button>
          </div>
        </div>

        {/* Feedback Alert */}
        {feedback && (
          <div className="p-3 bg-blue-50 border border-blue-200 text-blue-800 text-xs rounded-xl">
            {feedback}
          </div>
        )}

        {/* Progress & Milestone */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center">
          <div className="md:col-span-7 space-y-3">
            <div className="flex justify-between items-center text-xs">
              <span className="font-semibold text-slate-600">Cohort Member Progress</span>
              <span className="font-bold text-navy-950 text-sm">
                {group.current_members_count} / {group.target_members} Buyers Pooled
              </span>
            </div>

            <div className="w-full bg-slate-100 h-3 rounded-full overflow-hidden">
              <div
                className="bg-brand-500 h-full rounded-full transition-all duration-500"
                style={{ width: `${progressPct}%` }}
              />
            </div>

            <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1">
              <span>Timeline: {group.target_purchase_timeline.replace(/_/g, ' ')}</span>
              {group.bidding_end_time && (
                <span className="text-red-600 font-semibold flex items-center gap-1">
                  <Clock className="w-3 h-3" /> Bidding closes: {new Date(group.bidding_end_time).toLocaleDateString()}
                </span>
              )}
            </div>
          </div>

          {/* User Membership Actions */}
          <div className="md:col-span-5 bg-slate-50 p-4 rounded-2xl border border-slate-200/80 space-y-3">
            {group.is_current_user_member ? (
              <div className="space-y-2">
                <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-700">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>You are an active member of this cohort</span>
                </div>
                {group.status !== 'BIDDING_OPEN' && group.status !== 'OFFERS_AVAILABLE' ? (
                  <button
                    onClick={handleLeave}
                    disabled={actionLoading}
                    className="w-full py-2 bg-white hover:bg-red-50 border border-red-200 text-red-600 font-semibold text-xs rounded-xl transition-colors flex items-center justify-center gap-1.5"
                  >
                    <UserMinus className="w-3.5 h-3.5" />
                    Leave Group
                  </button>
                ) : (
                  <p className="text-[11px] text-slate-400">
                    Bidding or offers are live. Membership locked for quotation integrity.
                  </p>
                )}
              </div>
            ) : (
              <div className="space-y-2">
                <button
                  onClick={handleJoin}
                  disabled={actionLoading || (group.status !== 'OPEN' && group.status !== 'QUALIFYING')}
                  className="w-full py-2.5 bg-brand-500 hover:bg-brand-600 disabled:opacity-50 text-white font-bold text-xs rounded-xl shadow-md shadow-brand-500/20 transition-all flex items-center justify-center gap-1.5"
                >
                  <Users className="w-4 h-4" />
                  Join this Buying Group (Free)
                </button>
                <p className="text-[10px] text-center text-slate-400">
                  Non-binding. Zero financial commitment until you accept a quote.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Privacy Shield Notice (Requirement 9) */}
        <div className="bg-slate-50/80 p-3.5 rounded-2xl border border-slate-200 text-xs text-slate-600 flex items-start gap-2.5">
          <ShieldCheck className="w-4 h-4 text-emerald-600 mt-0.5 flex-shrink-0" />
          <div>
            <strong className="text-navy-900 font-semibold">Buyer Privacy Guaranteed:</strong> Your personal contact details (name, phone number, email) are strictly hidden from other cohort members. Contact information is only shared with an authorized dealership when you explicitly request a callback.
          </div>
        </div>

      </div>

      {/* Available Dealer Quotations / Side-by-Side Comparison CTA */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-navy-950">Competing Dealership Quotations</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Authorized OEM dealerships competing for this cohort in Indore
            </p>
          </div>
          {offers.length > 0 && (
            <Link
              href={`/groups/${group.id}/compare`}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs rounded-xl shadow-sm transition-colors flex items-center gap-1.5"
            >
              Side-by-Side Comparison
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          )}
        </div>

        {offers.length === 0 ? (
          <div className="p-8 bg-white rounded-2xl border border-slate-200 text-center space-y-2">
            <Clock className="w-8 h-8 text-slate-300 mx-auto" />
            <p className="text-sm font-semibold text-navy-900">
              {group.status === 'OPEN' || group.status === 'QUALIFYING'
                ? 'Dealership bidding opens once cohort milestones are met.'
                : 'Quotations currently under moderation by platform administrators.'}
            </p>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">
              Share this group to reach target members faster!
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {offers.map((quote) => {
              const totalDiscount = Number(quote.mfg_discount) + Number(quote.dealer_discount) + Number(quote.exchange_bonus) + Number(quote.corporate_discount);

              return (
                <div
                  key={quote.id}
                  className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-brand-300 transition-colors space-y-4 flex flex-col justify-between"
                >
                  <div className="space-y-2">
                    <div className="flex justify-between items-start">
                      <div>
                        <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-100">
                          Verified Dealership Quote
                        </span>
                        <h3 className="font-bold text-base text-navy-950 mt-1">
                          {quote.dealership_name}
                        </h3>
                        <p className="text-xs text-slate-400">{quote.dealer_city || 'Indore, MP'}</p>
                      </div>
                      <div className="text-right">
                        <span className="text-lg font-black text-navy-950">
                          ₹{Number(quote.final_on_road_price).toLocaleString('en-IN')}
                        </span>
                        <div className="text-[10px] text-slate-400">Final On-Road (Indore)</div>
                      </div>
                    </div>

                    <div className="p-3 bg-orange-50/60 rounded-xl border border-orange-100 text-xs flex justify-between items-center text-brand-900">
                      <span>Total Group Benefit:</span>
                      <strong className="text-brand-700 text-sm font-bold">
                        -₹{totalDiscount.toLocaleString('en-IN')}
                      </strong>
                    </div>

                    <div className="text-xs text-slate-500 space-y-1 pt-1">
                      <div>Estimated Delivery: <strong className="text-navy-900">{quote.delivery_timeline_days} Days</strong></div>
                      {quote.remarks && <div className="italic text-slate-600">&ldquo;{quote.remarks}&rdquo;</div>}
                    </div>
                  </div>

                  <div className="pt-2">
                    <Link
                      href={`/groups/${group.id}/compare`}
                      className="w-full py-2.5 bg-navy-900 hover:bg-navy-800 text-white font-semibold text-xs rounded-xl transition-colors text-center block"
                    >
                      Inspect Full Line-Item Breakdown
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

    </div>
  );
}
