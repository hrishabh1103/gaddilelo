'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { 
  Car, Zap, Bike, Truck, Boxes, Search, ArrowRight, ShieldCheck, 
  TrendingUp, Users, CheckCircle2, ChevronRight, Sparkles, Building2, MapPin,
  SlidersHorizontal, BadgePercent, Clock, ArrowUpRight, HelpCircle, Award, 
  Check, ChevronDown, PhoneCall, FileText, Star, Eye, ShieldAlert, Sparkle
} from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { VehicleCategory, BuyingGroup, VehicleModel } from '@/types';

export default function HomePage() {
  const router = useRouter();
  const [categories, setCategories] = useState<VehicleCategory[]>([]);
  const [popularGroups, setPopularGroups] = useState<BuyingGroup[]>([]);
  const [featuredModels, setFeaturedModels] = useState<VehicleModel[]>([]);
  const [loading, setLoading] = useState(true);

  // Search Filter Widget State (CarDekho Style)
  const [searchTab, setSearchTab] = useState<'budget' | 'body' | 'brand'>('budget');
  const [selectedBudget, setSelectedBudget] = useState('10-15');
  const [selectedBodyType, setSelectedBodyType] = useState('Compact SUV');
  const [selectedBrand, setSelectedBrand] = useState('Tata Motors');
  const [searchQuery, setSearchQuery] = useState('');
  const [activeGroupTab, setActiveGroupTab] = useState<'ALL' | 'CAR' | 'EV' | 'TWO_WHEELER' | 'COMMERCIAL'>('ALL');

  // Interactive Bulk Savings Visualizer State
  const [calcBudget, setCalcBudget] = useState<'under10' | '10to20' | '20to35' | 'commercial'>('10to20');
  const [calcCohortSize, setCalcCohortSize] = useState<number>(5);

  const brandName = process.env.NEXT_PUBLIC_BRAND_NAME || 'GaadiLelo';

  useEffect(() => {
    async function loadData() {
      try {
        const [cats, groups, models] = await Promise.all([
          apiFetch<VehicleCategory[]>('/catalog/categories').catch(() => []),
          apiFetch<BuyingGroup[]>('/groups').catch(() => []),
          apiFetch<VehicleModel[]>('/catalog/models').catch(() => []),
        ]);
        setCategories(cats || []);
        setPopularGroups(groups || []);
        setFeaturedModels(models || []);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleHeroSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/vehicles?search=${encodeURIComponent(searchQuery.trim())}`);
      return;
    }
    if (searchTab === 'budget') {
      router.push(`/vehicles?budget=${selectedBudget}`);
    } else if (searchTab === 'body') {
      router.push(`/vehicles?body_type=${encodeURIComponent(selectedBodyType)}`);
    } else {
      router.push(`/vehicles?search=${encodeURIComponent(selectedBrand)}`);
    }
  };

  // Filter groups according to tabs
  const filteredGroups = popularGroups.filter((g) => {
    if (activeGroupTab === 'ALL') return true;
    if (activeGroupTab === 'CAR') {
      return g.category_slug === 'car' || (!g.fuel_type?.includes('ELECTRIC') && (g.brand_name?.includes('Tata') || g.brand_name?.includes('Hyundai') || g.brand_name?.includes('Maruti') || g.brand_name?.includes('Mahindra')));
    }
    if (activeGroupTab === 'EV') {
      return g.category_slug === 'electric-vehicle' || g.fuel_type?.includes('ELECTRIC') || g.brand_name?.includes('Ather') || g.brand_name?.includes('Ola');
    }
    if (activeGroupTab === 'TWO_WHEELER') {
      return g.category_slug === 'two-wheeler' || g.brand_name?.includes('Ather') || g.brand_name?.includes('Ola') || g.brand_name?.includes('TVS');
    }
    if (activeGroupTab === 'COMMERCIAL') {
      return g.category_slug === 'commercial-vehicle' || g.brand_name?.includes('Ashok') || g.vehicle_name?.includes('Dost');
    }
    return true;
  });

  // Calculate savings for the enterprise tool
  const getSavingsEstimate = () => {
    let vehicleName = 'Tata Nexon / Hyundai Creta';
    let baseMSRP = 1250000;
    let baseDiscountRate = 0.06;

    if (calcBudget === 'under10') {
      vehicleName = 'Maruti Brezza LXi / Punch / Ather 450X';
      baseMSRP = 850000;
      baseDiscountRate = 0.05;
    } else if (calcBudget === '10to20') {
      vehicleName = 'Tata Nexon Creative / Creta EX / Scorpio-N';
      baseMSRP = 1350000;
      baseDiscountRate = 0.065;
    } else if (calcBudget === '20to35') {
      vehicleName = 'Mahindra XUV700 AX7 / Tata Harrier Fearless';
      baseMSRP = 2400000;
      baseDiscountRate = 0.075;
    } else if (calcBudget === 'commercial') {
      vehicleName = 'Ashok Leyland Bada Dost / Tata Ace SCV Fleet';
      baseMSRP = 980000;
      baseDiscountRate = 0.08;
    }

    const multiplier = calcCohortSize === 3 ? 1.0 : calcCohortSize === 5 ? 1.35 : calcCohortSize === 10 ? 1.75 : 2.1;
    const individualPromo = Math.round(baseMSRP * 0.012);
    const groupDiscount = Math.round(baseMSRP * baseDiscountRate * multiplier);
    const netExtraSavings = groupDiscount - individualPromo;

    return {
      vehicleName,
      baseMSRP,
      individualPromo,
      groupDiscount,
      netExtraSavings,
    };
  };

  const currentSavings = getSavingsEstimate();

  const getCategoryIcon = (slug: string) => {
    switch (slug) {
      case 'electric-vehicle': return <Zap className="w-5 h-5 text-amber-500" />;
      case 'two-wheeler': return <Bike className="w-5 h-5 text-blue-500" />;
      case 'commercial-vehicle': return <Truck className="w-5 h-5 text-emerald-500" />;
      case 'three-wheeler': return <Boxes className="w-5 h-5 text-purple-500" />;
      default: return <Car className="w-5 h-5 text-brand-600" />;
    }
  };

  return (
    <div className="space-y-12 sm:space-y-16 pb-20 bg-[#f8f9fa] text-slate-800 font-sans">
      
      {/* ========================================================= */}
      {/* 1. CARDEKHO-STYLE HERO SEARCH & SHOWCASE SECTION */}
      {/* ========================================================= */}
      <section className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
          
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center">
            
            {/* Left Column: CarDekho MNC Search Widget */}
            <div className="lg:col-span-7 space-y-6">
              
              <div>
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md bg-orange-50 text-brand-700 text-xs font-bold border border-orange-200/80 mb-3">
                  <Sparkles className="w-3.5 h-3.5 text-brand-600" />
                  <span>India&apos;s 1st Vehicle Group Buying Platform • Live in Indore, MP</span>
                </div>
                <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-navy-950 tracking-tight leading-tight">
                  Buy Together. <span className="text-brand-600">Save Together.</span>
                </h1>
                <p className="text-sm sm:text-base text-slate-600 mt-2 font-normal leading-relaxed">
                  Join forces with verified vehicle buyers in Indore. Authorized OEM dealerships compete with their best wholesale bulk quotations.
                </p>
              </div>

              {/* The CarDekho Tabbed Discovery Box */}
              <div className="bg-white rounded-2xl border border-slate-200 shadow-md shadow-slate-200/50 overflow-hidden">
                
                {/* Search Tabs */}
                <div className="flex border-b border-slate-200 bg-slate-50 text-xs font-bold">
                  <button
                    type="button"
                    onClick={() => setSearchTab('budget')}
                    className={`flex-1 py-3 text-center transition-colors border-b-2 ${
                      searchTab === 'budget' 
                        ? 'border-brand-600 text-brand-700 bg-white' 
                        : 'border-transparent text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    BY BUDGET
                  </button>
                  <button
                    type="button"
                    onClick={() => setSearchTab('body')}
                    className={`flex-1 py-3 text-center transition-colors border-b-2 ${
                      searchTab === 'body' 
                        ? 'border-brand-600 text-brand-700 bg-white' 
                        : 'border-transparent text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    BY BODY TYPE
                  </button>
                  <button
                    type="button"
                    onClick={() => setSearchTab('brand')}
                    className={`flex-1 py-3 text-center transition-colors border-b-2 ${
                      searchTab === 'brand' 
                        ? 'border-brand-600 text-brand-700 bg-white' 
                        : 'border-transparent text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    BY BRAND
                  </button>
                </div>

                {/* Form Controls */}
                <form onSubmit={handleHeroSearch} className="p-5 sm:p-6 space-y-4">
                  
                  {/* Dynamic Selector based on Tab */}
                  {searchTab === 'budget' && (
                    <div className="space-y-2">
                      <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                        Select Price Range in Indore
                      </label>
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                        {[
                          { id: 'under-5', label: 'Under ₹5 Lakh' },
                          { id: '5-10', label: '₹5 - 10 Lakh' },
                          { id: '10-15', label: '₹10 - 15 Lakh' },
                          { id: '15-25', label: '₹15 - 25 Lakh+' },
                        ].map((b) => (
                          <button
                            key={b.id}
                            type="button"
                            onClick={() => setSelectedBudget(b.id)}
                            className={`py-2 px-3 rounded-lg text-xs font-bold border transition-all text-center ${
                              selectedBudget === b.id
                                ? 'bg-orange-50 border-brand-500 text-brand-700 shadow-sm'
                                : 'bg-white border-slate-200 text-slate-700 hover:border-slate-300'
                            }`}
                          >
                            {b.label}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {searchTab === 'body' && (
                    <div className="space-y-2">
                      <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                        Select Vehicle Category
                      </label>
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                        {[
                          'Compact SUV',
                          'Mid-Size SUV',
                          'Electric Car/EV',
                          'Commercial Fleet',
                        ].map((body) => (
                          <button
                            key={body}
                            type="button"
                            onClick={() => setSelectedBodyType(body)}
                            className={`py-2 px-3 rounded-lg text-xs font-bold border transition-all text-center ${
                              selectedBodyType === body
                                ? 'bg-orange-50 border-brand-500 text-brand-700 shadow-sm'
                                : 'bg-white border-slate-200 text-slate-700 hover:border-slate-300'
                            }`}
                          >
                            {body}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {searchTab === 'brand' && (
                    <div className="space-y-2">
                      <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                        Select Authorized Manufacturer
                      </label>
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                        {['Tata Motors', 'Hyundai', 'Maruti Suzuki', 'Mahindra'].map((b) => (
                          <button
                            key={b}
                            type="button"
                            onClick={() => setSelectedBrand(b)}
                            className={`py-2 px-3 rounded-lg text-xs font-bold border transition-all text-center ${
                              selectedBrand === b
                                ? 'bg-orange-50 border-brand-500 text-brand-700 shadow-sm'
                                : 'bg-white border-slate-200 text-slate-700 hover:border-slate-300'
                            }`}
                          >
                            {b}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Free text search option */}
                  <div className="pt-2">
                    <div className="flex items-center bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5">
                      <Search className="w-4 h-4 text-slate-400 mr-2 flex-shrink-0" />
                      <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Or search specific model (e.g. Nexon, Creta, Brezza, Ather 450X)..."
                        className="w-full text-xs text-slate-800 placeholder-slate-400 bg-transparent focus:outline-none"
                      />
                    </div>
                  </div>

                  {/* Primary CarDekho Search Action */}
                  <div className="flex flex-col sm:flex-row items-center gap-3 pt-2">
                    <button
                      type="submit"
                      className="w-full sm:flex-1 py-3 px-6 bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs uppercase tracking-wider rounded-xl shadow-md shadow-brand-600/25 transition-all flex items-center justify-center gap-2"
                    >
                      <Search className="w-4 h-4" />
                      <span>Search Vehicles & Group Discounts</span>
                    </button>
                    
                    <Link
                      href="/groups/create"
                      className="w-full sm:w-auto py-3 px-5 bg-navy-950 hover:bg-slate-900 text-white font-bold text-xs rounded-xl transition-colors flex items-center justify-center gap-1.5"
                    >
                      <span>Start a Group</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>

                </form>

                {/* Popular Search Tags Bar */}
                <div className="bg-slate-50/80 px-5 py-3 border-t border-slate-200/80 text-xs flex flex-wrap items-center gap-2 text-slate-500">
                  <span className="font-bold text-slate-700 text-[11px] uppercase">Popular in Indore:</span>
                  <Link href="/vehicles?search=Nexon" className="hover:text-brand-600 underline decoration-slate-300">
                    Tata Nexon
                  </Link>
                  <span>•</span>
                  <Link href="/vehicles?search=Creta" className="hover:text-brand-600 underline decoration-slate-300">
                    Hyundai Creta
                  </Link>
                  <span>•</span>
                  <Link href="/vehicles?search=Brezza" className="hover:text-brand-600 underline decoration-slate-300">
                    Maruti Brezza
                  </Link>
                  <span>•</span>
                  <Link href="/vehicles?search=Ather" className="hover:text-brand-600 underline decoration-slate-300">
                    Ather 450X EV
                  </Link>
                  <span>•</span>
                  <Link href="/vehicles?search=Scorpio" className="hover:text-brand-600 underline decoration-slate-300">
                    Scorpio-N
                  </Link>
                </div>

              </div>

            </div>

            {/* Right Column: High-End Automotive Deal Showcase (CarDekho Style) */}
            <div className="lg:col-span-5">
              
              <div className="bg-white rounded-2xl border border-slate-200/90 shadow-lg p-5 sm:p-6 space-y-4 relative overflow-hidden">
                
                {/* Official Deal Badge */}
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
                    <span className="text-xs font-bold text-navy-950 uppercase tracking-wider">
                      Featured Indore Cohort
                    </span>
                  </div>
                  <span className="text-[10px] font-bold font-mono bg-slate-100 text-slate-700 px-2 py-0.5 rounded">
                    #IND-NEXON-04
                  </span>
                </div>

                {/* Crisp Vehicle Photography */}
                <div className="relative rounded-xl overflow-hidden aspect-[16/10] bg-slate-100 border border-slate-100">
                  <img
                    src="https://images.unsplash.com/photo-1609521263047-f8f205293f24?w=800&auto=format&fit=crop&q=80"
                    alt="Tata Nexon Dealership Group"
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute top-2.5 left-2.5 bg-emerald-600 text-white text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-md shadow-sm">
                    Offers Available (3 Bids)
                  </div>
                  <div className="absolute bottom-2.5 right-2.5 bg-navy-950/80 backdrop-blur-md text-white text-[11px] font-semibold px-2.5 py-0.5 rounded">
                    Indore, MP Delivery
                  </div>
                </div>

                {/* Model and Deal Details */}
                <div>
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-xs text-slate-500 font-semibold">Tata Motors</span>
                      <h3 className="text-lg font-black text-navy-950">Tata Nexon Creative Plus</h3>
                      <p className="text-xs text-slate-500">1.2L Turbo Petrol • Manual • 5 Seater</p>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] text-slate-400 uppercase font-semibold block">Ex-Showroom</span>
                      <span className="text-sm font-bold text-slate-800">₹11,69,000*</span>
                    </div>
                  </div>
                </div>

                {/* CarDekho Group Deal Box */}
                <div className="bg-emerald-50 rounded-xl p-3.5 border border-emerald-200 flex items-center justify-between">
                  <div>
                    <span className="text-[11px] font-bold text-emerald-800 uppercase tracking-wider block">
                      Sanghi Brothers (Official Dealership)
                    </span>
                    <span className="text-xs text-emerald-700">Exclusive Bulk Cohort Discount</span>
                  </div>
                  <div className="text-right">
                    <span className="text-base font-black text-emerald-700">₹80,000 OFF</span>
                    <span className="text-[10px] text-emerald-600 block">+ Free Ceramic Coating</span>
                  </div>
                </div>

                {/* Cohort Progress */}
                <div className="space-y-1.5 pt-1">
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-500 font-medium">Buyer Capacity</span>
                    <span className="font-bold text-navy-900">5 of 5 Joined (Target Reached)</span>
                  </div>
                  <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                    <div className="bg-emerald-500 h-full w-full rounded-full" />
                  </div>
                </div>

                {/* Actions */}
                <div className="pt-2 flex gap-2">
                  <Link
                    href="/groups"
                    className="flex-1 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs text-center rounded-xl transition-colors shadow-sm"
                  >
                    Compare Dealership Offers
                  </Link>
                  <Link
                    href="/vehicles"
                    className="py-2.5 px-4 border border-slate-200 hover:bg-slate-50 text-slate-700 font-bold text-xs rounded-xl transition-colors"
                  >
                    Explore Model
                  </Link>
                </div>

              </div>

            </div>

          </div>

        </div>
      </section>


      {/* ========================================================= */}
      {/* 2. CORPORATE TRUSTMARKS & STATS (CARDEKHO ENTERPRISE STRIP) */}
      {/* ========================================================= */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center divide-y md:divide-y-0 md:divide-x divide-slate-100">
            
            <div className="pt-3 md:pt-0">
              <span className="text-2xl sm:text-3xl font-black text-navy-950 block">3,450+</span>
              <span className="text-xs font-semibold text-slate-500 mt-0.5 block">Verified Buyers Pooled</span>
              <span className="text-[11px] text-emerald-600 font-medium">Active in Indore Pilot</span>
            </div>

            <div className="pt-3 md:pt-0">
              <span className="text-2xl sm:text-3xl font-black text-navy-950 block">48+</span>
              <span className="text-xs font-semibold text-slate-500 mt-0.5 block">Authorized Dealerships</span>
              <span className="text-[11px] text-slate-400">Tata, Hyundai, Maruti, Mahindra</span>
            </div>

            <div className="pt-3 md:pt-0">
              <span className="text-2xl sm:text-3xl font-black text-emerald-600 block">₹78,000</span>
              <span className="text-xs font-semibold text-slate-500 mt-0.5 block">Avg. Saving Per Buyer</span>
              <span className="text-[11px] text-slate-400">Beyond solitary walk-in pricing</span>
            </div>

            <div className="pt-3 md:pt-0">
              <span className="text-2xl sm:text-3xl font-black text-brand-600 block">₹0 Fee</span>
              <span className="text-xs font-semibold text-slate-500 mt-0.5 block">100% Free & Non-Binding</span>
              <span className="text-[11px] text-slate-400">Zero purchase lock-in</span>
            </div>

          </div>
        </div>
      </section>


      {/* ========================================================= */}
      {/* 3. POPULAR BUYING GROUPS (CARDEKHO TABBED VEHICLE SHOWCASE) */}
      {/* ========================================================= */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header & Category Filter Tabs */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-6 gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 text-xs font-bold text-brand-600 uppercase tracking-wider mb-1">
              <span className="w-2 h-2 rounded-full bg-brand-500 animate-ping" />
              <span>Live Bidding & Available Quotations</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-navy-950">
              Active Buying Groups in Indore
            </h2>
          </div>

          <Link
            href="/groups"
            className="text-xs font-bold text-brand-600 hover:text-brand-700 flex items-center gap-1 self-start md:self-auto"
          >
            <span>View All Buying Groups ({popularGroups.length})</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {/* Tab Pills */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2 mb-6 text-xs font-bold scrollbar-none">
          <button
            type="button"
            onClick={() => setActiveGroupTab('ALL')}
            className={`px-4 py-2 rounded-xl transition-all whitespace-nowrap ${
              activeGroupTab === 'ALL'
                ? 'bg-navy-950 text-white shadow-sm'
                : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
            }`}
          >
            All Active Cohorts ({popularGroups.length})
          </button>
          <button
            type="button"
            onClick={() => setActiveGroupTab('CAR')}
            className={`px-4 py-2 rounded-xl transition-all whitespace-nowrap ${
              activeGroupTab === 'CAR'
                ? 'bg-navy-950 text-white shadow-sm'
                : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
            }`}
          >
            SUVs & Passenger Cars
          </button>
          <button
            type="button"
            onClick={() => setActiveGroupTab('EV')}
            className={`px-4 py-2 rounded-xl transition-all whitespace-nowrap ${
              activeGroupTab === 'EV'
                ? 'bg-navy-950 text-white shadow-sm'
                : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
            }`}
          >
            Electric Vehicles (EVs)
          </button>
          <button
            type="button"
            onClick={() => setActiveGroupTab('TWO_WHEELER')}
            className={`px-4 py-2 rounded-xl transition-all whitespace-nowrap ${
              activeGroupTab === 'TWO_WHEELER'
                ? 'bg-navy-950 text-white shadow-sm'
                : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
            }`}
          >
            Two-Wheelers
          </button>
          <button
            type="button"
            onClick={() => setActiveGroupTab('COMMERCIAL')}
            className={`px-4 py-2 rounded-xl transition-all whitespace-nowrap ${
              activeGroupTab === 'COMMERCIAL'
                ? 'bg-navy-950 text-white shadow-sm'
                : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
            }`}
          >
            Commercial Fleets
          </button>
        </div>

        {/* Group Grid */}
        {loading ? (
          <div className="p-12 text-center text-xs text-slate-400 bg-white rounded-2xl border border-slate-200">
            Loading active groups in Indore...
          </div>
        ) : filteredGroups.length === 0 ? (
          <div className="p-10 text-center bg-white rounded-2xl border border-slate-200 space-y-3">
            <p className="text-sm font-semibold text-slate-700">No active cohorts in this category currently.</p>
            <p className="text-xs text-slate-500">Be the first to start a group for this category in Indore!</p>
            <Link
              href="/groups/create"
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-brand-600 text-white text-xs font-bold rounded-xl"
            >
              Start Group
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {filteredGroups.slice(0, 8).map((group) => {
              const progressPct = Math.min(100, Math.round((group.current_members_count / group.target_members) * 100));

              return (
                <div
                  key={group.id}
                  className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-md hover:border-slate-300 transition-all flex flex-col justify-between group"
                >
                  {/* Card Media */}
                  <div className="relative h-44 bg-slate-100 overflow-hidden">
                    <img
                      src={group.vehicle_image_url || 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=600'}
                      alt={group.vehicle_name || 'Vehicle'}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                    
                    {/* Status Badge */}
                    <div className="absolute top-2.5 left-2.5">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider shadow-sm ${
                        group.status === 'OFFERS_AVAILABLE'
                          ? 'bg-emerald-600 text-white'
                          : group.status === 'BIDDING_OPEN'
                          ? 'bg-blue-600 text-white'
                          : 'bg-brand-600 text-white'
                      }`}>
                        {group.status.replace('_', ' ')}
                      </span>
                    </div>

                    <div className="absolute bottom-2 right-2 bg-navy-950/80 backdrop-blur-md text-white px-2 py-0.5 rounded text-[10px] font-mono">
                      {group.group_code}
                    </div>
                  </div>

                  {/* Body Content */}
                  <div className="p-4 flex-1 flex flex-col justify-between space-y-4">
                    <div>
                      <div className="text-[11px] font-semibold text-slate-400">
                        {group.brand_name} • {group.city_name}
                      </div>
                      <h3 className="font-bold text-sm text-navy-950 line-clamp-1 mt-0.5">
                        {group.vehicle_name}
                      </h3>
                      <p className="text-xs text-slate-500 line-clamp-1 mt-0.5">
                        {group.variant_name}
                      </p>
                    </div>

                    {/* Progress Bar */}
                    <div className="space-y-1.5 pt-2 border-t border-slate-100">
                      <div className="flex justify-between items-center text-xs">
                        <span className="text-slate-500 font-medium">Cohort Status</span>
                        <span className="font-bold text-navy-900">
                          {group.current_members_count} / {group.target_members} Buyers Joined
                        </span>
                      </div>
                      
                      <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                        <div
                          className="bg-brand-500 h-full rounded-full transition-all duration-500"
                          style={{ width: `${progressPct}%` }}
                        />
                      </div>

                      <div className="flex justify-between text-[10px] text-slate-400 pt-1">
                        <span>Timeline: {group.target_purchase_timeline.replace(/_/g, ' ')}</span>
                        {group.approved_quotations_count ? (
                          <span className="text-emerald-600 font-bold">
                            {group.approved_quotations_count} Offers Live
                          </span>
                        ) : (
                          <span className="text-slate-400">Qualifying Stage</span>
                        )}
                      </div>
                    </div>

                    {/* Action */}
                    <Link
                      href={`/groups/${group.id}`}
                      className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs text-center rounded-xl transition-colors flex items-center justify-center gap-1"
                    >
                      <span>{group.status === 'OFFERS_AVAILABLE' ? 'Compare Offers' : 'View Group Details'}</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}

      </section>


      {/* ========================================================= */}
      {/* 4. CARDEKHO-STYLE BRAND DIRECTORY */}
      {/* ========================================================= */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 space-y-6 shadow-sm">
          
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg sm:text-xl font-bold text-navy-950">Popular Automotive Brands</h3>
              <p className="text-xs text-slate-500">Authorized OEM dealerships actively competing in Indore</p>
            </div>
            <Link href="/vehicles" className="text-xs font-bold text-brand-600 hover:text-brand-700 flex items-center gap-1">
              <span>View All Brands</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
            {[
              { name: 'Tata Motors', models: 'Nexon, Harrier, Safari', query: 'Tata' },
              { name: 'Hyundai', models: 'Creta, Venue, Verna', query: 'Hyundai' },
              { name: 'Maruti Suzuki', models: 'Brezza, Swift, Ertiga', query: 'Maruti' },
              { name: 'Mahindra', models: 'Scorpio-N, XUV700, Thar', query: 'Mahindra' },
              { name: 'Ather Energy', models: '450X, Rizta EV', query: 'Ather' },
              { name: 'Ola Electric', models: 'S1 Pro, S1 Air', query: 'Ola' },
              { name: 'TVS Motor', models: 'iQube EV, Raider, Apache', query: 'TVS' },
              { name: 'Ashok Leyland', models: 'Bada Dost, Dost+', query: 'Ashok' },
            ].map((brand) => (
              <Link
                key={brand.name}
                href={`/vehicles?search=${encodeURIComponent(brand.query)}`}
                className="p-3 bg-slate-50 hover:bg-orange-50/60 border border-slate-200 hover:border-brand-300 rounded-xl transition-all text-center group flex flex-col justify-center items-center"
              >
                <div className="w-8 h-8 rounded-lg bg-white border border-slate-200 flex items-center justify-center font-black text-xs text-navy-950 group-hover:text-brand-600 transition-colors mb-1.5 shadow-xs">
                  {brand.name.substring(0, 2).toUpperCase()}
                </div>
                <h4 className="font-bold text-xs text-navy-950 group-hover:text-brand-600 transition-colors">
                  {brand.name}
                </h4>
                <span className="text-[10px] text-slate-400 mt-0.5 line-clamp-1">{brand.models}</span>
              </Link>
            ))}
          </div>

        </div>
      </section>


      {/* ========================================================= */}
      {/* 5. INTERACTIVE CARDEKHO BULK SAVINGS ESTIMATOR */}
      {/* ========================================================= */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="bg-navy-950 rounded-2xl p-6 sm:p-10 text-white shadow-xl relative overflow-hidden">
          
          <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center">
            
            {/* Left Controls */}
            <div className="lg:col-span-7 space-y-6">
              
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md bg-brand-500/20 text-orange-300 text-xs font-bold border border-brand-500/30">
                <SlidersHorizontal className="w-3.5 h-3.5" />
                <span>Group Buying Savings Calculator</span>
              </div>

              <div>
                <h3 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
                  Estimate Your Real On-Road Group Discount
                </h3>
                <p className="text-xs sm:text-sm text-slate-300 mt-2 leading-relaxed">
                  Bulk fleet margin discounts scale exponentially with cohort volume. Select your budget segment and group size to see verified Indore estimates.
                </p>
              </div>

              {/* Segment Toggles */}
              <div className="space-y-2">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block">
                  1. Choose Vehicle Segment
                </span>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  <button
                    type="button"
                    onClick={() => setCalcBudget('under10')}
                    className={`py-2 px-3 rounded-xl text-xs font-bold transition-all border ${
                      calcBudget === 'under10'
                        ? 'bg-brand-600 text-white border-brand-500 shadow-md'
                        : 'bg-navy-900 text-slate-300 border-navy-800 hover:bg-navy-850'
                    }`}
                  >
                    Entry / EV Scooter
                  </button>
                  <button
                    type="button"
                    onClick={() => setCalcBudget('10to20')}
                    className={`py-2 px-3 rounded-xl text-xs font-bold transition-all border ${
                      calcBudget === '10to20'
                        ? 'bg-brand-600 text-white border-brand-500 shadow-md'
                        : 'bg-navy-900 text-slate-300 border-navy-800 hover:bg-navy-850'
                    }`}
                  >
                    Compact SUV
                  </button>
                  <button
                    type="button"
                    onClick={() => setCalcBudget('20to35')}
                    className={`py-2 px-3 rounded-xl text-xs font-bold transition-all border ${
                      calcBudget === '20to35'
                        ? 'bg-brand-600 text-white border-brand-500 shadow-md'
                        : 'bg-navy-900 text-slate-300 border-navy-800 hover:bg-navy-850'
                    }`}
                  >
                    Mid / 7-Str SUV
                  </button>
                  <button
                    type="button"
                    onClick={() => setCalcBudget('commercial')}
                    className={`py-2 px-3 rounded-xl text-xs font-bold transition-all border ${
                      calcBudget === 'commercial'
                        ? 'bg-brand-600 text-white border-brand-500 shadow-md'
                        : 'bg-navy-900 text-slate-300 border-navy-800 hover:bg-navy-850'
                    }`}
                  >
                    Commercial SCV
                  </button>
                </div>
              </div>

              {/* Group Size Toggles */}
              <div className="space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-bold uppercase tracking-wider text-slate-400">
                    2. Cohort Volume (Buyers)
                  </span>
                  <span className="text-orange-400 font-bold font-mono">
                    {calcCohortSize} Buyers Pooled
                  </span>
                </div>
                <div className="grid grid-cols-4 gap-2">
                  {[3, 5, 10, 15].map((s) => (
                    <button
                      key={s}
                      type="button"
                      onClick={() => setCalcCohortSize(s)}
                      className={`py-2.5 rounded-xl text-xs font-bold transition-all border ${
                        calcCohortSize === s
                          ? 'bg-white text-navy-950 border-white shadow-md font-black'
                          : 'bg-navy-900 text-slate-300 border-navy-800 hover:bg-navy-850'
                      }`}
                    >
                      {s} Buyers
                    </button>
                  ))}
                </div>
              </div>

              <div className="pt-2">
                <Link
                  href="/groups/create"
                  className="inline-flex items-center gap-2 px-6 py-3 bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs rounded-xl shadow-lg shadow-brand-600/30 transition-all uppercase tracking-wider"
                >
                  <span>Start Cohort with this Tier</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>

            </div>

            {/* Right Comparison Box */}
            <div className="lg:col-span-5">
              <div className="bg-navy-900/90 rounded-2xl p-6 border border-navy-700/80 shadow-2xl space-y-5">
                
                <div className="flex justify-between items-center pb-3 border-b border-navy-800">
                  <span className="text-xs text-slate-400 font-semibold">{currentSavings.vehicleName}</span>
                  <span className="text-[10px] font-bold uppercase bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded border border-emerald-500/30">
                    Indore Benchmark
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-navy-950 p-4 rounded-xl border border-navy-800">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                      Solo Showroom Walk-in
                    </span>
                    <span className="text-base font-bold text-slate-400 line-through">
                      ₹{currentSavings.individualPromo.toLocaleString('en-IN')}
                    </span>
                    <p className="text-[10px] text-slate-500 mt-1">Retail promotional cap</p>
                  </div>

                  <div className="bg-emerald-950/50 p-4 rounded-xl border border-emerald-500/30">
                    <span className="text-[10px] uppercase font-bold text-emerald-400 block mb-1">
                      GaadiLelo Group Cohort
                    </span>
                    <span className="text-xl sm:text-2xl font-black text-emerald-300">
                      ₹{currentSavings.groupDiscount.toLocaleString('en-IN')}
                    </span>
                    <p className="text-[10px] text-emerald-400/80 mt-1">Direct fleet wholesale margin</p>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-gradient-to-r from-brand-600/20 to-orange-500/20 border border-brand-500/30 flex items-center justify-between">
                  <div>
                    <span className="text-xs text-orange-200 font-bold block">Extra Net Saving Per Buyer</span>
                    <span className="text-[10px] text-slate-400">Audited ₹0 handling fee guarantee</span>
                  </div>
                  <span className="text-xl font-black text-orange-300">
                    +₹{currentSavings.netExtraSavings.toLocaleString('en-IN')}
                  </span>
                </div>

                <div className="space-y-2 text-[11px] text-slate-300 pt-1 border-t border-navy-800">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                    <span>Includes MP RTO registration & statutory zero-dep insurance.</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                    <span>Paperwork and car delivery executed directly at OEM showroom.</span>
                  </div>
                </div>

              </div>
            </div>

          </div>

        </div>

      </section>


      {/* ========================================================= */}
      {/* 6. HOW IT WORKS (CARDEKHO 4-STEP WORKFLOW) */}
      {/* ========================================================= */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="text-center max-w-2xl mx-auto mb-10 space-y-2">
          <span className="text-xs font-bold text-brand-600 uppercase tracking-wider">Transparent Process</span>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-navy-950">
            How Vehicle Group Buying Works
          </h2>
          <p className="text-xs sm:text-sm text-slate-500">
            We replace solitary haggling with transparent dealership reverse auctions.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3 relative">
            <div className="w-9 h-9 rounded-xl bg-orange-100 text-brand-700 font-black text-sm flex items-center justify-center">
              01
            </div>
            <h3 className="font-bold text-base text-navy-950">Select Your Vehicle</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Choose your exact car, motorcycle, EV, or commercial fleet model, powertrain, and delivery timeline in Indore.
            </p>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3 relative">
            <div className="w-9 h-9 rounded-xl bg-blue-100 text-blue-700 font-black text-sm flex items-center justify-center">
              02
            </div>
            <h3 className="font-bold text-base text-navy-950">Join or Create Cohort</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Join an existing Indore buyer cohort (3 to 10 buyers) or start a new group in 30 seconds with ₹0 commitment.
            </p>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3 relative">
            <div className="w-9 h-9 rounded-xl bg-purple-100 text-purple-700 font-black text-sm flex items-center justify-center">
              03
            </div>
            <h3 className="font-bold text-base text-navy-950">Dealerships Compete</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Once target members join, verified OEM dealerships submit their sharpest wholesale quotations in a competitive bidding room.
            </p>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3 relative">
            <div className="w-9 h-9 rounded-xl bg-emerald-100 text-emerald-700 font-black text-sm flex items-center justify-center">
              04
            </div>
            <h3 className="font-bold text-base text-navy-950">Direct Showroom Delivery</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Compare transparent line-item quotes, pick the winning dealer, and take delivery with manufacturer warranty at the showroom.
            </p>
          </div>

        </div>

      </section>


      {/* ========================================================= */}
      {/* 7. WHY GAADILELO (MNC COMPARISON TABLE) */}
      {/* ========================================================= */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-10 shadow-sm space-y-8">
          
          <div className="text-center max-w-2xl mx-auto space-y-2">
            <span className="text-xs font-bold text-brand-600 uppercase tracking-wider">The Group Buying Advantage</span>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-navy-950">
              Traditional Showroom Walk-in vs. GaadiLelo
            </h2>
            <p className="text-xs sm:text-sm text-slate-500">
              Why thousands of Indian buyers are switching to organized group purchasing.
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 text-slate-700 font-bold uppercase">
                  <th className="py-3 px-4">Feature / Parameter</th>
                  <th className="py-3 px-4 text-slate-500">Traditional Solo Buyer Walk-In</th>
                  <th className="py-3 px-4 text-brand-700 bg-orange-50/60 font-black">GaadiLelo Group Cohort</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                <tr>
                  <td className="py-3.5 px-4 font-bold text-navy-950">Pricing Leverage</td>
                  <td className="py-3.5 px-4 text-slate-500">Solitary retail markup; minimal room for bargaining (₹5,000 - ₹15,000 max)</td>
                  <td className="py-3.5 px-4 font-semibold text-emerald-700 bg-orange-50/30">Bulk fleet corporate discount tier (Save ₹50,000 - ₹1,40,000+)</td>
                </tr>
                <tr>
                  <td className="py-3.5 px-4 font-bold text-navy-950">Dealership Competition</td>
                  <td className="py-3.5 px-4 text-slate-500">Must physically visit multiple showrooms across Indore over weekends</td>
                  <td className="py-3.5 px-4 font-semibold text-emerald-700 bg-orange-50/30">Reverse auction: Multiple OEM dealerships bid online to win the cohort</td>
                </tr>
                <tr>
                  <td className="py-3.5 px-4 font-bold text-navy-950">Dealer Handling / Logistics Markups</td>
                  <td className="py-3.5 px-4 text-red-600 font-medium">Often charged ₹15,000 - ₹35,000 illegally under &ldquo;handling charges&rdquo;</td>
                  <td className="py-3.5 px-4 font-semibold text-emerald-700 bg-orange-50/30">100% Platform Audited: Mandatory ₹0 handling/logistics charges</td>
                </tr>
                <tr>
                  <td className="py-3.5 px-4 font-bold text-navy-950">Buyer Privacy</td>
                  <td className="py-3.5 px-4 text-red-600 font-medium">Phone number entered into dealer CRMs leads to months of telecaller spam</td>
                  <td className="py-3.5 px-4 font-semibold text-emerald-700 bg-orange-50/30">Strict PII Shield: Contact info shared ONLY if you request a callback</td>
                </tr>
                <tr>
                  <td className="py-3.5 px-4 font-bold text-navy-950">Commitment & Flexibility</td>
                  <td className="py-3.5 px-4 text-slate-500">Showrooms demand immediate non-refundable booking tokens</td>
                  <td className="py-3.5 px-4 font-semibold text-emerald-700 bg-orange-50/30">100% Non-Binding: Joining is free; accept or walk away anytime</td>
                </tr>
                <tr>
                  <td className="py-3.5 px-4 font-bold text-navy-950">Delivery & Paperwork</td>
                  <td className="py-3.5 px-4 text-slate-500">Standard queue allocation</td>
                  <td className="py-3.5 px-4 font-semibold text-emerald-700 bg-orange-50/30">Priority cohort vehicle allocation directly at authorized OEM showroom</td>
                </tr>
              </tbody>
            </table>
          </div>

        </div>

      </section>


      {/* ========================================================= */}
      {/* 8. AUTHORIZED INDORE DEALERSHIP PARTNER NETWORK */}
      {/* ========================================================= */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="bg-slate-100 rounded-2xl p-6 sm:p-8 border border-slate-200">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
            <div>
              <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Indore Pilot Network</span>
              <h3 className="text-xl font-bold text-navy-950">Verified OEM Franchised Dealerships</h3>
              <p className="text-xs text-slate-500">Every quotation is issued by a licensed franchise dealership with official manufacturer warranty.</p>
            </div>
            <Link
              href="/register?role=DEALER"
              className="px-4 py-2 bg-white hover:bg-slate-50 text-slate-800 text-xs font-bold rounded-xl border border-slate-200 self-start sm:self-auto shadow-sm"
            >
              Dealership Partner Onboarding
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded-xl border border-slate-200">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-bold text-xs text-navy-950">Sanghi Brothers (Indore) Ltd.</h4>
                <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-1.5 py-0.5 rounded">VERIFIED OEM</span>
              </div>
              <p className="text-[11px] text-slate-500">Authorized Dealer: Tata Motors, Mahindra</p>
              <p className="text-[10px] text-slate-400 mt-1">Showrooms: AB Road, Manoramaganj, Vijay Nagar</p>
            </div>

            <div className="bg-white p-4 rounded-xl border border-slate-200">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-bold text-xs text-navy-950">Shreeji Automotives Indore</h4>
                <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-1.5 py-0.5 rounded">VERIFIED OEM</span>
              </div>
              <p className="text-[11px] text-slate-500">Authorized Dealer: Maruti Suzuki Arena & Nexa</p>
              <p className="text-[10px] text-slate-400 mt-1">Showrooms: Ring Road, Dewas Naka</p>
            </div>

            <div className="bg-white p-4 rounded-xl border border-slate-200">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-bold text-xs text-navy-950">Ather Space Indore (Palasia)</h4>
                <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-1.5 py-0.5 rounded">VERIFIED OEM</span>
              </div>
              <p className="text-[11px] text-slate-500">Authorized Experience Center: Ather Energy EV</p>
              <p className="text-[10px] text-slate-400 mt-1">Experience Center: New Palasia, Indore</p>
            </div>
          </div>
        </div>

      </section>


      {/* ========================================================= */}
      {/* 9. TESTIMONIALS (CLEARLY LABELED DEMO CONTENT) */}
      {/* ========================================================= */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="text-center max-w-2xl mx-auto mb-8 space-y-1">
          <span className="text-[10px] font-bold uppercase tracking-wider bg-slate-200 text-slate-700 px-3 py-1 rounded-full">
            Early Pilot Feedback (Demo Representative Content)
          </span>
          <h2 className="text-2xl font-bold text-navy-950 pt-2">What Indore Buyers & Dealers Say</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
            <div className="flex items-center gap-1 text-amber-500 mb-3">
              {[...Array(5)].map((_, i) => (
                <Star key={i} className="w-3.5 h-3.5 fill-current" />
              ))}
            </div>
            <p className="text-xs text-slate-600 leading-relaxed italic">
              &ldquo;Four of us in Indore were looking to buy the Tata Nexon. We pooled our group on GaadiLelo, and Sanghi Motors gave us an ₹80,000 on-road discount each plus complimentary mats and coating!&rdquo;
            </p>
            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-orange-100 text-brand-700 font-bold text-xs flex items-center justify-center">
                RS
              </div>
              <div>
                <h4 className="font-bold text-xs text-navy-900">Rahul Sharma</h4>
                <p className="text-[10px] text-slate-400">Vijay Nagar, Indore • Nexon Cohort</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
            <div className="flex items-center gap-1 text-amber-500 mb-3">
              {[...Array(5)].map((_, i) => (
                <Star key={i} className="w-3.5 h-3.5 fill-current" />
              ))}
            </div>
            <p className="text-xs text-slate-600 leading-relaxed italic">
              &ldquo;Negotiating battery addons and charger installation alone was confusing. Through GaadiLelo, our 6-member Ather 450X cohort received clean quotations directly from authorized dealers.&rdquo;
            </p>
            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 font-bold text-xs flex items-center justify-center">
                PV
              </div>
              <div>
                <h4 className="font-bold text-xs text-navy-900">Priya Verma</h4>
                <p className="text-[10px] text-slate-400">Palasia, Indore • Ather EV Cohort</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
            <div className="flex items-center gap-1 text-amber-500 mb-3">
              {[...Array(5)].map((_, i) => (
                <Star key={i} className="w-3.5 h-3.5 fill-current" />
              ))}
            </div>
            <p className="text-xs text-slate-600 leading-relaxed italic">
              &ldquo;GaadiLelo delivers serious buyers ready to purchase. Instead of spending lakhs on cold digital leads, we pass our marketing savings directly to the group cohort as bulk discounts.&rdquo;
            </p>
            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-purple-100 text-purple-700 font-bold text-xs flex items-center justify-center">
                SM
              </div>
              <div>
                <h4 className="font-bold text-xs text-navy-900">Sanghi Brothers Sales Desk</h4>
                <p className="text-[10px] text-slate-400">Authorized Dealership, AB Road Indore</p>
              </div>
            </div>
          </div>
        </div>

      </section>


      {/* ========================================================= */}
      {/* 10. FAQ ACCORDION (CARDEKHO STYLE) */}
      {/* ========================================================= */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        
        <div className="text-center space-y-1">
          <h2 className="text-2xl font-bold text-navy-950">Frequently Asked Questions</h2>
          <p className="text-xs text-slate-500">Quick answers about vehicle group buying in Indore</p>
        </div>

        <div className="space-y-3">
          <div className="p-5 bg-white rounded-2xl border border-slate-200 shadow-sm">
            <h3 className="font-bold text-sm text-navy-950 mb-1">Is joining a buying group legally binding?</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              No. Joining a buying group is completely free and non-binding. It represents an expression of high purchase intent. You can leave the group at any time before bidding closes, and you retain full freedom to accept or decline the final dealer quotation.
            </p>
          </div>

          <div className="p-5 bg-white rounded-2xl border border-slate-200 shadow-sm">
            <h3 className="font-bold text-sm text-navy-950 mb-1">Can other members of my group see my personal contact details?</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Never. Buyer privacy is a foundational pillar of {brandName}. Other cohort members only see aggregated counts and vehicle variant preferences. Your contact details are only shared with a specific authorized dealership when you explicitly click &ldquo;Request Callback&rdquo;.
            </p>
          </div>

          <div className="p-5 bg-white rounded-2xl border border-slate-200 shadow-sm">
            <h3 className="font-bold text-sm text-navy-950 mb-1">How are quotations verified by the platform?</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              All participating dealerships are verified against state transport franchise registrations. Every submitted quote is reviewed by our operations team to confirm statutory MP RTO registration slabs, insurance formulas, and genuine group discounts before it is published to buyers.
            </p>
          </div>

          <div className="p-5 bg-white rounded-2xl border border-slate-200 shadow-sm">
            <h3 className="font-bold text-sm text-navy-950 mb-1">Where and how do I receive the vehicle?</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Delivery happens directly at the winning authorized OEM dealership in Indore (e.g. AB Road or Vijay Nagar showroom). You perform standard pre-delivery inspection (PDI), receive original invoices, and register the vehicle in your individual name.
            </p>
          </div>
        </div>

      </section>


      {/* ========================================================= */}
      {/* 11. ENTERPRISE FOOTER CALL-TO-ACTION */}
      {/* ========================================================= */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="p-8 sm:p-12 bg-gradient-to-r from-navy-950 via-slate-900 to-navy-950 rounded-2xl text-center text-white space-y-4 shadow-xl">
          <h3 className="text-2xl sm:text-3xl font-black">
            Ready to Pool Your Vehicle Demand in Indore?
          </h3>
          <p className="text-xs sm:text-sm text-slate-300 max-w-xl mx-auto leading-relaxed">
            Browse open cohorts or start a new group for your desired car, motorcycle, or commercial fleet in seconds. Free, non-binding, and 100% private.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
            <Link
              href="/groups/create"
              className="px-6 py-3 bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs uppercase tracking-wider rounded-xl shadow-lg shadow-brand-600/30 transition-all flex items-center gap-2"
            >
              <span>Start a Buying Group</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/vehicles"
              className="px-6 py-3 bg-white/10 hover:bg-white/15 text-white font-bold text-xs rounded-xl border border-white/20 transition-all"
            >
              <span>Explore Vehicle Catalog</span>
            </Link>
          </div>
        </div>
      </section>

    </div>
  );
}
