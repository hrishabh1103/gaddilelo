'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { 
  PhoneCall, Mail, User, CheckCircle2, Clock, 
  MapPin, AlertCircle, ArrowRight, Check 
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { apiFetch } from '@/lib/api';
import { BuyerLead } from '@/types';

export default function DealerLeadsPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  const [leads, setLeads] = useState<BuyerLead[]>([]);
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const [feedback, setFeedback] = useState('');

  useEffect(() => {
    if (!isLoading) {
      if (!user) {
        router.push('/login?redirect=/dealer/leads');
        return;
      }
      if (user.role !== 'DEALER' && user.role !== 'ADMIN') {
        router.push('/dashboard');
        return;
      }
    }

    async function loadLeads() {
      try {
        const data = await apiFetch<BuyerLead[]>('/dealers/leads');
        setLeads(data || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    if (user && (user.role === 'DEALER' || user.role === 'ADMIN')) {
      loadLeads();
    }
  }, [user, isLoading, router]);

  const handleStatusChange = async (leadId: string, newStatus: string) => {
    setUpdatingId(leadId);
    setFeedback('');
    try {
      await apiFetch(`/dealers/leads/${leadId}/status`, {
        method: 'PUT',
        body: JSON.stringify({ status: newStatus }),
      });

      setLeads(prev => prev.map(l => l.id === leadId ? { ...l, status: newStatus } : l));
      setFeedback('Customer lead status updated successfully!');
    } catch (err: any) {
      setFeedback(err.message || 'Failed to update lead status');
    } finally {
      setUpdatingId(null);
    }
  };

  if (isLoading || loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-sm text-slate-400">
        Loading customer leads...
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <div className="text-xs font-bold uppercase tracking-wider text-purple-600">Customer Conversion Engine</div>
          <h1 className="text-2xl sm:text-3xl font-black text-navy-950 mt-1">
            Buyer Enquiries & Leads
          </h1>
          <p className="text-xs sm:text-sm text-slate-500">
            Buyers who accepted your quotation and explicitly consented to a showroom callback.
          </p>
        </div>

        <Link
          href="/dealer/dashboard"
          className="text-xs font-semibold text-slate-600 hover:text-navy-900 border border-slate-200 px-3 py-2 rounded-xl"
        >
          ← Return to Dashboard
        </Link>
      </div>

      {feedback && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-xl flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
          <span>{feedback}</span>
        </div>
      )}

      {leads.length === 0 ? (
        <div className="p-16 bg-white rounded-3xl border border-slate-200 text-center space-y-3">
          <PhoneCall className="w-10 h-10 text-slate-300 mx-auto" />
          <h3 className="text-sm font-bold text-navy-950">No customer callback requests yet</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            When buyers review your approved quotations in the side-by-side comparison matrix and click &ldquo;Request Callback&rdquo;, their contact leads will appear here.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {leads.map((lead) => (
            <div
              key={lead.id}
              className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between space-y-4"
            >
              <div className="space-y-3">
                <div className="flex justify-between items-start">
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-purple-50 text-purple-700 border border-purple-100">
                    Consent-Verified Lead
                  </span>
                  <span className="text-[10px] text-slate-400">
                    {new Date(lead.created_at).toLocaleDateString()}
                  </span>
                </div>

                <div>
                  <h3 className="font-bold text-base text-navy-950 flex items-center gap-1.5">
                    <User className="w-4 h-4 text-brand-500" />
                    {lead.buyer_name}
                  </h3>
                  <div className="text-xs text-slate-600 mt-1 space-y-0.5">
                    <div className="flex items-center gap-1.5">
                      <PhoneCall className="w-3.5 h-3.5 text-slate-400" />
                      <a href={`tel:${lead.buyer_phone}`} className="font-bold text-navy-900 hover:underline">
                        {lead.buyer_phone}
                      </a>
                    </div>
                    <div className="flex items-center gap-1.5 text-slate-500">
                      <Mail className="w-3.5 h-3.5 text-slate-400" />
                      <span>{lead.buyer_email}</span>
                    </div>
                  </div>
                </div>

                <div className="p-3 bg-slate-50 rounded-xl space-y-1 text-xs border border-slate-200/60">
                  <div className="text-slate-500 text-[11px]">Interested Vehicle:</div>
                  <strong className="text-navy-950 block">{lead.vehicle_name}</strong>
                  {lead.quoted_price && (
                    <div className="text-emerald-700 font-bold mt-1">
                      Quoted On-Road: ₹{Number(lead.quoted_price).toLocaleString('en-IN')}
                    </div>
                  )}
                </div>

                {lead.notes && (
                  <div className="text-xs text-slate-500 italic bg-amber-50/60 p-2.5 rounded-lg border border-amber-100">
                    &ldquo;{lead.notes}&rdquo;
                  </div>
                )}
              </div>

              {/* Status Update Dropdown */}
              <div className="pt-3 border-t border-slate-100 space-y-1.5">
                <label className="text-[11px] font-bold text-slate-700">Update Lead Pipeline Status:</label>
                <select
                  value={lead.status}
                  disabled={updatingId === lead.id}
                  onChange={(e) => handleStatusChange(lead.id, e.target.value)}
                  className="w-full text-xs bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-800 font-semibold focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="PENDING_CALLBACK">Pending Callback</option>
                  <option value="CONTACTED">Contacted by Phone</option>
                  <option value="TEST_DRIVE_SCHEDULED">Test Drive Scheduled</option>
                  <option value="BOOKING_IN_PROGRESS">Booking in Progress</option>
                  <option value="PURCHASE_COMPLETED">Purchase Delivered (Success)</option>
                  <option value="LOST">Lost / Dropped</option>
                </select>
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  );
}
