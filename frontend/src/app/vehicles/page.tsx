'use client';

import React, { useState, useEffect, Suspense } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { 
  Car, Zap, Bike, Truck, Boxes, Filter, Search, ArrowRight, 
  CheckCircle2, Users, IndianRupee, Sparkles 
} from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { VehicleCategory, VehicleBrand, VehicleModel } from '@/types';

function VehiclesContent() {
  const searchParams = useSearchParams();
  const initialCategory = searchParams.get('category') || '';
  const initialSearch = searchParams.get('search') || '';

  const [categories, setCategories] = useState<VehicleCategory[]>([]);
  const [brands, setBrands] = useState<VehicleBrand[]>([]);
  const [models, setModels] = useState<VehicleModel[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [selectedCategory, setSelectedCategory] = useState<string>(initialCategory);
  const [selectedBrand, setSelectedBrand] = useState<string>('');
  const [selectedFuel, setSelectedFuel] = useState<string>('');
  const [search, setSearch] = useState<string>(initialSearch);

  useEffect(() => {
    async function init() {
      try {
        const [cats, brs] = await Promise.all([
          apiFetch<VehicleCategory[]>('/catalog/categories').catch(() => []),
          apiFetch<VehicleBrand[]>('/catalog/brands').catch(() => []),
        ]);
        setCategories(cats || []);
        setBrands(brs || []);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, []);

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

  const formatPrice = (p: number) => {
    if (p >= 100000) {
      return `₹${(p / 100000).toFixed(2)} Lakh`;
    }
    return `₹${p.toLocaleString('en-IN')}`;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
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
            <span className="font-bold text-xs uppercase tracking-wider text-navy-900 flex items-center gap-1.5">
              <Filter className="w-3.5 h-3.5 text-brand-500" /> Filters
            </span>
            {(selectedCategory || selectedBrand || selectedFuel || search) && (
              <button
                onClick={() => {
                  setSelectedCategory('');
                  setSelectedBrand('');
                  setSelectedFuel('');
                  setSearch('');
                }}
                className="text-[11px] text-brand-600 font-semibold hover:underline"
              >
                Clear all
              </button>
            )}
          </div>

          {/* Search Box */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-700">Search Model</label>
            <div className="flex items-center gap-2 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl">
              <Search className="w-3.5 h-3.5 text-slate-400" />
              <input
                type="text"
                placeholder="e.g. Nexon, Ather..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="bg-transparent text-xs text-slate-800 placeholder-slate-400 focus:outline-none w-full"
              />
            </div>
          </div>

          {/* Category Tabs */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-700">Category</label>
            <div className="space-y-1">
              <button
                onClick={() => setSelectedCategory('')}
                className={`w-full text-left px-3 py-2 rounded-xl text-xs font-medium transition-colors ${
                  !selectedCategory ? 'bg-orange-50 text-brand-700 font-semibold border border-orange-200' : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                All Categories
              </button>
              {categories.map((c) => (
                <button
                  key={c.id}
                  onClick={() => setSelectedCategory(c.slug)}
                  className={`w-full text-left px-3 py-2 rounded-xl text-xs font-medium transition-colors flex items-center justify-between ${
                    selectedCategory === c.slug
                      ? 'bg-orange-50 text-brand-700 font-semibold border border-orange-200'
                      : 'text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <span>{c.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Brand Filter */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-700">Manufacturer (OEM)</label>
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
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-700">Powertrain</label>
            <select
              value={selectedFuel}
              onChange={(e) => setSelectedFuel(e.target.value)}
              className="w-full text-xs bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-800 focus:outline-none"
            >
              <option value="">All Powertrains</option>
              <option value="PETROL">Petrol</option>
              <option value="DIESEL">Diesel</option>
              <option value="ELECTRIC">Electric (EV)</option>
              <option value="CNG">CNG</option>
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
            <div className="p-16 text-center text-sm text-slate-500 bg-white rounded-2xl border border-slate-200 space-y-3">
              <Car className="w-10 h-10 text-slate-300 mx-auto" />
              <p className="font-semibold text-navy-900">No vehicles match the selected criteria.</p>
              <p className="text-xs text-slate-400">Try adjusting your filters or search keywords.</p>
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
                        className="flex-1 py-2 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-xl transition-colors text-center"
                      >
                        View Variants & Groups
                      </Link>
                      <Link
                        href={`/groups/create?model_id=${m.id}`}
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
