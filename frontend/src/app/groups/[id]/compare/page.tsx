'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { 
  Building2, CheckCircle2, ShieldCheck, ArrowLeft, PhoneCall, 
  Clock, IndianRupee, HelpCircle, Check, AlertCircle 
} from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { Quotation, BuyingGroup } from '@/types';
import { useAuth } from '@/context/AuthContext';

export default function QuotationComparisonPage() {
  const params = useParams();
  const router = useRouter();
  const id = params?.id as string;

  const { user } = useAuth();
  const [group, setGroup] = useState<any>(null);
  const [quotations, setQuotations] = useState<Quotation[]>([]);
  const [loading, setLoading] = useState(true);
  const [callbackRequested, setCallbackRequested] = useState<string | null>(null);
  const [submittingLead, setSubmittingLead] = useState(false);
  const [feedback, setFeedback] = useState('');

  useEffect(() => {
    async function loadData() {
      try {
        const [g, quotes] = await Promise.all([
          apiFetch(`/groups/${id}`),
          apiFetch<Quotation[]>(`/groups/${id}/offers`),
        ]);
        setGroup(g);
        setQuotations(quotes || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    if (id) loadData();
  }, [id]);

  const handleRequestCallback = async (quotationId: string) => {
    if (!user) {
      router.push(`/login?redirect=/groups/${id}/compare`);
      return;
    }

    setSubmittingLead(true);
    setFeedback('');
    try {
      await apiFetch('/leads/request-callback', {
        method: 'POST',
        body: JSON.stringify({
          group_id: id,
          quotation_id: quotationId,
          notes: 'Requested callback via Quotation Comparison table',
        }),
      });

      setCallbackRequested(quotationId);
      setFeedback('Callback requested! The authorized dealership has received your details and will contact you.');
    } catch (err: any) {
      setFeedback(err.message || 'Failed to request callback');
    } finally {
      setSubmittingLead(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-sm text-slate-400">
        Loading quotation comparison...
      </div>
    );
  }

  if (!group || quotations.length === 0) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-sm text-slate-500 space-y-3">
        <p>No approved quotations available for this group yet.</p>
        <Link href={`/groups/${id}`} className="text-brand-600 underline">Return to group details</Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div className="space-y-1">
          <Link href={`/groups/${id}`} className="text-xs font-semibold text-slate-500 hover:text-navy-900 flex items-center gap-1 mb-1">
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Group
          </Link>
          <h1 className="text-2xl sm:text-3xl font-black text-navy-950">
            Quotation Comparison
          </h1>
          <p className="text-xs sm:text-sm text-slate-500">
            Vehicle: <strong className="text-navy-900">{group.vehicle.brand_name} {group.vehicle.model_name} ({group.vehicle.variant_name})</strong> • Cohort Code: <span className="font-mono">{group.group_code}</span>
          </p>
        </div>

        <div className="text-xs text-slate-500 bg-slate-100 px-3 py-1.5 rounded-xl border border-slate-200">
          Territory: <strong>Indore, Madhya Pradesh</strong>
        </div>
      </div>

      {feedback && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-xl flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 flex-shrink-0 text-emerald-600" />
          <span>{feedback}</span>
        </div>
      )}

      {/* Side-by-Side Comparison Matrix */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden overflow-x-auto">
        <table className="w-full text-xs text-left border-collapse min-w-[700px]">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200">
              <th className="p-4 font-bold text-navy-900 w-1/3 text-sm">
                Cost Breakdown Components
              </th>
              {quotations.map((q) => (
                <th key={q.id} className="p-4 font-bold text-navy-950 text-center border-l border-slate-200 w-1/3">
                  <div className="text-xs text-brand-600 uppercase tracking-wider font-semibold">Authorized OEM Dealer</div>
                  <div className="text-sm font-black text-navy-900 mt-0.5">{q.dealership_name}</div>
                  <div className="text-[11px] font-normal text-slate-400">{q.dealer_city || 'Indore, MP'}</div>
                </th>
              ))}
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-100">
            
            {/* 1. Base Ex-Showroom */}
            <tr>
              <td className="p-3.5 font-medium text-slate-700">1. Base Ex-Showroom Price</td>
              {quotations.map((q) => (
                <td key={q.id} className="p-3.5 text-center font-mono font-semibold text-slate-900 border-l border-slate-100">
                  ₹{Number(q.base_ex_showroom).toLocaleString('en-IN')}
                </td>
              ))}
            </tr>

            {/* 2. RTO / Road Tax */}
            <tr className="bg-slate-50/50">
              <td className="p-3.5 font-medium text-slate-700">
                2. RTO Registration & Road Tax (MP Slabs)
              </td>
              {quotations.map((q) => (
                <td key={q.id} className="p-3.5 text-center font-mono text-slate-700 border-l border-slate-100">
                  ₹{Number(q.rto_road_tax).toLocaleString('en-IN')}
                </td>
              ))}
            </tr>

            {/* 3. Insurance */}
            <tr>
              <td className="p-3.5 font-medium text-slate-700">
                3. Comprehensive Insurance (1-Yr OD + Multi-Yr TP)
              </td>
              {quotations.map((q) => (
                <td key={q.id} className="p-3.5 text-center font-mono text-slate-700 border-l border-slate-100">
                  ₹{Number(q.insurance_amount).toLocaleString('en-IN')}
                </td>
              ))}
            </tr>

            {/* 4. Statutory TCS (if applicable) */}
            <tr className="bg-slate-50/50">
              <td className="p-3.5 font-medium text-slate-700">
                4. Statutory TCS (1% if Ex-Showroom &gt; ₹10 Lakhs)
              </td>
              {quotations.map((q) => (
                <td key={q.id} className="p-3.5 text-center font-mono text-slate-700 border-l border-slate-100">
                  {Number(q.tcs_amount) > 0 ? `₹${Number(q.tcs_amount).toLocaleString('en-IN')}` : '₹0 (Not Applicable)'}
                </td>
              ))}
            </tr>

            {/* 5. Accessories & Logistics */}
            <tr>
              <td className="p-3.5 font-medium text-slate-700">
                5. Essential Accessories & Logistics
              </td>
              {quotations.map((q) => (
                <td key={q.id} className="p-3.5 text-center font-mono text-slate-700 border-l border-slate-100">
                  ₹{(Number(q.accessories_amount) + Number(q.logistics_handling)).toLocaleString('en-IN')}
                </td>
              ))}
            </tr>

            {/* SECTION: DISCOUNTS HEADER */}
            <tr className="bg-orange-50/60 font-bold text-brand-900 border-t border-b border-orange-200">
              <td className="p-3 uppercase text-[11px] tracking-wider" colSpan={quotations.length + 1}>
                Deductions & Group Benefits (Zero Double-Counting)
              </td>
            </tr>

            {/* 6. Manufacturer Discount */}
            <tr>
              <td className="p-3.5 font-medium text-emerald-800">OEM Consumer Campaign Bonus</td>
              {quotations.map((q) => (
                <td key={q.id} className="p-3.5 text-center font-mono font-semibold text-emerald-700 border-l border-slate-100">
                  -₹{Number(q.mfg_discount).toLocaleString('en-IN')}
                </td>
              ))}
            </tr>

            {/* 7. Dealership Cohort Discount */}
            <tr className="bg-slate-50/50">
              <td className="p-3.5 font-medium text-emerald-800">Dealership Volume Margin Discount</td>
              {quotations.map((q) => (
                <td key={q.id} className="p-3.5 text-center font-mono font-semibold text-emerald-700 border-l border-slate-100">
                  -₹{Number(q.dealer_discount).toLocaleString('en-IN')}
                </td>
              ))}
            </tr>

            {/* 8. Exchange & Corporate */}
            <tr>
              <td className="p-3.5 font-medium text-emerald-800">Exchange Benefit & Corporate Perks</td>
              {quotations.map((q) => (
                <td key={q.id} className="p-3.5 text-center font-mono font-semibold text-emerald-700 border-l border-slate-100">
                  -₹{(Number(q.exchange_bonus) + Number(q.corporate_discount)).toLocaleString('en-IN')}
                </td>
              ))}
            </tr>

            {/* TOTAL SAVINGS ROW */}
            <tr className="bg-emerald-50 font-bold border-t border-b border-emerald-200">
              <td className="p-4 text-emerald-950 font-bold text-xs uppercase">Total Cohort Group Benefit</td>
              {quotations.map((q) => {
                const totalDisc = Number(q.mfg_discount) + Number(q.dealer_discount) + Number(q.exchange_bonus) + Number(q.corporate_discount);
                return (
                  <td key={q.id} className="p-4 text-center font-mono font-black text-emerald-800 text-sm border-l border-slate-200">
                    -₹{totalDisc.toLocaleString('en-IN')}
                  </td>
                );
              })}
            </tr>

            {/* FINAL ON-ROAD PRICE */}
            <tr className="bg-navy-950 text-white font-bold text-sm">
              <td className="p-4 font-black">FINAL ON-ROAD PRICE (Indore)</td>
              {quotations.map((q) => (
                <td key={q.id} className="p-4 text-center font-mono font-black text-base text-brand-400 border-l border-navy-800">
                  ₹{Number(q.final_on_road_price).toLocaleString('en-IN')}
                </td>
              ))}
            </tr>

            {/* Delivery & Validity */}
            <tr className="bg-slate-50">
              <td className="p-3.5 font-medium text-slate-700">Delivery Estimate</td>
              {quotations.map((q) => (
                <td key={q.id} className="p-3.5 text-center font-semibold text-navy-900 border-l border-slate-200">
                  {q.delivery_timeline_days} Days from Booking
                </td>
              ))}
            </tr>

            <tr>
              <td className="p-3.5 font-medium text-slate-700">Offer Validity</td>
              {quotations.map((q) => (
                <td key={q.id} className="p-3.5 text-center text-slate-500 border-l border-slate-200">
                  Valid until {new Date(q.offer_valid_until).toLocaleDateString()}
                </td>
              ))}
            </tr>

            {/* ACTION CTA ROW */}
            <tr className="bg-white">
              <td className="p-4 font-semibold text-xs text-slate-600">
                Direct Dealership Connection
              </td>
              {quotations.map((q) => (
                <td key={q.id} className="p-4 text-center border-l border-slate-200">
                  <button
                    onClick={() => handleRequestCallback(q.id)}
                    disabled={submittingLead || callbackRequested === q.id}
                    className={`w-full py-2.5 rounded-xl font-bold text-xs transition-all flex items-center justify-center gap-1.5 ${
                      callbackRequested === q.id
                        ? 'bg-emerald-600 text-white'
                        : 'bg-brand-500 hover:bg-brand-600 text-white shadow-md shadow-brand-500/20'
                    }`}
                  >
                    {callbackRequested === q.id ? (
                      <>
                        <Check className="w-3.5 h-3.5" /> Callback Requested
                      </>
                    ) : (
                      <>
                        <PhoneCall className="w-3.5 h-3.5" /> Request Dealership Callback
                      </>
                    )}
                  </button>
                  <p className="text-[10px] text-slate-400 mt-1">
                    Direct showroom fulfillment in Indore
                  </p>
                </td>
              ))}
            </tr>

          </tbody>
        </table>
      </div>

    </div>
  );
}
