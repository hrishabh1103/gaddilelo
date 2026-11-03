'use client';

import React, { useState, useEffect, Suspense } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { 
  Car, Zap, Bike, Truck, Boxes, Filter, Search, ArrowRight, 
  CheckCircle2, Users, IndianRupee, Sparkles, Send, Clock, Check, AlertCircle, Building2
} from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { VehicleCategory, VehicleBrand, VehicleModel } from '@/types';
import { useAuth } from '@/context/AuthContext';

function VehiclesContent() {
  const searchParams = useSearchParams();
  const initialCategory = searchParams.get('category') || '';
  const initialSearch = searchParams.get('search') || '';

  const { user } = useAuth();

  const [categories, setCategories] = useState<VehicleCategory[]>([]);
  const [brands, setBrands] = useState<VehicleBrand[]>([]);
  const [models, setModels] = useState<VehicleModel[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [selectedCategory, setSelectedCategory] = useState<string>(initialCategory);
  const [selectedBrand, setSelectedBrand] = useState<string>('');
  const [selectedFuel, setSelectedFuel] = useState<string>('');
  const [search, setSearch] = useState<string>(initialSearch);

  // Sync state with URL search parameters (e.g. from homepage brand directory or search bar)
  useEffect(() => {
    const qSearch = searchParams.get('search') || '';
    const qCat = searchParams.get('category') || '';
    const qBrand = searchParams.get('brand') || searchParams.get('brand_id') || '';
    setSearch(qSearch);
    if (qCat) setSelectedCategory(qCat);
    if (qBrand) setSelectedBrand(qBrand);
  }, [searchParams]);

  // Discovery Request Form State
  const [discName, setDiscName] = useState(user?.full_name || '');
  const [discEmail, setDiscEmail] = useState(user?.email || '');
  const [discPhone, setDiscPhone] = useState(user?.phone || '');
  const [discoverySubmitting, setDiscoverySubmitting] = useState(false);
  const [discoverySuccess, setDiscoverySuccess] = useState<any>(null);
  const [discoveryError, setDiscoveryError] = useState('');

  useEffect(() => {
    async function init() {
      try {
        const cats = await apiFetch<VehicleCategory[]>('/catalog/categories').catch(() => []);
        setCategories(cats || []);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, []);

  useEffect(() => {
    async function updateBrands() {
      try {
        const url = selectedCategory ? `/catalog/brands?category_id=${selectedCategory}` : '/catalog/brands';
        const brs = await apiFetch<VehicleBrand[]>(url).catch(() => []);
        setBrands(brs || []);
        if (selectedBrand && brs && !brs.some(b => b.id === selectedBrand)) {
          setSelectedBrand('');
        }
      } catch (e) {
        console.error(e);
      }
    }
    updateBrands();
  }, [selectedCategory]);

  useEffect(() => {
    async function fetchModels() {
      setLoading(true);
      try {
        const params = new URLSearchParams();
        if (selectedCategory) {
          const cat = categories.find(c => c.slug === selectedCategory);
          if (cat) params.append('category_id', cat.id);
        }
        if (selectedBrand) params.append('brand_id', selectedBrand);
        if (selectedFuel) params.append('fuel_type', selectedFuel);
        if (search) params.append('search', search);

        const data = await apiFetch<VehicleModel[]>(`/catalog/models?${params.toString()}`);
        setModels(data || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    fetchModels();
  }, [selectedCategory, selectedBrand, selectedFuel, search, categories]);

  const handleDiscoverySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setDiscoveryError('');
    setDiscoverySubmitting(true);

    try {
      const res = await apiFetch('/intelligence/discovery-requests', {
        method: 'POST',
        body: JSON.stringify({
          search_query: search || 'Requested Vehicle',
          category_slug: selectedCategory || 'car',
          customer_name: discName || user?.full_name || 'Customer',
          customer_email: discEmail || user?.email,
          customer_phone: discPhone || user?.phone || null,
        }),
      });
      setDiscoverySuccess(res);
    } catch (err: any) {
      setDiscoveryError(err.message || 'Failed to submit discovery request');
    } finally {
      setDiscoverySubmitting(false);
    }
  };

  const formatPrice = (p: number) => {
    if (p >= 100000) {
      return `₹${(p / 100000).toFixed(2)} Lakh`;
    }
    return `₹${p.toLocaleString('en-IN')}`;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 font-sans">
      
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-navy-950">Vehicle Catalogue</h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Browse supported vehicles in Indore, MP across all categories and start or join high-saving buying cohorts.
          </p>
        </div>

        <Link
          href="/groups/create"
          className="self-start md:self-auto px-4 py-2 bg-brand-500 hover:bg-brand-600 text-white font-semibold text-xs rounded-xl shadow-md shadow-brand-500/20 transition-all flex items-center gap-1.5"
        >
          <Sparkles className="w-4 h-4" /> Start a Custom Buying Group
        </Link>
      </div>

      {/* Main Layout: Filters Sidebar + Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        
        {/* Filters Sidebar */}
        <div className="space-y-6 bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm h-fit">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <span className="font-bold text-sm text-navy-900 flex items-center gap-1.5">
              <Filter className="w-4 h-4 text-brand-500" /> Filters
            </span>
            <button
              onClick={() => {
                setSelectedCategory('');
                setSelectedBrand('');
                setSelectedFuel('');
                setSearch('');
              }}
              className="text-[11px] font-semibold text-brand-600 hover:underline"
            >
              Reset All
            </button>
          </div>

          {/* Search Input */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700">Keyword Search</label>
            <div className="flex items-center bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs">
              <Search className="w-3.5 h-3.5 text-slate-400 mr-2 flex-shrink-0" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Model, brand (e.g. Nexon)..."
                className="w-full bg-transparent focus:outline-none text-slate-800"
              />
            </div>
          </div>

          {/* Category Filter */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700">Vehicle Category</label>
            <div className="space-y-1">
              <button
                onClick={() => setSelectedCategory('')}
                className={`w-full text-left px-3 py-2 rounded-xl text-xs font-medium transition-colors ${
                  !selectedCategory ? 'bg-orange-50 text-brand-700 font-bold' : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                All Categories
              </button>
              {categories.map((c) => (
                <button
                  key={c.id}
                  onClick={() => setSelectedCategory(c.slug)}
                  className={`w-full text-left px-3 py-2 rounded-xl text-xs font-medium transition-colors flex items-center justify-between ${
                    selectedCategory === c.slug ? 'bg-orange-50 text-brand-700 font-bold' : 'text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <span>{c.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Brand Filter */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700">Manufacturer Brand</label>
            <select
              value={selectedBrand}
              onChange={(e) => setSelectedBrand(e.target.value)}
              className="w-full text-xs bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-800 focus:outline-none"
            >
              <option value="">All Brands</option>
              {brands.map((b) => (
                <option key={b.id} value={b.id}>{b.name}</option>
              ))}
            </select>
          </div>

          {/* Fuel Type */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700">Fuel / Powertrain</label>
            <select
              value={selectedFuel}
              onChange={(e) => setSelectedFuel(e.target.value)}
              className="w-full text-xs bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-800 focus:outline-none"
            >
              <option value="">All Fuel Types</option>
              <option value="PETROL">Petrol</option>
              <option value="DIESEL">Diesel</option>
              <option value="ELECTRIC">Electric (EV)</option>
              <option value="CNG">CNG</option>
              <option value="HYBRID">Hybrid</option>
            </select>
          </div>

        </div>

        {/* Models Grid */}
        <div className="lg:col-span-3 space-y-4">
          <div className="flex items-center justify-between text-xs text-slate-500 font-medium px-1">
            <span>Showing {models.length} vehicle models</span>
            <span>Pilot Territory: Indore, Madhya Pradesh</span>
          </div>

          {loading ? (
            <div className="p-16 text-center text-sm text-slate-400 bg-white rounded-2xl border border-slate-200">
              Loading vehicles...
            </div>
          ) : models.length === 0 ? (
            
            /* ========================================================= */
            /* CUSTOMER-TRIGGERED VEHICLE DISCOVERY CARD (STEP 3 & 4) */
            /* ========================================================= */
            <div className="bg-white rounded-2xl border border-slate-200 p-8 sm:p-10 shadow-sm space-y-6">
              
              <div className="text-center max-w-xl mx-auto space-y-2">
                <div className="w-12 h-12 rounded-2xl bg-orange-100 text-brand-600 flex items-center justify-center mx-auto mb-3">
                  <Sparkles className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-black text-navy-950">
                  We couldn&apos;t find &ldquo;{search || 'this vehicle'}&rdquo; in our catalogue.
                </h3>
                <p className="text-xs sm:text-sm text-slate-500 leading-relaxed">
                  Let us discover it for you! Our automated vehicle intelligence engine scans official OEM announcements, extracts exact variant specifications, and files it for verification.
                </p>
              </div>

              {discoverySuccess ? (
                <div className="p-6 rounded-2xl bg-emerald-50 border border-emerald-200 max-w-lg mx-auto text-center space-y-3">
                  <div className="w-10 h-10 rounded-full bg-emerald-600 text-white flex items-center justify-center mx-auto">
                    <Check className="w-5 h-5 stroke-[2.5]" />
                  </div>
                  <h4 className="font-bold text-sm text-emerald-950">
                    Discovery Request Filed Successfully!
                  </h4>
                  <p className="text-xs text-emerald-800 leading-relaxed">
                    We&apos;ve extracted the specifications for <strong>{discoverySuccess.brand} {discoverySuccess.model}</strong>. Our operations team is verifying the OEM launch docket. You will receive an email the moment it is published so you can start a buying group!
                  </p>
                  <div className="pt-2 text-[11px] text-emerald-700 font-mono">
                    Tracking Job: {discoverySuccess.job_id}
                  </div>
                </div>
              ) : (
                <form onSubmit={handleDiscoverySubmit} className="max-w-md mx-auto space-y-4 bg-slate-50 p-6 rounded-2xl border border-slate-200">
                  {discoveryError && (
                    <div className="p-3 rounded-xl bg-red-50 text-red-700 text-xs flex items-center gap-2 border border-red-200">
                      <AlertCircle className="w-4 h-4 flex-shrink-0" />
                      <span>{discoveryError}</span>
                    </div>
                  )}

                  <div className="space-y-1">
                    <label className="text-xs font-bold text-slate-700">Vehicle / Model Name *</label>
                    <input
                      type="text"
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                      placeholder="e.g. Mahindra BE 6e, Curvv EV, Toyota Taisor..."
                      required
                      className="w-full text-xs bg-white border border-slate-300 rounded-xl px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="text-xs font-bold text-slate-700">Your Full Name *</label>
                    <input
                      type="text"
                      value={discName}
                      onChange={(e) => setDiscName(e.target.value)}
                      placeholder="Enter your name"
                      required
                      className="w-full text-xs bg-white border border-slate-300 rounded-xl px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="text-xs font-bold text-slate-700">Email Address (for notification) *</label>
                    <input
                      type="email"
                      value={discEmail}
                      onChange={(e) => setDiscEmail(e.target.value)}
                      placeholder="name@example.com"
                      required
                      className="w-full text-xs bg-white border border-slate-300 rounded-xl px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="text-xs font-bold text-slate-700">Phone Number (Optional)</label>
                    <input
                      type="tel"
                      value={discPhone}
                      onChange={(e) => setDiscPhone(e.target.value)}
                      placeholder="+91 98765 43210"
                      className="w-full text-xs bg-white border border-slate-300 rounded-xl px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={discoverySubmitting}
                    className="w-full py-3 bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs uppercase tracking-wider rounded-xl shadow-md shadow-brand-600/20 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    {discoverySubmitting ? (
                      <span>Analyzing OEM Announcements...</span>
                    ) : (
                      <>
                        <Send className="w-3.5 h-3.5" />
                        <span>Discover Vehicle & Notify Me</span>
                      </>
                    )}
                  </button>

                  <p className="text-[10px] text-slate-400 text-center">
                    100% Free • Automated OEM Newsroom Discovery • Non-Binding
                  </p>
                </form>
              )}

            </div>

          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {models.map((m) => (
                <div
                  key={m.id}
                  className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-md transition-all flex flex-col justify-between group"
                >
                  <div className="relative h-48 bg-slate-100 overflow-hidden">
                    <img
                      src={m.image_url || 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=600'}
                      alt={m.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                    <div className="absolute top-3 left-3 bg-white/90 backdrop-blur-md px-2.5 py-0.5 rounded-full text-[10px] font-bold text-navy-900">
                      {m.brand_name}
                    </div>
                    {m.active_groups_count > 0 && (
                      <div className="absolute bottom-3 right-3 bg-brand-500 text-white px-2 py-0.5 rounded-md text-[10px] font-bold flex items-center gap-1 shadow-sm">
                        <Users className="w-3 h-3" />
                        {m.active_groups_count} Active {m.active_groups_count === 1 ? 'Cohort' : 'Cohorts'}
                      </div>
                    )}
                  </div>

                  <div className="p-5 flex-1 flex flex-col justify-between space-y-4">
                    <div>
                      <div className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">
                        {m.body_type}
                      </div>
                      <h3 className="font-bold text-base text-navy-950 mt-0.5">
                        {m.name}
                      </h3>
                      
                      <div className="mt-2 text-xs font-semibold text-slate-900">
                        {m.min_price ? (
                          <span>
                            {formatPrice(m.min_price)} {m.max_price > m.min_price ? `– ${formatPrice(m.max_price)}` : ''}
                            <span className="text-[10px] text-slate-400 font-normal ml-1">(Ex-showroom)</span>
                          </span>
                        ) : (
                          <span className="text-slate-400">Price on request</span>
                        )}
                      </div>

                      <div className="mt-3 flex flex-wrap gap-1.5">
                        {m.variants.slice(0, 2).map((v) => (
                          <span key={v.id} className="text-[10px] px-2 py-0.5 bg-slate-100 text-slate-600 rounded">
                            {v.name}
                          </span>
                        ))}
                        {m.variants.length > 2 && (
                          <span className="text-[10px] px-1.5 py-0.5 bg-slate-50 text-slate-400 rounded">
                            +{m.variants.length - 2} more
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="pt-3 border-t border-slate-100 flex items-center gap-2">
                      <Link
                        href={`/vehicles/${m.id}`}
                        prefetch={false}
                        className="flex-1 py-2 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-xl transition-colors text-center"
                      >
                        View Variants & Groups
                      </Link>
                      <Link
                        href={`/groups/create?model_id=${m.id}`}
                        prefetch={false}
                        className="p-2 border border-slate-200 hover:border-brand-500 rounded-xl text-slate-700 hover:text-brand-600 transition-colors"
                        title="Start Group for this Vehicle"
                      >
                        <Sparkles className="w-4 h-4" />
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>

    </div>
  );
}

export default function VehiclesPage() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-sm text-slate-400">Loading vehicles...</div>}>
      <VehiclesContent />
    </Suspense>
  );
}
