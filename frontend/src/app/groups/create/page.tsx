'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { 
  Users, Sparkles, Car, MapPin, Calendar, CheckCircle2, AlertCircle, ArrowRight, Globe, Zap, Search
} from 'lucide-react';
import { apiFetch, FALLBACK_BRANDS, FALLBACK_MODELS, FALLBACK_CATEGORIES, FALLBACK_CITIES } from '@/lib/api';
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

  // Buyer Intent Confirmation State (Requirement 6)
  const [showIntentModal, setShowIntentModal] = useState(false);
  const [intentGenuine, setIntentGenuine] = useState(true);
  const [intentNonBinding, setIntentNonBinding] = useState(true);
  const [intentContactAgreed, setIntentContactAgreed] = useState(true);

  // Custom Vehicle Discovery State
  const [isCustomBrand, setIsCustomBrand] = useState(false);
  const [isCustomModel, setIsCustomModel] = useState(false);
  const [customBrandName, setCustomBrandName] = useState('');
  const [customModelName, setCustomModelName] = useState('');
  const [customVariantName, setCustomVariantName] = useState('');
  const [customFuelType, setCustomFuelType] = useState('PETROL');
  const [customPrice, setCustomPrice] = useState('');

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  // 1. Initial Load of Categories and Cities
  useEffect(() => {
    async function loadInitial() {
      try {
        const [cats, cts] = await Promise.all([
          apiFetch<VehicleCategory[]>('/catalog/categories').catch(() => FALLBACK_CATEGORIES as VehicleCategory[]),
          apiFetch<City[]>('/catalog/cities').catch(() => FALLBACK_CITIES as City[]),
        ]);
        const finalCats = cats?.length ? cats : (FALLBACK_CATEGORIES as VehicleCategory[]);
        const finalCts = cts?.length ? cts : (FALLBACK_CITIES as City[]);
        setCategories(finalCats);
        setCities(finalCts);

        if (finalCts?.length > 0) {
          const ind = finalCts.find(c => c.name.toLowerCase() === 'indore') || finalCts[0];
          setCityId(ind.id);
        }

        if (finalCats?.length > 0 && !categoryId) {
          setCategoryId(finalCats[0].id);
        }
      } catch (e) {
        console.error(e);
        setCategories(FALLBACK_CATEGORIES as VehicleCategory[]);
        setCities(FALLBACK_CITIES as City[]);
        setCategoryId(FALLBACK_CATEGORIES[0].id);
        setCityId(FALLBACK_CITIES[0].id);
      } finally {
        setLoading(false);
      }
    }
    loadInitial();
  }, []);

  // Pre-load if query params provided
  useEffect(() => {
    if (preselectedModelId) {
      apiFetch<any>(`/catalog/models/${preselectedModelId}`).then((m) => {
        if (m) {
          if (m.brand_id) setBrandId(m.brand_id);
          setModelId(m.id);
          if (m.variants && m.variants.length > 0) {
            setVariants(m.variants);
            if (preselectedVariantId) {
              setVariantId(preselectedVariantId);
            } else {
              setVariantId(m.variants[0].id);
            }
          }
        }
      }).catch(() => {});
    }
  }, [preselectedModelId, preselectedVariantId]);

  // 2. When Category changes, fetch Brands
  useEffect(() => {
    async function loadBrands() {
      if (!categoryId) return;
      try {
        let data = await apiFetch<VehicleBrand[]>(`/catalog/brands?category_id=${categoryId}`).catch(() => []);
        if (!data || data.length === 0) {
          data = await apiFetch<VehicleBrand[]>('/catalog/brands').catch(() => []);
        }
        if (!data || data.length === 0) {
          data = FALLBACK_BRANDS as VehicleBrand[];
        }
        setBrands(data);
        if (data.length > 0) {
          if (!data.some(b => b.id === brandId) && brandId !== 'OTHER') {
            setBrandId(data[0].id);
            setIsCustomBrand(false);
          }
        }
      } catch (e) {
        console.error('Failed to load brands:', e);
        setBrands(FALLBACK_BRANDS as VehicleBrand[]);
        setBrandId(FALLBACK_BRANDS[0].id);
      }
    }
    loadBrands();
  }, [categoryId]);

  // 3. When Brand changes, fetch Models
  useEffect(() => {
    async function loadModels() {
      if (!brandId || brandId === 'OTHER') return;
      try {
        const catParam = categoryId ? `&category_id=${categoryId}` : '';
        let data = await apiFetch<VehicleModel[]>(`/catalog/models?brand_id=${brandId}${catParam}`).catch(() => []);
        if (!data || data.length === 0) {
          data = await apiFetch<VehicleModel[]>(`/catalog/models?brand_id=${brandId}`).catch(() => []);
        }
        if (!data || data.length === 0) {
          const bMatch = FALLBACK_MODELS.filter(m => m.brand_id === brandId);
          data = bMatch.length > 0 ? (bMatch as unknown as VehicleModel[]) : (FALLBACK_MODELS as unknown as VehicleModel[]);
        }
        setModels(data);
        if (data.length > 0) {
          if (modelId !== 'OTHER' && !data.some(m => m.id === modelId)) {
            const selected = data[0];
            setModelId(selected.id);
            setIsCustomModel(false);
            if (selected.variants && selected.variants.length > 0) {
              setVariants(selected.variants);
              setVariantId(selected.variants[0].id);
            }
          }
        }
      } catch (e) {
        console.error('Failed to load models:', e);
        setModels(FALLBACK_MODELS as unknown as VehicleModel[]);
        const fb = FALLBACK_MODELS[0];
        setModelId(fb.id);
        if (fb.variants?.length) {
          setVariants(fb.variants as any);
          setVariantId(fb.variants[0].id);
        }
      }
    }
    loadModels();
  }, [brandId, categoryId]);

  // 4. When Model changes, extract Variants
  useEffect(() => {
    if (!modelId || modelId === 'OTHER') return;
    const m = models.find(mod => mod.id === modelId);
    if (m?.variants && m.variants.length > 0) {
      setVariants(m.variants);
      setVariantId(m.variants[0].id);
    } else {
      // Fetch model detail directly
      apiFetch<any>(`/catalog/models/${modelId}`)
        .then((mDetail) => {
          if (mDetail?.variants?.length > 0) {
            setVariants(mDetail.variants);
            setVariantId(mDetail.variants[0].id);
          } else {
            const fbModel = FALLBACK_MODELS.find(f => f.id === modelId);
            if (fbModel?.variants?.length) {
              setVariants(fbModel.variants as any);
              setVariantId(fbModel.variants[0].id);
            } else {
              const defaultVars = [
                {
                  id: `default-${modelId}`,
                  name: `${m?.name || 'Standard'} All Trims Eligible (Bulk Discount)`,
                  fuel_type: 'PETROL',
                  transmission: 'MANUAL',
                  reference_ex_showroom: 1100000,
                  specifications: {}
                }
              ];
              setVariants(defaultVars as any);
              setVariantId(defaultVars[0].id);
            }
          }
        })
        .catch(() => {
          const fbModel = FALLBACK_MODELS.find(f => f.id === modelId);
          if (fbModel?.variants?.length) {
            setVariants(fbModel.variants as any);
            setVariantId(fbModel.variants[0].id);
          } else {
            const defaultVars = [
              {
                id: `default-${modelId}`,
                name: `${m?.name || 'Standard'} All Trims Eligible (Bulk Discount)`,
                fuel_type: 'PETROL',
                transmission: 'MANUAL',
                reference_ex_showroom: 1100000,
                specifications: {}
              }
            ];
            setVariants(defaultVars as any);
            setVariantId(defaultVars[0].id);
          }
        });
    }
  }, [modelId, models]);

  const handleBrandChange = (val: string) => {
    if (val === 'OTHER') {
      setBrandId('OTHER');
      setIsCustomBrand(true);
      setModelId('OTHER');
      setIsCustomModel(true);
      setVariantId('OTHER');
    } else {
      setBrandId(val);
      setIsCustomBrand(false);
      if (modelId === 'OTHER') {
        setIsCustomModel(false);
        setModelId('');
      }
    }
  };

  const handleModelChange = (val: string) => {
    if (val === 'OTHER') {
      setModelId('OTHER');
      setIsCustomModel(true);
      setVariantId('OTHER');
      setVariants([]);
    } else {
      setModelId(val);
      setIsCustomModel(false);
      const found = models.find(m => m.id === val);
      if (found?.variants && found.variants.length > 0) {
        setVariants(found.variants);
        setVariantId(found.variants[0].id);
      } else {
        const defaultVars = [
          {
            id: `default-${val}`,
            name: `${found?.name || 'Standard'} All Trims Eligible (Bulk Discount)`,
            fuel_type: 'PETROL',
            transmission: 'MANUAL',
            reference_ex_showroom: 1100000,
            specifications: {}
          }
        ];
        setVariants(defaultVars as any);
        setVariantId(defaultVars[0].id);
      }
    }
  };

  const isCustomSubmission = isCustomBrand || isCustomModel || modelId === 'OTHER' || brandId === 'OTHER';

  const handleInitiateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!user) {
      router.push(`/login?redirect=/groups/create`);
      return;
    }

    if (!cityId) {
      setError('Please select a target city');
      return;
    }

    if (isCustomSubmission) {
      if (isCustomBrand && !customBrandName.trim()) {
        setError('Please enter the manufacturer brand name');
        return;
      }
      if (!customModelName.trim()) {
        setError('Please enter the vehicle model name (e.g. Mahindra XEV 9e)');
        return;
      }
    } else {
      if (!variantId && variants.length === 0) {
        setError('Please select an exact vehicle variant');
        return;
      }
    }

    setShowIntentModal(true);
  };

  const executeFinalSubmission = async () => {
    setError('');
    setSubmitting(true);
    try {
      const activeBrandObj = brands.find(b => b.id === brandId);
      const activeModelObj = models.find(m => m.id === modelId);

      const intentPayload = {
        purchase_timeline: purchaseTimeline,
        is_genuine_intent: intentGenuine,
        is_non_binding_acknowledged: intentNonBinding,
        agreed_to_contact: intentContactAgreed
      };

      const payload = isCustomSubmission ? {
        vehicle_variant_id: 'OTHER',
        city_id: cityId,
        target_members: Number(targetMembers),
        target_purchase_timeline: purchaseTimeline,
        additional_notes: additionalNotes,
        category_id: categoryId,
        custom_brand_name: isCustomBrand ? customBrandName.trim() : (activeBrandObj?.name || 'Custom'),
        custom_model_name: customModelName.trim(),
        custom_variant_name: customVariantName.trim() || `${customModelName.trim()} Standard`,
        custom_fuel_type: customFuelType,
        estimated_price: customPrice ? parseFloat(customPrice) : undefined,
        buyer_intent: intentPayload
      } : {
        vehicle_variant_id: variantId || (variants[0]?.id || `default-${modelId}`),
        city_id: cityId,
        target_members: Number(targetMembers),
        target_purchase_timeline: purchaseTimeline,
        additional_notes: additionalNotes,
        buyer_intent: intentPayload
      };

      const res = await apiFetch('/groups', {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      setShowIntentModal(false);
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
          <span>Demand Aggregation & Discovery Engine</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-navy-950">
          Start a Vehicle Buying Group
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 max-w-lg mx-auto">
          Specify your vehicle in Indore. If your exact car or model is not listed, our Automated Vehicle Intelligence Engine will search the internet, match OEM specifications, and retrieve real photos.
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

        <form onSubmit={handleInitiateSubmit} className="space-y-6">
          
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

          {/* Step 2: Brand & Model Selection */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700">3. Manufacturer Brand *</label>
              <select
                value={brandId}
                onChange={(e) => handleBrandChange(e.target.value)}
                required
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500 font-medium"
              >
                {brands.length === 0 && <option value="">Loading brands...</option>}
                {brands.map((b) => (
                  <option key={b.id} value={b.id}>{b.name}</option>
                ))}
                <option value="OTHER" className="font-bold text-brand-600 bg-orange-50">✨ Other / Brand Not Listed</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700">4. Vehicle Model *</label>
              <select
                value={modelId}
                onChange={(e) => handleModelChange(e.target.value)}
                required
                disabled={brandId === 'OTHER'}
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500 font-medium disabled:opacity-60"
              >
                {brandId === 'OTHER' ? (
                  <option value="OTHER">✨ Custom Vehicle Model (Type Below)</option>
                ) : (
                  <>
                    {models.length === 0 && <option value="">Loading models...</option>}
                    {models.map((m) => (
                      <option key={m.id} value={m.id}>{m.name}</option>
                    ))}
                    <option value="OTHER" className="font-bold text-brand-600 bg-orange-50">✨ Other / Model Not Listed</option>
                  </>
                )}
              </select>
            </div>
          </div>

          {/* Custom Vehicle Discovery Details Panel */}
          {isCustomSubmission && (
            <div className="p-4 sm:p-5 rounded-2xl bg-gradient-to-br from-orange-50/60 to-amber-50/40 border border-orange-200/80 space-y-4">
              <div className="flex items-start gap-2.5">
                <div className="p-2 bg-orange-500 text-white rounded-xl shadow-sm">
                  <Globe className="w-4 h-4 animate-pulse" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-navy-950 flex items-center gap-1.5">
                    Automated Internet Vehicle Discovery & Specification Retrieval
                    <span className="px-2 py-0.5 rounded-full bg-orange-200/80 text-orange-800 text-[10px] font-semibold">Live Web Search</span>
                  </h4>
                  <p className="text-[11px] text-slate-600 mt-0.5">
                    Enter the vehicle name. GaadiLelo will automatically query OEM specification portals, Wikimedia Commons, and open automotive datasets to retrieve real photos and variants.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                {isCustomBrand && (
                  <div className="space-y-1">
                    <label className="text-[11px] font-bold text-slate-700">Manufacturer Brand *</label>
                    <input
                      type="text"
                      placeholder="e.g. Mahindra, Maruti Suzuki, Tesla, BYD"
                      value={customBrandName}
                      onChange={(e) => setCustomBrandName(e.target.value)}
                      required={isCustomBrand}
                      className="w-full text-xs bg-white border border-slate-200 rounded-xl px-3 py-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500 font-medium"
                    />
                  </div>
                )}

                <div className="space-y-1">
                  <label className="text-[11px] font-bold text-slate-700">Vehicle Model Name *</label>
                  <input
                    type="text"
                    placeholder="e.g. Mahindra XEV 9e, WagonR, Ignis, Grand Vitara"
                    value={customModelName}
                    onChange={(e) => setCustomModelName(e.target.value)}
                    required={isCustomSubmission}
                    className="w-full text-xs bg-white border border-slate-200 rounded-xl px-3 py-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500 font-medium"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-[11px] font-bold text-slate-700">Preferred Trim / Powertrain (Optional)</label>
                  <input
                    type="text"
                    placeholder="e.g. Pack Two 79kWh EV, ZXi DualJet, Alpha Hybrid"
                    value={customVariantName}
                    onChange={(e) => setCustomVariantName(e.target.value)}
                    className="w-full text-xs bg-white border border-slate-200 rounded-xl px-3 py-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-[11px] font-bold text-slate-700">Fuel / Powertrain Type</label>
                  <select
                    value={customFuelType}
                    onChange={(e) => setCustomFuelType(e.target.value)}
                    className="w-full text-xs bg-white border border-slate-200 rounded-xl px-3 py-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500"
                  >
                    <option value="ELECTRIC">⚡ Electric (EV)</option>
                    <option value="PETROL">⛽ Petrol</option>
                    <option value="DIESEL">🛢️ Diesel</option>
                    <option value="HYBRID">🔋 Strong Hybrid</option>
                    <option value="CNG">🌱 S-CNG</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-[11px] font-bold text-slate-700">Target Ex-Showroom Budget ₹ (Optional)</label>
                  <input
                    type="number"
                    placeholder="e.g. 2190000"
                    value={customPrice}
                    onChange={(e) => setCustomPrice(e.target.value)}
                    className="w-full text-xs bg-white border border-slate-200 rounded-xl px-3 py-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Variant Selection */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700">5. Exact Variant / Powertrain *</label>
            {isCustomSubmission ? (
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-700 text-xs flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-brand-600 flex-shrink-0" />
                <span>
                  <strong>Custom Baseline Variant:</strong> A new cohort for <em>{customModelName || 'your custom vehicle'}</em> will be initiated. All additional manufacturer trims will be populated via live internet search.
                </span>
              </div>
            ) : (
              <select
                value={variantId}
                onChange={(e) => setVariantId(e.target.value)}
                required
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                {variants.length === 0 ? (
                  <option value="default-std">Standard All Trims Eligible (Bulk Discount Applicable)</option>
                ) : (
                  variants.map((v) => (
                    <option key={v.id} value={v.id}>
                      {v.name} ({v.fuel_type} • {v.transmission} • Ex-showroom: ₹{Number(v.reference_ex_showroom).toLocaleString('en-IN')})
                    </option>
                  ))
                )}
              </select>
            )}
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
                <option value={3}>3 Buyers (Fast turnaround)</option>
                <option value={5}>5 Buyers (Standard bulk tier - Recommended)</option>
                <option value={10}>10 Buyers (High volume OEM maximum discount)</option>
                <option value={15}>15 Buyers (Commercial & fleet tier)</option>
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
              <span>Review & Confirm Buying Interest</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

        </form>

      </div>

      {/* Buyer Intent Confirmation Modal (Requirement 6) */}
      {showIntentModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-950/60 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-white max-w-lg w-full rounded-3xl p-6 sm:p-8 shadow-2xl border border-slate-100 space-y-6">
            
            <div className="text-center space-y-1.5">
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 text-[11px] font-bold">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span>Indore Pilot • Buyer Intent Affirmation</span>
              </div>
              <h2 className="text-xl font-black text-navy-950">
                Confirm Your Buying Interest
              </h2>
              <p className="text-xs text-slate-500">
                Authorized dealerships formulate binding bulk discounts based on real buyer cohorts. Please verify your intent below.
              </p>
            </div>

            {/* Vehicle Summary Card */}
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/80 space-y-2">
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-500">Target Vehicle:</span>
                <span className="font-bold text-navy-950">
                  {isCustomSubmission ? (customModelName || 'Custom Vehicle') : (models.find(m => m.id === modelId)?.name || 'Selected Vehicle')}
                </span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-500">Powertrain / Trim:</span>
                <span className="font-semibold text-slate-800">
                  {isCustomSubmission ? (customVariantName || 'Standard Baseline') : (variants.find(v => v.id === variantId)?.name || 'All Trims Eligible')}
                </span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-500">Pilot Market:</span>
                <span className="font-semibold text-slate-800">Indore, Madhya Pradesh</span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-500">Target Cohort Size:</span>
                <span className="font-bold text-brand-600">{targetMembers} Verified Buyers</span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-500">Timeline:</span>
                <span className="font-semibold text-slate-800">
                  {purchaseTimeline === 'WITHIN_15_DAYS' ? 'Immediate (Within 15 Days)' : purchaseTimeline === 'WITHIN_30_DAYS' ? 'Normal (Within 30 Days)' : 'Flexible (Within 60 Days)'}
                </span>
              </div>
            </div>

            {/* Checkbox Declarations */}
            <div className="space-y-3">
              <label className="flex items-start gap-3 p-3 rounded-xl bg-slate-50/80 border border-slate-200 hover:bg-slate-50 cursor-pointer transition-colors">
                <input
                  type="checkbox"
                  checked={intentGenuine}
                  onChange={(e) => setIntentGenuine(e.target.checked)}
                  className="mt-0.5 rounded text-brand-600 focus:ring-brand-500"
                />
                <span className="text-xs text-slate-700 leading-relaxed">
                  <strong>Genuine Buying Intent:</strong> I am genuinely planning to purchase this vehicle within my specified timeline in Indore.
                </span>
              </label>

              <label className="flex items-start gap-3 p-3 rounded-xl bg-slate-50/80 border border-slate-200 hover:bg-slate-50 cursor-pointer transition-colors">
                <input
                  type="checkbox"
                  checked={intentNonBinding}
                  onChange={(e) => setIntentNonBinding(e.target.checked)}
                  className="mt-0.5 rounded text-brand-600 focus:ring-brand-500"
                />
                <span className="text-xs text-slate-700 leading-relaxed">
                  <strong>100% Free & Non-Binding:</strong> I understand that group creation and joining are completely free and non-binding, with zero financial deposit required.
                </span>
              </label>

              <label className="flex items-start gap-3 p-3 rounded-xl bg-slate-50/80 border border-slate-200 hover:bg-slate-50 cursor-pointer transition-colors">
                <input
                  type="checkbox"
                  checked={intentContactAgreed}
                  onChange={(e) => setIntentContactAgreed(e.target.checked)}
                  className="mt-0.5 rounded text-brand-600 focus:ring-brand-500"
                />
                <span className="text-xs text-slate-700 leading-relaxed">
                  <strong>Direct Quotations & Privacy:</strong> I agree to receive verified dealership quotation updates via GaadiLelo. My personal contact details remain shielded from other buyers.
                </span>
              </label>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-3 pt-2">
              <button
                type="button"
                onClick={() => setShowIntentModal(false)}
                disabled={submitting}
                className="w-1/3 py-3 border border-slate-200 hover:bg-slate-100 text-slate-700 font-bold text-xs rounded-xl transition-colors"
              >
                Back / Edit
              </button>
              <button
                type="button"
                onClick={executeFinalSubmission}
                disabled={submitting || !intentGenuine || !intentNonBinding || !intentContactAgreed}
                className="w-2/3 py-3 bg-brand-500 hover:bg-brand-600 disabled:opacity-40 text-white font-bold text-xs rounded-xl shadow-md shadow-brand-500/20 transition-all flex items-center justify-center gap-2"
              >
                {submitting ? 'Creating Group...' : 'Confirm & Launch Buying Group'}
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>

          </div>
        </div>
      )}

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
