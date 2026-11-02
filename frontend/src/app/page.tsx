'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { 
  Car, Zap, Bike, Truck, Boxes, Search, ArrowRight, ShieldCheck, 
  TrendingUp, Users, CheckCircle2, ChevronRight, Sparkles, Building2, MapPin,
  Layers, Lock, BadgePercent, Clock, ArrowUpRight, Award, SlidersHorizontal,
  ThumbsUp, RefreshCw
} from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { VehicleCategory, BuyingGroup, VehicleModel } from '@/types';

export default function HomePage() {
  const [categories, setCategories] = useState<VehicleCategory[]>([]);
  const [popularGroups, setPopularGroups] = useState<BuyingGroup[]>([]);
  const [featuredModels, setFeaturedModels] = useState<VehicleModel[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCity, setSelectedCity] = useState('Indore');
  const [loading, setLoading] = useState(true);

  // 3D Tilt State for Hero Card
  const heroCardRef = useRef<HTMLDivElement>(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [isHoveringHero, setIsHoveringHero] = useState(false);

  // Interactive 3D Bulk Savings Visualizer State
  const [simulatorBudgetTier, setSimulatorBudgetTier] = useState<'budget' | 'mid' | 'premium' | 'commercial'>('mid');
  const [simulatorGroupSize, setSimulatorGroupSize] = useState<number>(5);

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
        setPopularGroups(groups?.slice(0, 4) || []);
        setFeaturedModels(models?.slice(0, 4) || []);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  // 3D Card Mouse Tilt Handler
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!heroCardRef.current) return;
    const rect = heroCardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    // Normalize tilt angles
    setMousePos({
      x: (y / rect.height) * -16, // rotateX
      y: (x / rect.width) * 16,   // rotateY
    });
  };

  const handleMouseEnter = () => setIsHoveringHero(true);
  const handleMouseLeave = () => {
    setIsHoveringHero(false);
    setMousePos({ x: 0, y: 0 });
  };

  const getCategoryIcon = (slug: string) => {
    switch (slug) {
      case 'electric-vehicle': return <Zap className="w-5 h-5 text-amber-500" />;
      case 'two-wheeler': return <Bike className="w-5 h-5 text-blue-500" />;
      case 'commercial-vehicle': return <Truck className="w-5 h-5 text-emerald-500" />;
      case 'three-wheeler': return <Boxes className="w-5 h-5 text-purple-500" />;
      default: return <Car className="w-5 h-5 text-brand-500" />;
    }
  };

  // Savings Calculator Computations
  const getSavingsEstimate = () => {
    let basePrice = 1200000;
    let baseDiscountPct = 0.04;
    let name = 'Tata Nexon / Hyundai Creta (Mid SUV)';

    if (simulatorBudgetTier === 'budget') {
      basePrice = 145000;
      baseDiscountPct = 0.05;
      name = 'Ather 450X / TVS Raider (Two-Wheeler)';
    } else if (simulatorBudgetTier === 'mid') {
      basePrice = 1250000;
      baseDiscountPct = 0.06;
      name = 'Tata Nexon Creative / Brezza ZXi (Compact SUV)';
    } else if (simulatorBudgetTier === 'premium') {
      basePrice = 2100000;
      baseDiscountPct = 0.075;
      name = 'Mahindra Scorpio-N / XUV700 (7-Seater SUV)';
    } else if (simulatorBudgetTier === 'commercial') {
      basePrice = 980000;
      baseDiscountPct = 0.08;
      name = 'Ashok Leyland Bada Dost / SCV Fleet';
    }

    // Bulk multipliers: 3 buyers = 1x, 5 buyers = 1.35x, 10 buyers = 1.75x, 15 buyers = 2.1x
    const sizeMultiplier = simulatorGroupSize === 3 ? 1.0 : simulatorGroupSize === 5 ? 1.35 : simulatorGroupSize === 10 ? 1.75 : 2.1;
    const individualDiscount = Math.round(basePrice * 0.015);
    const groupDiscountPerBuyer = Math.round(basePrice * baseDiscountPct * sizeMultiplier);
    const netAdditionalSaving = groupDiscountPerBuyer - individualDiscount;

    return {
      name,
      basePrice,
      individualDiscount,
      groupDiscountPerBuyer,
      netAdditionalSaving,
    };
  };

  const savings = getSavingsEstimate();

  return (
    <div className="space-y-24 pb-20 overflow-hidden">
      
      {/* ========================================================= */}
      {/* 1. MINIMAL HERO SECTION WITH 3D PERSPECTIVE SHOWCASE */}
      {/* ========================================================= */}
      <section className="relative pt-8 sm:pt-14 pb-12 sm:pb-20 border-b border-slate-200/60 bg-gradient-to-b from-white via-slate-50/50 to-white">
        
        {/* Subtle Ambient Background Gradients */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[650px] h-[350px] bg-gradient-to-tr from-brand-500/10 via-orange-400/5 to-blue-500/10 blur-3xl pointer-events-none rounded-full" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
            
            {/* Left Column: Minimal Value Proposition */}
            <div className="lg:col-span-7 space-y-6 text-center lg:text-left">
              
              {/* Pilot Status Badge */}
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900 text-white text-xs font-semibold shadow-md shadow-slate-900/10">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span>Indore Pilot Live</span>
                <span className="text-slate-400 font-normal">|</span>
                <span className="text-orange-300">Authorized Dealership Direct</span>
              </div>

              {/* Bold Minimal Headline */}
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black text-navy-950 tracking-tight leading-[1.12]">
                Your Next Gaadi. <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-600 via-orange-500 to-amber-500">
                  Your Best Deal.
                </span>
              </h1>

              {/* Concise Supporting Copy */}
              <p className="text-sm sm:text-base text-slate-600 leading-relaxed max-w-xl mx-auto lg:mx-0 font-normal">
                Don’t bargain alone. {brandName} pools verified buyers seeking the same vehicle in Indore. Authorized OEM dealerships compete with their best wholesale bulk quotations.
              </p>

              {/* Clean Search & City Selector Bar */}
              <div className="pt-2 max-w-xl mx-auto lg:mx-0">
                <div className="bg-white p-2 rounded-2xl shadow-xl shadow-slate-200/80 border border-slate-200/90 flex flex-col sm:flex-row items-center gap-2">
                  
                  {/* City Selector */}
                  <div className="flex items-center gap-2 px-3 py-2 bg-slate-50 rounded-xl w-full sm:w-auto text-xs font-bold text-slate-700 border border-slate-200/60">
                    <MapPin className="w-4 h-4 text-brand-500 flex-shrink-0" />
                    <select 
                      value={selectedCity} 
                      onChange={(e) => setSelectedCity(e.target.value)}
                      className="bg-transparent focus:outline-none cursor-pointer text-xs"
                    >
                      <option value="Indore">Indore, MP</option>
                      <option value="Bhopal">Bhopal, MP (Soon)</option>
                    </select>
                  </div>

                  {/* Search Input */}
                  <div className="flex items-center gap-2 px-3 py-2 flex-1 w-full">
                    <Search className="w-4 h-4 text-slate-400 flex-shrink-0" />
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="Search Nexon, Creta, Brezza, Ather..."
                      className="w-full text-xs sm:text-sm text-slate-800 placeholder-slate-400 bg-transparent focus:outline-none"
                    />
                  </div>

                  {/* Search Action */}
                  <Link
                    href={`/vehicles${searchQuery ? `?search=${encodeURIComponent(searchQuery)}` : ''}`}
                    className="w-full sm:w-auto px-5 py-2.5 bg-brand-500 hover:bg-brand-600 text-white font-bold text-xs rounded-xl shadow-md shadow-brand-500/25 transition-all flex items-center justify-center gap-1.5 flex-shrink-0"
                  >
                    <span>Find Deals</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>

              {/* Trust Badges */}
              <div className="pt-2 flex flex-wrap items-center justify-center lg:justify-start gap-5 sm:gap-8 text-xs text-slate-500 font-medium">
                <div className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                  <span>₹0 Joining Fee</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4 text-blue-500" />
                  <span>100% Non-Binding</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Lock className="w-3.5 h-3.5 text-brand-500" />
                  <span>Inviolable Buyer Privacy</span>
                </div>
              </div>

            </div>

            {/* Right Column: 3D Interactive Perspective Showcase Card */}
            <div className="lg:col-span-5 flex justify-center perspective-1200">
              
              <div 
                ref={heroCardRef}
                onMouseMove={handleMouseMove}
                onMouseEnter={handleMouseEnter}
                onMouseLeave={handleMouseLeave}
                style={{
                  transform: isHoveringHero 
                    ? `perspective(1200px) rotateX(${mousePos.x}deg) rotateY(${mousePos.y}deg) scale3d(1.02, 1.02, 1.02)`
                    : 'perspective(1200px) rotateX(4deg) rotateY(-8deg) scale3d(1, 1, 1)',
                  transition: isHoveringHero ? 'transform 0.1s ease-out' : 'transform 0.6s cubic-bezier(0.16, 1, 0.3, 1)'
                }}
                className="relative w-full max-w-md bg-white rounded-3xl p-5 sm:p-6 shadow-2xl shadow-slate-300/60 border border-slate-200/90 transform-style-3d cursor-pointer select-none group"
              >
                
                {/* 3D Floating Pill 1 (Top Left): Live Cohort Status */}
                <div 
                  className="absolute -top-3.5 -left-3.5 bg-navy-950/90 backdrop-blur-md text-white text-[11px] font-bold px-3.5 py-1.5 rounded-full shadow-lg border border-white/10 flex items-center gap-2 translate-z-30 animate-float-slow z-20"
                >
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                  <span>Indore Cohort #04 • 5 Buyers</span>
                </div>

                {/* 3D Floating Pill 2 (Top Right): Dealer Competition */}
                <div 
                  className="absolute -top-3 -right-3 bg-brand-500 text-white text-[11px] font-bold px-3 py-1.5 rounded-full shadow-lg border border-white/20 flex items-center gap-1.5 translate-z-20 animate-float-reverse z-20"
                >
                  <Building2 className="w-3.5 h-3.5 text-orange-200" />
                  <span>3 Dealers Bidding</span>
                </div>

                {/* Vehicle Showcase Image with 3D Depth */}
                <div className="relative rounded-2xl overflow-hidden bg-slate-100 aspect-[16/10] mb-4 border border-slate-200/60">
                  <img
                    src="https://images.unsplash.com/photo-1609521263047-f8f205293f24?w=800&auto=format&fit=crop&q=80"
                    alt="Tata Nexon Group Deal"
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 ease-out"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-navy-950/70 via-transparent to-transparent flex items-end p-4">
                    <div className="text-white space-y-0.5">
                      <span className="text-[10px] uppercase font-bold tracking-wider text-orange-300">Indore Hot Pick</span>
                      <h4 className="font-black text-base">Tata Nexon Creative Plus</h4>
                      <p className="text-xs text-slate-200">Ex-Showroom: ₹11,69,000</p>
                    </div>
                  </div>
                </div>

                {/* 3D Group Metrics Details */}
                <div className="space-y-3 pt-1">
                  
                  {/* Progress Line */}
                  <div className="space-y-1.5">
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-slate-500 font-medium">Cohort Progress</span>
                      <span className="font-bold text-navy-950">5 / 5 Buyers Joined (Target Reached)</span>
                    </div>
                    <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                      <div className="bg-gradient-to-r from-brand-500 to-emerald-500 h-full w-full rounded-full" />
                    </div>
                  </div>

                  {/* Savings Locked Card (3D Floating Pop) */}
                  <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-200 flex items-center justify-between translate-z-20">
                    <div>
                      <p className="text-[11px] font-bold text-emerald-800">Locked Group Discount</p>
                      <p className="text-xs text-emerald-700">Sanghi Brothers • Official Dealership</p>
                    </div>
                    <div className="text-right">
                      <span className="text-sm sm:text-base font-black text-emerald-700">₹80,000 Saved</span>
                      <p className="text-[10px] text-emerald-600 font-medium">+ Free Ceramic Coating</p>
                    </div>
                  </div>

                  {/* Fast Action CTA */}
                  <Link
                    href="/groups"
                    className="w-full py-2.5 bg-navy-950 hover:bg-slate-900 text-white font-bold text-xs rounded-xl transition-all flex items-center justify-center gap-1.5 shadow-md"
                  >
                    <span>View Competing Dealer Quotations</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>

                </div>

              </div>

            </div>

          </div>

        </div>
      </section>


      {/* ========================================================= */}
      {/* 2. SERVICES WE PROVIDE (MINIMAL 4-PILLAR SERVICE ARCHITECTURE) */}
      {/* ========================================================= */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="text-center max-w-2xl mx-auto mb-12 space-y-2">
          <div className="inline-flex items-center gap-1.5 text-xs font-bold text-brand-600 uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Our Core Platform Services</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-black text-navy-950">
            How GaadiLelo Works For You
          </h2>
          <p className="text-xs sm:text-sm text-slate-500">
            We transform individual buyers into organized volume cohorts that dealerships compete to serve.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          
          {/* Service 1 */}
          <div className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-sm hover:shadow-md hover:border-brand-200 transition-all space-y-4 group">
            <div className="w-12 h-12 rounded-2xl bg-orange-50 group-hover:bg-brand-500 text-brand-600 group-hover:text-white flex items-center justify-center transition-colors">
              <Users className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-base text-navy-950">1. Demand Aggregation</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              We aggregate individual customers looking for the same vehicle variant and timeline into structured local cohorts in Indore.
            </p>
            <div className="pt-2 text-xs font-semibold text-brand-600 flex items-center gap-1">
              <span>Pooled Leverage</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </div>
          </div>

          {/* Service 2 */}
          <div className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-sm hover:shadow-md hover:border-blue-200 transition-all space-y-4 group">
            <div className="w-12 h-12 rounded-2xl bg-blue-50 group-hover:bg-blue-600 text-blue-600 group-hover:text-white flex items-center justify-center transition-colors">
              <Building2 className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-base text-navy-950">2. Dealership Bidding</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Verified OEM authorized dealerships receive an exclusive invitation to submit their sharpest wholesale quotations for the group.
            </p>
            <div className="pt-2 text-xs font-semibold text-blue-600 flex items-center gap-1">
              <span>Reverse Auction</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </div>
          </div>

          {/* Service 3 */}
          <div className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-sm hover:shadow-md hover:border-purple-200 transition-all space-y-4 group">
            <div className="w-12 h-12 rounded-2xl bg-purple-50 group-hover:bg-purple-600 text-purple-600 group-hover:text-white flex items-center justify-center transition-colors">
              <BadgePercent className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-base text-navy-950">3. Line-Item Transparency</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Every quote is audited line-by-line: statutory RTO tax, insurance, TCS, OEM subsidies, and genuine cash discounts without hidden charges.
            </p>
            <div className="pt-2 text-xs font-semibold text-purple-600 flex items-center gap-1">
              <span>Zero Markups</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </div>
          </div>

          {/* Service 4 */}
          <div className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-sm hover:shadow-md hover:border-emerald-200 transition-all space-y-4 group">
            <div className="w-12 h-12 rounded-2xl bg-emerald-50 group-hover:bg-emerald-600 text-emerald-600 group-hover:text-white flex items-center justify-center transition-colors">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-base text-navy-950">4. Direct Showroom Delivery</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              You execute paperwork, financing, and standard vehicle PDI inspection directly at the official dealership showroom in Indore.
            </p>
            <div className="pt-2 text-xs font-semibold text-emerald-600 flex items-center gap-1">
              <span>Official Warranty</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </div>
          </div>

        </div>

      </section>


      {/* ========================================================= */}
      {/* 3. PRODUCT CATEGORIES (MINIMAL VEHICLE DIRECTORY) */}
      {/* ========================================================= */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-8 gap-4">
          <div>
            <span className="text-xs font-bold text-brand-600 uppercase tracking-wider">Product Catalog</span>
            <h2 className="text-2xl sm:text-3xl font-black text-navy-950 mt-1">Vehicle Range Covered</h2>
            <p className="text-xs text-slate-500 mt-1">Group-buying power across every powertrain and vehicle segment in Indore.</p>
          </div>
          <Link 
            href="/vehicles"
            className="text-xs font-bold text-brand-600 hover:text-brand-700 flex items-center gap-1 self-start sm:self-auto"
          >
            <span>Explore All Vehicles</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          {categories.map((cat) => (
            <Link
              key={cat.id}
              href={`/vehicles?category=${cat.slug}`}
              className="p-5 bg-white rounded-2xl border border-slate-200/80 hover:border-brand-300 hover:shadow-lg hover:shadow-brand-500/5 transition-all group text-center flex flex-col items-center justify-center"
            >
              <div className="w-12 h-12 rounded-xl bg-slate-50 group-hover:bg-orange-50 flex items-center justify-center transition-colors mb-3">
                {getCategoryIcon(cat.slug)}
              </div>
              <h3 className="font-bold text-sm text-navy-950 group-hover:text-brand-600 transition-colors">
                {cat.name}
              </h3>
              <p className="text-[11px] text-slate-400 mt-1 line-clamp-1">
                {cat.description}
              </p>
            </Link>
          ))}
        </div>

      </section>


      {/* ========================================================= */}
      {/* 4. INTERACTIVE 3D BULK SAVINGS ESTIMATOR */}
      {/* ========================================================= */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="bg-navy-950 rounded-3xl p-6 sm:p-10 text-white relative overflow-hidden shadow-2xl">
          
          {/* Subtle Ambient Glowing Spheres */}
          <div className="absolute top-0 right-0 w-96 h-96 bg-brand-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute bottom-0 left-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />

          <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            
            {/* Left Column: Interactive Controls */}
            <div className="lg:col-span-6 space-y-6">
              
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-brand-500/20 text-orange-300 text-xs font-semibold border border-brand-500/30">
                <SlidersHorizontal className="w-3.5 h-3.5" />
                <span>Interactive Bulk Savings Calculator</span>
              </div>

              <div>
                <h3 className="text-2xl sm:text-3xl font-black tracking-tight text-white">
                  See How Much Your Cohort Saves
                </h3>
                <p className="text-xs sm:text-sm text-slate-400 mt-2 leading-relaxed">
                  Bulk fleet discounts scale with group size. Choose a vehicle segment and group size to estimate real-world dealership discounts in Indore.
                </p>
              </div>

              {/* Segment Selector */}
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                  Select Vehicle Segment
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  <button
                    type="button"
                    onClick={() => setSimulatorBudgetTier('budget')}
                    className={`px-3 py-2 rounded-xl text-xs font-bold transition-all ${
                      simulatorBudgetTier === 'budget' 
                        ? 'bg-brand-500 text-white shadow-md' 
                        : 'bg-navy-900 text-slate-400 hover:text-white border border-navy-800'
                    }`}
                  >
                    2-Wheeler / EV
                  </button>
                  <button
                    type="button"
                    onClick={() => setSimulatorBudgetTier('mid')}
                    className={`px-3 py-2 rounded-xl text-xs font-bold transition-all ${
                      simulatorBudgetTier === 'mid' 
                        ? 'bg-brand-500 text-white shadow-md' 
                        : 'bg-navy-900 text-slate-400 hover:text-white border border-navy-800'
                    }`}
                  >
                    Compact SUV
                  </button>
                  <button
                    type="button"
                    onClick={() => setSimulatorBudgetTier('premium')}
                    className={`px-3 py-2 rounded-xl text-xs font-bold transition-all ${
                      simulatorBudgetTier === 'premium' 
                        ? 'bg-brand-500 text-white shadow-md' 
                        : 'bg-navy-900 text-slate-400 hover:text-white border border-navy-800'
                    }`}
                  >
                    Mid / 7-Str SUV
                  </button>
                  <button
                    type="button"
                    onClick={() => setSimulatorBudgetTier('commercial')}
                    className={`px-3 py-2 rounded-xl text-xs font-bold transition-all ${
                      simulatorBudgetTier === 'commercial' 
                        ? 'bg-brand-500 text-white shadow-md' 
                        : 'bg-navy-900 text-slate-400 hover:text-white border border-navy-800'
                    }`}
                  >
                    Commercial SCV
                  </button>
                </div>
              </div>

              {/* Group Size Selector */}
              <div className="space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <label className="font-bold text-slate-300 uppercase tracking-wider">
                    Cohort Size (Buyers)
                  </label>
                  <span className="font-mono text-orange-400 font-bold">
                    {simulatorGroupSize} Buyers Pooled
                  </span>
                </div>
                <div className="grid grid-cols-4 gap-2">
                  {[3, 5, 10, 15].map((size) => (
                    <button
                      key={size}
                      type="button"
                      onClick={() => setSimulatorGroupSize(size)}
                      className={`py-2 rounded-xl text-xs font-bold transition-all ${
                        simulatorGroupSize === size 
                          ? 'bg-white text-navy-950 shadow-md font-black' 
                          : 'bg-navy-900 text-slate-400 hover:text-white border border-navy-800'
                      }`}
                    >
                      {size} Buyers
                    </button>
                  ))}
                </div>
              </div>

              <div className="pt-2">
                <Link
                  href="/groups/create"
                  className="inline-flex items-center gap-2 px-6 py-3 bg-brand-500 hover:bg-brand-600 text-white font-bold text-xs rounded-xl shadow-lg shadow-brand-500/25 transition-all"
                >
                  <span>Start Group with this Tier</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>

            </div>

            {/* Right Column: 3D Perspective Output Card */}
            <div className="lg:col-span-6 flex justify-center">
              
              <div className="w-full max-w-md bg-navy-900/90 backdrop-blur-md rounded-3xl p-6 border border-navy-700/80 shadow-2xl space-y-6">
                
                <div className="flex justify-between items-center border-b border-navy-800 pb-3">
                  <span className="text-xs text-slate-400 font-medium">{savings.name}</span>
                  <span className="text-[10px] uppercase font-bold bg-emerald-500/20 text-emerald-300 px-2.5 py-0.5 rounded-full border border-emerald-500/30">
                    Verified Estimate
                  </span>
                </div>

                {/* Side-by-side comparison box */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-navy-950 p-4 rounded-2xl border border-navy-800">
                    <span className="text-[11px] text-slate-400 block mb-1">Solo Buyer Walk-in</span>
                    <span className="text-lg font-bold text-slate-300 line-through">
                      ₹{savings.individualDiscount.toLocaleString('en-IN')}
                    </span>
                    <p className="text-[10px] text-slate-500 mt-1">Average retail dealer promo</p>
                  </div>

                  <div className="bg-emerald-950/40 p-4 rounded-2xl border border-emerald-500/30">
                    <span className="text-[11px] text-emerald-400 font-bold block mb-1">GaadiLelo Group</span>
                    <span className="text-xl sm:text-2xl font-black text-emerald-300">
                      ₹{savings.groupDiscountPerBuyer.toLocaleString('en-IN')}
                    </span>
                    <p className="text-[10px] text-emerald-400/80 mt-1">Direct bulk fleet margin</p>
                  </div>
                </div>

                {/* Total Cohort Net Advantage */}
                <div className="p-4 rounded-2xl bg-gradient-to-r from-brand-500/20 to-orange-500/20 border border-brand-500/30 flex items-center justify-between">
                  <div>
                    <span className="text-xs text-orange-200 font-bold block">Extra Net Savings Per Buyer</span>
                    <span className="text-[11px] text-slate-400">Beyond solitary showroom bargaining</span>
                  </div>
                  <span className="text-xl font-black text-orange-300">
                    +₹{savings.netAdditionalSaving.toLocaleString('en-IN')}
                  </span>
                </div>

                <div className="text-[11px] text-slate-400 flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  <span>Includes zero handling charges + priority Indore showroom delivery slot.</span>
                </div>

              </div>

            </div>

          </div>

        </div>

      </section>


      {/* ========================================================= */}
      {/* 5. ADVERTISED FEATURES (MINIMAL & TRANSPARENT CUSTOMER PILLARS) */}
      {/* ========================================================= */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="text-center max-w-2xl mx-auto mb-12 space-y-2">
          <div className="inline-flex items-center gap-1.5 text-xs font-bold text-brand-600 uppercase tracking-wider">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Buyer Protection Features</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-black text-navy-950">
            Engineered For Buyer Safety & Transparency
          </h2>
          <p className="text-xs sm:text-sm text-slate-500">
            We eliminated the opacity, spam calls, and arbitrary handling charges of traditional car retail.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          
          {/* Feature 1 */}
          <div className="p-6 bg-white rounded-3xl border border-slate-200/80 shadow-sm space-y-3">
            <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
              <Lock className="w-5 h-5" />
            </div>
            <h4 className="font-bold text-sm text-navy-950">100% Buyer Privacy Shield</h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              Other group members never see your phone number or email. Dealerships only receive your contact info if you explicitly request a callback.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="p-6 bg-white rounded-3xl border border-slate-200/80 shadow-sm space-y-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <h4 className="font-bold text-sm text-navy-950">Zero-Commitment Intent</h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              Joining a group costs ₹0 and is non-binding. If you don’t love the dealership’s final quotation, you can walk away with zero penalty.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="p-6 bg-white rounded-3xl border border-slate-200/80 shadow-sm space-y-3">
            <div className="w-10 h-10 rounded-xl bg-orange-50 text-brand-600 flex items-center justify-center">
              <BadgePercent className="w-5 h-5" />
            </div>
            <h4 className="font-bold text-sm text-navy-950">Zero Handling Fees</h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              Our quotation audit engine automatically flags and strips illegal dealership &ldquo;logistics charges&rdquo; and arbitrary accessory markups.
            </p>
          </div>

          {/* Feature 4 */}
          <div className="p-6 bg-white rounded-3xl border border-slate-200/80 shadow-sm space-y-3">
            <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
              <Layers className="w-5 h-5" />
            </div>
            <h4 className="font-bold text-sm text-navy-950">Side-by-Side Comparison</h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              Compare competing dealerships with itemized tables: ex-showroom, state RTO, zero-dep insurance, TCS, corporate discounts, and perks.
            </p>
          </div>

        </div>

      </section>


      {/* ========================================================= */}
      {/* 6. POPULAR LIVE GROUPS IN INDORE PILOT */}
      {/* ========================================================= */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-8 gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 text-xs font-bold text-brand-600 uppercase tracking-wider">
              <span className="w-2 h-2 rounded-full bg-brand-500 animate-ping" />
              <span>Live Indore Buying Groups</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-navy-950 mt-1">Active Buyer Cohorts</h2>
            <p className="text-xs text-slate-500 mt-1">Join an open cohort now to lock in dealer bidding when target count is reached.</p>
          </div>
          <Link 
            href="/groups"
            className="text-xs font-bold text-brand-600 hover:text-brand-700 flex items-center gap-1 self-start sm:self-auto"
          >
            <span>View All Groups</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {loading ? (
          <div className="p-12 text-center text-xs text-slate-400">Loading active groups...</div>
        ) : popularGroups.length === 0 ? (
          <div className="p-8 bg-white rounded-2xl border border-slate-200 text-center text-xs text-slate-500">
            No active groups yet in Indore. Start the first group for your target vehicle!
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {popularGroups.map((group) => {
              const progressPct = Math.min(100, Math.round((group.current_members_count / group.target_members) * 100));

              return (
                <div
                  key={group.id}
                  className="bg-white rounded-3xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between"
                >
                  <div className="relative h-44 bg-slate-100 overflow-hidden">
                    <img
                      src={group.vehicle_image_url || 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=600'}
                      alt={group.vehicle_name || 'Vehicle'}
                      className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                    />
                    <div className="absolute top-3 left-3">
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
                    <div className="absolute bottom-2 right-2 bg-navy-950/80 backdrop-blur-sm text-white px-2 py-0.5 rounded text-[10px] font-mono">
                      {group.group_code}
                    </div>
                  </div>

                  <div className="p-5 flex-1 flex flex-col justify-between space-y-4">
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
                        <span className="text-slate-500 font-medium">Cohort Progress</span>
                        <span className="font-bold text-navy-900">
                          {group.current_members_count} / {group.target_members} Buyers
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
                        ) : null}
                      </div>
                    </div>

                    {/* Action */}
                    <Link
                      href={`/groups/${group.id}`}
                      className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs rounded-xl transition-colors flex items-center justify-center gap-1.5"
                    >
                      {group.status === 'OFFERS_AVAILABLE' ? 'Compare Offers' : 'View Cohort'}
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
      {/* 7. PILOT TESTIMONIALS (CLEARLY LABELED DEMO CONTENT) */}
      {/* ========================================================= */}
      <section className="bg-slate-100/70 py-16 border-y border-slate-200/70">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="text-center max-w-2xl mx-auto mb-10 space-y-1">
            <span className="text-[10px] font-bold uppercase tracking-wider bg-slate-200 text-slate-700 px-3 py-1 rounded-full border border-slate-300">
              Indore Pilot Feedback (Demo Representative Content)
            </span>
            <h2 className="text-2xl font-bold text-navy-950 pt-2">What Early Buyers & Dealerships Say</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-sm flex flex-col justify-between">
              <p className="text-xs text-slate-600 italic leading-relaxed">
                &ldquo;Four of us in Indore were looking to buy the Tata Nexon. We pooled our group on GaadiLelo, and Sanghi Motors gave us an ₹80,000 on-road discount each plus complimentary mats and coating!&rdquo;
              </p>
              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-orange-100 text-brand-600 font-bold text-xs flex items-center justify-center">
                  RS
                </div>
                <div>
                  <h4 className="font-bold text-xs text-navy-900">Rahul Sharma</h4>
                  <p className="text-[10px] text-slate-400">Vijay Nagar, Indore • Nexon Cohort</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-sm flex flex-col justify-between">
              <p className="text-xs text-slate-600 italic leading-relaxed">
                &ldquo;Negotiating battery addons and charger installation alone was confusing. Through GaadiLelo, our 6-member Ather 450X cohort received clean quotations directly from authorized dealers.&rdquo;
              </p>
              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 font-bold text-xs flex items-center justify-center">
                  PV
                </div>
                <div>
                  <h4 className="font-bold text-xs text-navy-900">Priya Verma</h4>
                  <p className="text-[10px] text-slate-400">Palasia, Indore • Ather EV Cohort</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-sm flex flex-col justify-between">
              <p className="text-xs text-slate-600 italic leading-relaxed">
                &ldquo;GaadiLelo delivers serious buyers ready to purchase. Instead of spending lakhs on cold digital leads, we pass our marketing savings directly to the group cohort as bulk discounts.&rdquo;
              </p>
              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-purple-100 text-purple-600 font-bold text-xs flex items-center justify-center">
                  SM
                </div>
                <div>
                  <h4 className="font-bold text-xs text-navy-900">Sanghi Brothers Sales Desk</h4>
                  <p className="text-[10px] text-slate-400">Authorized Dealership, AB Road Indore</p>
                </div>
              </div>
            </div>
          </div>

        </div>
      </section>


      {/* ========================================================= */}
      {/* 8. FAQ & FINAL CALL TO ACTION */}
      {/* ========================================================= */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        
        <div className="text-center space-y-1">
          <h2 className="text-2xl font-bold text-navy-950">Frequently Asked Questions</h2>
          <p className="text-xs text-slate-500">Quick answers about vehicle group buying</p>
        </div>

        <div className="space-y-4">
          <div className="p-5 bg-white rounded-2xl border border-slate-200/80 shadow-sm">
            <h3 className="font-bold text-sm text-navy-950 mb-1">Is joining a buying group legally binding?</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              No. Joining a buying group is completely free and non-binding. It represents an expression of high purchase intent. You can leave the group at any time before bidding closes, and you retain full freedom to accept or decline the final dealer quotation.
            </p>
          </div>

          <div className="p-5 bg-white rounded-2xl border border-slate-200/80 shadow-sm">
            <h3 className="font-bold text-sm text-navy-950 mb-1">Can other members of my group see my personal contact details?</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Never. Buyer privacy is a foundational pillar of {brandName}. Other cohort members only see aggregated counts and vehicle variant preferences. Your contact details are only shared with a specific authorized dealership when you explicitly click &ldquo;Request Callback&rdquo;.
            </p>
          </div>

          <div className="p-5 bg-white rounded-2xl border border-slate-200/80 shadow-sm">
            <h3 className="font-bold text-sm text-navy-950 mb-1">How are quotations verified by the platform?</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              All participating dealerships are verified against state transport franchise registrations. Every submitted quote is reviewed by our operations team to confirm statutory MP RTO registration slabs, insurance formulas, and genuine group discounts before it is published to buyers.
            </p>
          </div>

          <div className="p-5 bg-white rounded-2xl border border-slate-200/80 shadow-sm">
            <h3 className="font-bold text-sm text-navy-950 mb-1">Where and how do I receive the vehicle?</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Delivery happens directly at the winning authorized OEM dealership in Indore (e.g. AB Road or Vijay Nagar showroom). You perform standard pre-delivery inspection (PDI), receive original invoices, and register the vehicle in your individual name.
            </p>
          </div>
        </div>

        {/* Final Minimal CTA Banner */}
        <div className="p-8 sm:p-10 bg-gradient-to-r from-navy-950 via-slate-900 to-navy-900 rounded-3xl text-center text-white space-y-5 shadow-xl">
          <h3 className="text-2xl sm:text-3xl font-black">Ready to Pool Your Vehicle Demand in Indore?</h3>
          <p className="text-xs sm:text-sm text-slate-300 max-w-lg mx-auto">
            Browse open cohorts or start a new group for your desired car, motorcycle, or commercial fleet in seconds.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
            <Link
              href="/groups/create"
              className="px-6 py-3 bg-brand-500 hover:bg-brand-600 text-white font-bold text-xs rounded-xl shadow-lg shadow-brand-500/25 transition-all flex items-center gap-1.5"
            >
              <span>Start a Buying Group</span>
              <ArrowRight className="w-3.5 h-3.5" />
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
