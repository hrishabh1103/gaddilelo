'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { 
  Building2, IndianRupee, ShieldCheck, ArrowLeft, CheckCircle2, 
  AlertCircle, Sparkles, Plus, Trash2, HelpCircle 
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { apiFetch } from '@/lib/api';

export default function SubmitQuotationPage() {
  const params = useParams();
  const router = useRouter();
  const groupId = params?.groupId as string;

  const { user, isLoading } = useAuth();

  const [group, setGroup] = useState<any>(null);
  const [existingQuote, setExistingQuote] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  // Vehicle-Agnostic Pricing Form Fields
  const [baseExShowroom, setBaseExShowroom] = useState<number>(0);
  const [rtoRoadTax, setRtoRoadTax] = useState<number>(0);
  const [insuranceAmount, setInsuranceAmount] = useState<number>(0);
  const [tcsAmount, setTcsAmount] = useState<number>(0);
  const [mfgDiscount, setMfgDiscount] = useState<number>(0);
  const [dealerDiscount, setDealerDiscount] = useState<number>(0);
  const [exchangeBonus, setExchangeBonus] = useState<number>(0);
  const [corporateDiscount, setCorporateDiscount] = useState<number>(0);
  const [accessoriesAmount, setAccessoriesAmount] = useState<number>(0);
  const [logisticsHandling, setLogisticsHandling] = useState<number>(0);
  const [otherCharges, setOtherCharges] = useState<number>(0);
  const [deliveryDays, setDeliveryDays] = useState<number>(14);
  const [remarks, setRemarks] = useState<string>('');

  useEffect(() => {
    if (!isLoading) {
      if (!user) {
        router.push(`/login?redirect=/dealer/bid/${groupId}`);
        return;
      }
      if (user.role !== 'DEALER' && user.role !== 'ADMIN') {
        router.push('/dashboard');
        return;
      }
    }

    async function loadData() {
      try {
        const [gData, quotes] = await Promise.all([
          apiFetch(`/groups/${groupId}`),
          apiFetch<any[]>('/dealers/quotations').catch(() => []),
        ]);
        setGroup(gData);

        const refPrice = Number(gData.vehicle.reference_ex_showroom) || 1000000;
        setBaseExShowroom(refPrice);

        // Pre-fill statutory estimates for Indore, MP:
        // MP Road Tax ~8%, Insurance ~3.5%
        setRtoRoadTax(Math.round(refPrice * 0.08));
        setInsuranceAmount(Math.round(refPrice * 0.035));
        if (refPrice > 1000000) {
          setTcsAmount(Math.round(refPrice * 0.01)); // 1% TCS
        }

        // Check if existing quote
        const found = quotes?.find((q) => q.group_id === groupId);
        if (found) {
          setExistingQuote(found);
          setBaseExShowroom(Number(found.base_ex_showroom));
          setRtoRoadTax(Number(found.rto_road_tax));
          setInsuranceAmount(Number(found.insurance_amount));
          setTcsAmount(Number(found.tcs_amount));
          setMfgDiscount(Number(found.mfg_discount));
          setDealerDiscount(Number(found.dealer_discount));
          setExchangeBonus(Number(found.exchange_bonus));
          setCorporateDiscount(Number(found.corporate_discount));
          setAccessoriesAmount(Number(found.accessories_amount));
          setLogisticsHandling(Number(found.logistics_handling));
          setOtherCharges(Number(found.other_statutory_charges));
          setDeliveryDays(found.delivery_timeline_days);
          setRemarks(found.remarks || '');
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }

    if (user && (user.role === 'DEALER' || user.role === 'ADMIN')) {
      loadData();
    }
  }, [user, isLoading, groupId, router]);

  // Pricing Engine Live Calculations
  const grossAdditions = Number(baseExShowroom || 0) + Number(rtoRoadTax || 0) + Number(insuranceAmount || 0) + 
                         Number(tcsAmount || 0) + Number(accessoriesAmount || 0) + Number(logisticsHandling || 0) + 
                         Number(otherCharges || 0);

  const totalDiscounts = Number(mfgDiscount || 0) + Number(dealerDiscount || 0) + 
                         Number(exchangeBonus || 0) + Number(corporateDiscount || 0);

  const calculatedFinalPrice = Math.max(0, grossAdditions - totalDiscounts);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (totalDiscounts > baseExShowroom) {
      setError('Total discounts cannot exceed base vehicle ex-showroom price');
      return;
    }

    setSubmitting(true);
    try {
      const payload = {
        group_id: groupId,
        base_ex_showroom: baseExShowroom,
        rto_road_tax: rtoRoadTax,
        insurance_amount: insuranceAmount,
        tcs_amount: tcsAmount,
        mfg_discount: mfgDiscount,
        dealer_discount: dealerDiscount,
        exchange_bonus: exchangeBonus,
        corporate_discount: corporateDiscount,
        accessories_amount: accessoriesAmount,
        logistics_handling: logisticsHandling,
        other_statutory_charges: otherCharges,
        delivery_timeline_days: deliveryDays,
        offer_valid_until: new Date(Date.now() + 14 * 86400000).toISOString(),
        remarks,
        line_items: [
          { item_name: 'All-Weather Matting Pack', item_type: 'COMPLIMENTARY', amount: 0 },
          { item_name: 'Roadside Assistance (3 Yrs)', item_type: 'COMPLIMENTARY', amount: 0 },
        ],
      };

      if (existingQuote) {
        // Revision
        await apiFetch(`/dealers/quotations/${existingQuote.id}`, {
          method: 'PUT',
          body: JSON.stringify(payload),
        });
      } else {
        // Initial Submission
        await apiFetch('/dealers/quotations', {
          method: 'POST',
          body: JSON.stringify(payload),
        });
      }

      router.push('/dealer/quotations');
    } catch (err: any) {
      setError(err.message || 'Failed to submit quotation');
    } finally {
      setSubmitting(false);
    }
  };

  if (isLoading || loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center text-sm text-slate-400">
        Loading quotation engine...
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="space-y-2 pb-6 border-b border-slate-200">
        <Link href="/dealer/invitations" className="text-xs font-semibold text-slate-500 hover:text-navy-900 flex items-center gap-1 mb-1">
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Invitations
        </Link>
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
            {existingQuote ? 'Revise Quotation (Snapshot Preserved)' : 'Submit Competitive Quotation'}
          </span>
          <span className="font-mono text-xs text-slate-400">Cohort: {group?.group_code}</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-navy-950">
          {group?.vehicle.brand_name} {group?.vehicle.model_name} ({group?.vehicle.variant_name})
        </h1>
        <p className="text-xs text-slate-500">
          Target Cohort Size: <strong className="text-navy-900">{group?.current_members_count} Buyers Pooled</strong> • Territory: <strong>Indore, MP</strong>
        </p>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Pricing Engine Form */}
      <form onSubmit={handleSubmit} className="space-y-8">
        
        {/* Section 1: Base & Statutory Additions */}
        <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
          <h2 className="text-sm font-bold text-navy-900 border-b border-slate-100 pb-2">
            1. Base Vehicle & Statutory Costs (Indore, MP)
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
            
            <div className="space-y-1">
              <label className="font-semibold text-slate-700">Base Ex-Showroom (₹) *</label>
              <input
                type="number"
                value={baseExShowroom}
                onChange={(e) => setBaseExShowroom(Number(e.target.value))}
                required
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 font-mono focus:outline-none"
              />
            </div>

            <div className="space-y-1">
              <label className="font-semibold text-slate-700">RTO & Road Tax MP (₹) *</label>
              <input
                type="number"
                value={rtoRoadTax}
                onChange={(e) => setRtoRoadTax(Number(e.target.value))}
                required
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 font-mono focus:outline-none"
              />
            </div>

            <div className="space-y-1">
              <label className="font-semibold text-slate-700">Comprehensive Insurance (₹) *</label>
              <input
                type="number"
                value={insuranceAmount}
                onChange={(e) => setInsuranceAmount(Number(e.target.value))}
                required
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 font-mono focus:outline-none"
              />
            </div>

            <div className="space-y-1">
              <label className="font-semibold text-slate-700">Statutory TCS (1% if &gt; 10L) (₹)</label>
              <input
                type="number"
                value={tcsAmount}
                onChange={(e) => setTcsAmount(Number(e.target.value))}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 font-mono focus:outline-none"
              />
            </div>

            <div className="space-y-1">
              <label className="font-semibold text-slate-700">Basic Kit / Accessories Pack (₹)</label>
              <input
                type="number"
                value={accessoriesAmount}
                onChange={(e) => setAccessoriesAmount(Number(e.target.value))}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 font-mono focus:outline-none"
              />
            </div>

            <div className="space-y-1">
              <label className="font-semibold text-slate-700">Fastag & Statutory Logistics (₹)</label>
              <input
                type="number"
                value={logisticsHandling}
                onChange={(e) => setLogisticsHandling(Number(e.target.value))}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 font-mono focus:outline-none"
              />
            </div>

          </div>
        </div>

        {/* Section 2: Group Deductions & OEM Discounts */}
        <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex justify-between items-center border-b border-slate-100 pb-2">
            <h2 className="text-sm font-bold text-emerald-800">
              2. Cohort Group Discounts & Incentives (Deductions)
            </h2>
            <span className="text-[11px] font-bold text-emerald-700">
              Total Benefits: -₹{totalDiscounts.toLocaleString('en-IN')}
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            
            <div className="space-y-1">
              <label className="font-semibold text-slate-700">Dealership Volume Margin Discount (₹)</label>
              <input
                type="number"
                value={dealerDiscount}
                onChange={(e) => setDealerDiscount(Number(e.target.value))}
                placeholder="e.g. 35000"
                className="w-full bg-emerald-50/50 border border-emerald-200 rounded-xl px-3 py-2 text-slate-900 font-mono focus:outline-none"
              />
            </div>

            <div className="space-y-1">
              <label className="font-semibold text-slate-700">OEM Consumer Scheme (₹)</label>
              <input
                type="number"
                value={mfgDiscount}
                onChange={(e) => setMfgDiscount(Number(e.target.value))}
                placeholder="e.g. 25000"
                className="w-full bg-emerald-50/50 border border-emerald-200 rounded-xl px-3 py-2 text-slate-900 font-mono focus:outline-none"
              />
            </div>

            <div className="space-y-1">
              <label className="font-semibold text-slate-700">Exchange Bonus (₹)</label>
              <input
                type="number"
                value={exchangeBonus}
                onChange={(e) => setExchangeBonus(Number(e.target.value))}
                placeholder="e.g. 15000"
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 font-mono focus:outline-none"
              />
            </div>

            <div className="space-y-1">
              <label className="font-semibold text-slate-700">Corporate / Trade Perk (₹)</label>
              <input
                type="number"
                value={corporateDiscount}
                onChange={(e) => setCorporateDiscount(Number(e.target.value))}
                placeholder="e.g. 5000"
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 font-mono focus:outline-none"
              />
            </div>

          </div>
        </div>

        {/* Section 3: Delivery Terms & Remarks */}
        <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
          <h2 className="text-sm font-bold text-navy-900 border-b border-slate-100 pb-2">
            3. Delivery Commitment & Offer Remarks
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="space-y-1">
              <label className="font-semibold text-slate-700">Estimated Delivery (Days from Booking) *</label>
              <input
                type="number"
                value={deliveryDays}
                onChange={(e) => setDeliveryDays(Number(e.target.value))}
                required
                min={1}
                max={180}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:outline-none"
              />
            </div>

            <div className="space-y-1">
              <label className="font-semibold text-slate-700">Dealership Notes & Perks</label>
              <input
                type="text"
                value={remarks}
                onChange={(e) => setRemarks(e.target.value)}
                placeholder="e.g. Complimentary Teflon coating & 3-year RSA included"
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:outline-none"
              />
            </div>
          </div>
        </div>

        {/* Live Calculation Summary Card */}
        <div className="bg-navy-950 text-white p-6 rounded-3xl shadow-xl space-y-4">
          <div className="flex justify-between items-center pb-3 border-b border-navy-800">
            <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">
              Live Quotation Engine Formula Breakdown
            </span>
            <span className="text-xs text-brand-400 font-bold">
              Formula: (Gross Additions) - (Group Discounts)
            </span>
          </div>

          <div className="grid grid-cols-3 gap-4 text-xs">
            <div>
              <div className="text-slate-400 text-[11px]">Gross Additions</div>
              <div className="font-mono font-bold text-sm text-slate-200">
                ₹{grossAdditions.toLocaleString('en-IN')}
              </div>
            </div>
            <div>
              <div className="text-slate-400 text-[11px]">Total Deductions</div>
              <div className="font-mono font-bold text-sm text-emerald-400">
                -₹{totalDiscounts.toLocaleString('en-IN')}
              </div>
            </div>
            <div className="text-right">
              <div className="text-brand-400 text-[11px] font-bold">FINAL ON-ROAD PRICE</div>
              <div className="font-mono font-black text-xl text-white">
                ₹{calculatedFinalPrice.toLocaleString('en-IN')}
              </div>
            </div>
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={submitting}
              className="w-full py-3.5 bg-brand-500 hover:bg-brand-600 disabled:opacity-50 text-white font-bold text-xs rounded-xl shadow-lg shadow-brand-500/20 transition-all text-center"
            >
              {submitting
                ? 'Submitting to Moderation Desk...'
                : existingQuote
                ? 'Submit Revised Quotation'
                : 'Submit Official Quotation to Cohort'}
            </button>
          </div>
        </div>

      </form>

    </div>
  );
}
