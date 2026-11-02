'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { 
  Users, Sparkles, Car, MapPin, Calendar, CheckCircle2, AlertCircle, ArrowRight 
} from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { VehicleCategory, VehicleBrand, VehicleModel, VehicleVariant, City } from '@/types';
import { useAuth } from '@/context/AuthContext';

function CreateBuyingGroupForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const preselectedVariantId = searchParams.get('variant_id') || '';
  const preselectedModelId = searchParams.get('model_id') || '';

  const { user } = useAuth();

  const [categories, setCategories] = useState<VehicleCategory[]>([]);
  const [brands, setBrands] = useState<VehicleBrand[]>([]);
  const [models, setModels] = useState<VehicleModel[]>([]);
  const [variants, setVariants] = useState<VehicleVariant[]>([]);
  const [cities, setCities] = useState<City[]>([]);

  // Selected Form State
  const [categoryId, setCategoryId] = useState('');
  const [brandId, setBrandId] = useState('');
  const [modelId, setModelId] = useState(preselectedModelId);
  const [variantId, setVariantId] = useState(preselectedVariantId);
  const [cityId, setCityId] = useState('');
  const [targetMembers, setTargetMembers] = useState(5);
  const [purchaseTimeline, setPurchaseTimeline] = useState('WITHIN_30_DAYS');
  const [additionalNotes, setAdditionalNotes] = useState('');

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadInitial() {
      try {
        const [cats, cts] = await Promise.all([
          apiFetch<VehicleCategory[]>('/catalog/categories'),
          apiFetch<City[]>('/catalog/cities'),
        ]);
        setCategories(cats || []);
        setCities(cts || []);
        if (cts?.length > 0) {
          const ind = cts.find(c => c.name.toLowerCase() === 'indore') || cts[0];
          setCityId(ind.id);
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    loadInitial();
  }, []);

  // When category changes, load brands
  useEffect(() => {
    async function loadBrands() {
      if (!categoryId) return;
      try {
        const data = await apiFetch<VehicleBrand[]>(`/catalog/brands?category_id=${categoryId}`);
        setBrands(data || []);
        setBrandId('');
        setModels([]);
        setVariants([]);
      } catch (e) {
        console.error(e);
      }
    }
    loadBrands();
  }, [categoryId]);

  // When brand changes, load models
  useEffect(() => {
    async function loadModels() {
      if (!brandId) return;
      try {
        const data = await apiFetch<VehicleModel[]>(`/catalog/models?brand_id=${brandId}`);
        setModels(data || []);
        setModelId('');
        setVariants([]);
      } catch (e) {
        console.error(e);
      }
    }
    loadModels();
  }, [brandId]);

  // When model changes, load variants
  useEffect(() => {
    if (!modelId) return;
    const m = models.find(mod => mod.id === modelId);
    if (m?.variants) {
      setVariants(m.variants);
      if (m.variants.length > 0 && !variantId) {
        setVariantId(m.variants[0].id);
      }
    }
  }, [modelId, models, variantId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!user) {
      router.push(`/login?redirect=/groups/create`);
      return;
    }

    if (!variantId || !cityId) {
      setError('Please select a vehicle variant and target city');
      return;
    }

    setSubmitting(true);
    try {
      const res = await apiFetch('/groups', {
        method: 'POST',
        body: JSON.stringify({
          vehicle_variant_id: variantId,
          city_id: cityId,
          target_members: Number(targetMembers),
          target_purchase_timeline: purchaseTimeline,
          additional_notes: additionalNotes,
        }),
      });

      router.push(`/groups/${res.id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to create group');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-orange-100 text-brand-700 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Demand Aggregation Engine</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-navy-950">
          Start a Vehicle Buying Group
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 max-w-lg mx-auto">
          Specify your vehicle variant in Indore. Once your cohort reaches target capacity, authorized dealerships are invited to compete with their best bulk quotations.
        </p>
      </div>

      {/* Form Container */}
      <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200/80 shadow-sm space-y-6">
        
        {error && (
          <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          
          {/* Step 1: Category & City */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700">1. Vehicle Category *</label>
              <select
                value={categoryId}
                onChange={(e) => setCategoryId(e.target.value)}
                required
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                <option value="">Select category...</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700">2. Target City (Pilot Market) *</label>
              <select
                value={cityId}
                onChange={(e) => setCityId(e.target.value)}
                required
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                {cities.map((city) => (
                  <option key={city.id} value={city.id}>{city.name}, {city.state}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Step 2: Brand & Model */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700">3. Manufacturer Brand *</label>
              <select
                value={brandId}
                onChange={(e) => setBrandId(e.target.value)}
                disabled={!categoryId}
                required
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-slate-800 focus:outline-none disabled:opacity-50"
              >
                <option value="">Select brand...</option>
                {brands.map((b) => (
                  <option key={b.id} value={b.id}>{b.name}</option>
                ))}
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700">4. Vehicle Model *</label>
              <select
                value={modelId}
                onChange={(e) => setModelId(e.target.value)}
                disabled={!brandId}
                required
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-slate-800 focus:outline-none disabled:opacity-50"
              >
                <option value="">Select model...</option>
                {models.map((m) => (
                  <option key={m.id} value={m.id}>{m.name}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Step 3: Variant Selection */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700">5. Exact Variant / Powertrain *</label>
            <select
              value={variantId}
              onChange={(e) => setVariantId(e.target.value)}
              disabled={!modelId || variants.length === 0}
              required
              className="w-full text-xs bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-slate-800 focus:outline-none disabled:opacity-50"
            >
              <option value="">Select variant...</option>
              {variants.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.name} ({v.fuel_type} • {v.transmission} • Ex-showroom: ₹{Number(v.reference_ex_showroom).toLocaleString('en-IN')})
                </option>
              ))}
            </select>
          </div>

          {/* Step 4: Group Parameters */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700">6. Target Cohort Size</label>
              <select
                value={targetMembers}
                onChange={(e) => setTargetMembers(Number(e.target.value))}
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-slate-800 focus:outline-none"
              >
                <option value={3}>3 Buyers (Fast bidding turnaround)</option>
                <option value={5}>5 Buyers (Standard bulk tier - Recommended)</option>
                <option value={10}>10 Buyers (High volume OEM maximum discount)</option>
                <option value={15}>15 Buyers (Fleet / Commercial tier)</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700">7. Expected Purchase Timeline</label>
              <select
                value={purchaseTimeline}
                onChange={(e) => setPurchaseTimeline(e.target.value)}
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-slate-800 focus:outline-none"
              >
                <option value="WITHIN_15_DAYS">Immediate (Within 15 Days)</option>
                <option value="WITHIN_30_DAYS">Normal (Within 30 Days)</option>
                <option value="WITHIN_60_DAYS">Flexible (Within 60 Days)</option>
              </select>
            </div>
          </div>

          {/* Step 5: Optional Notes */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700">
              8. Additional Requirements / Notes (Optional)
            </label>
            <textarea
              rows={3}
              value={additionalNotes}
              onChange={(e) => setAdditionalNotes(e.target.value)}
              placeholder="e.g. Color preferences, exchange interest, corporate lease requirements..."
              className="w-full text-xs bg-slate-50 border border-slate-200 rounded-xl p-3 text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
          </div>

          {/* Privacy Guarantee & Submit */}
          <div className="pt-4 border-t border-slate-100 space-y-4">
            <div className="flex items-start gap-2 text-[11px] text-slate-500 bg-slate-50 p-3 rounded-xl border border-slate-200/60">
              <CheckCircle2 className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
              <span>
                <strong>Privacy Assurance:</strong> Creating or joining a group is 100% non-binding. Your personal contact details are never visible to other members.
              </span>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-3.5 bg-brand-500 hover:bg-brand-600 disabled:opacity-50 text-white font-bold text-xs rounded-xl shadow-md shadow-brand-500/20 transition-all flex items-center justify-center gap-2"
            >
              {submitting ? 'Creating Group...' : 'Launch Buying Group in Indore'}
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

        </form>

      </div>

    </div>
  );
}

export default function CreateBuyingGroupPage() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-sm text-slate-400">Loading form...</div>}>
      <CreateBuyingGroupForm />
    </Suspense>
  );
}
