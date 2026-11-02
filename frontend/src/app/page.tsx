'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  Car, Zap, Bike, Truck, Boxes, Search, ArrowRight, ShieldCheck, 
  TrendingUp, Users, CheckCircle2, ChevronRight, HelpCircle, Sparkles, Building2, MapPin
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

  const getCategoryIcon = (slug: string) => {
    switch (slug) {
      case 'electric-vehicle': return <Zap className="w-5 h-5 text-amber-500" />;
      case 'two-wheeler': return <Bike className="w-5 h-5 text-blue-500" />;
      case 'commercial-vehicle': return <Truck className="w-5 h-5 text-emerald-500" />;
      case 'three-wheeler': return <Boxes className="w-5 h-5 text-purple-500" />;
      default: return <Car className="w-5 h-5 text-brand-500" />;
    }
  };

  return (
    <div className="space-y-16 pb-16">
      
      {/* 1. HERO SECTION */}
      <section className="relative overflow-hidden bg-gradient-to-b from-white via-orange-50/20 to-slate-50 pt-12 pb-20 border-b border-slate-200/70">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="text-center max-w-3xl mx-auto space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-orange-100/80 text-brand-800 text-xs font-semibold border border-orange-200">
              <Sparkles className="w-3.5 h-3.5 text-brand-600" />
              <span>Pilot Live in Indore, MP • 100% Free & Transparent</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black text-navy-950 tracking-tight leading-tight">
              Your Next Gaadi. <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-600 to-orange-500">
                Your Best Deal.
              </span>
            </h1>

            <p className="text-base sm:text-lg text-slate-600 leading-relaxed font-normal max-w-2xl mx-auto">
              Join forces with other buyers. Let dealerships compete. Get better vehicle deals.
              Group-buying power for cars, electric vehicles, two-wheelers, and commercial fleets.
            </p>

            {/* Live Search & City Filter Bar */}
            <div className="pt-2">
              <div className="bg-white p-2.5 rounded-2xl shadow-xl shadow-slate-200/60 border border-slate-200 flex flex-col sm:flex-row items-center gap-2 max-w-2xl mx-auto">
                
                {/* City Picker */}
                <div className="flex items-center gap-2 px-3 py-2 bg-slate-50 rounded-xl w-full sm:w-auto text-xs font-semibold text-slate-700 border border-slate-200/80">
                  <MapPin className="w-4 h-4 text-brand-500" />
                  <select 
                    value={selectedCity} 
                    onChange={(e) => setSelectedCity(e.target.value)}
                    className="bg-transparent focus:outline-none cursor-pointer"
                  >
                    <option value="Indore">Indore, MP</option>
                    <option value="Bhopal">Bhopal, MP (Upcoming)</option>
                  </select>
                </div>

                {/* Search Input */}
                <div className="flex items-center gap-2 px-3 py-2 flex-1 w-full">
                  <Search className="w-4 h-4 text-slate-400" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search vehicle model (e.g. Nexon, Brezza, Ather, Scorpio)..."
                    className="w-full text-xs sm:text-sm text-slate-800 placeholder-slate-400 bg-transparent focus:outline-none"
                  />
                </div>

                {/* Search CTA */}
                <Link
                  href={`/vehicles${searchQuery ? `?search=${encodeURIComponent(searchQuery)}` : ''}`}
                  className="w-full sm:w-auto px-6 py-2.5 bg-brand-500 hover:bg-brand-600 text-white font-semibold text-xs rounded-xl shadow-md shadow-brand-500/20 transition-all flex items-center justify-center gap-1.5"
                >
                  Find Deals
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>

            {/* Quick Metrics */}
            <div className="pt-4 flex flex-wrap items-center justify-center gap-6 sm:gap-12 text-xs text-slate-500 font-medium">
              <div className="flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-emerald-500" />
                <span>Verified OEM Dealerships</span>
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-brand-500" />
                <span>Non-Binding Intent Only</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Users className="w-4 h-4 text-blue-500" />
                <span>Strict Buyer Privacy</span>
              </div>
            </div>

          </div>

        </div>
      </section>


      {/* 2. BROWSE BY CATEGORY */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl sm:text-2xl font-bold text-navy-950">Explore Vehicle Categories</h2>
            <p className="text-xs text-slate-500 mt-0.5">Vehicle-agnostic group buying engine across all powertrains</p>
          </div>
          <Link href="/vehicles" className="text-xs font-semibold text-brand-600 hover:text-brand-700 flex items-center gap-1">
            View All <ChevronRight className="w-3.5 h-3.5" />
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
              <h3 className="font-bold text-sm text-navy-900 group-hover:text-brand-600 transition-colors">
                {cat.name}
              </h3>
              <p className="text-[11px] text-slate-400 mt-1 line-clamp-1">
                {cat.description}
              </p>
            </Link>
          ))}
        </div>
      </section>


      {/* 3. POPULAR BUYING GROUPS IN INDORE */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <div className="inline-flex items-center gap-1 text-[11px] font-bold text-brand-600 uppercase tracking-wider mb-1">
              <span className="w-2 h-2 rounded-full bg-brand-500 animate-ping inline-block mr-1" />
              Live Indore Cohorts
            </div>
            <h2 className="text-xl sm:text-2xl font-bold text-navy-950">Popular Buying Groups</h2>
          </div>
          <Link href="/groups" className="text-xs font-semibold text-brand-600 hover:text-brand-700 flex items-center gap-1">
            Explore All Groups <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {loading ? (
          <div className="p-12 text-center text-sm text-slate-400">Loading active groups...</div>
        ) : popularGroups.length === 0 ? (
          <div className="p-8 bg-white rounded-2xl border border-slate-200 text-center text-sm text-slate-500">
            No active groups in this category yet. Be the first to start one!
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {popularGroups.map((group) => {
              const progressPct = Math.min(100, Math.round((group.current_members_count / group.target_members) * 100));

              return (
                <div
                  key={group.id}
                  className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between"
                >
                  <div className="relative h-44 bg-slate-100 overflow-hidden">
                    <img
                      src={group.vehicle_image_url || 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=600'}
                      alt={group.vehicle_name || 'Vehicle'}
                      className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                    />
                    <div className="absolute top-3 left-3">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
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

                  <div className="p-4 flex-1 flex flex-col justify-between space-y-4">
                    <div>
                      <div className="text-[11px] font-semibold text-slate-400">
                        {group.brand_name} • {group.city_name}
                      </div>
                      <h3 className="font-bold text-sm text-navy-950 line-clamp-1">
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
                      <div className="flex justify-between text-[10px] text-slate-400">
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
                      className="w-full py-2 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-xl transition-colors flex items-center justify-center gap-1.5"
                    >
                      {group.status === 'OFFERS_AVAILABLE' ? 'Compare Offers' : 'View Group'}
                      <ChevronRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>


      {/* 4. HOW IT WORKS */}
      <section className="bg-navy-900 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold tracking-tight">How Group-Buying Works</h2>
            <p className="text-xs sm:text-sm text-slate-400 mt-2">
              Transforming fragmented single-buyer struggles into organized, high-leverage buyer cohorts.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="bg-navy-800/60 p-6 rounded-2xl border border-navy-700/60 relative">
              <div className="w-8 h-8 rounded-lg bg-brand-500 text-white font-bold text-xs flex items-center justify-center mb-4">
                01
              </div>
              <h3 className="font-bold text-base text-white mb-2">Pool Demand</h3>
              <p className="text-xs text-slate-300 leading-relaxed">
                Join or initiate a local Indore cohort for your target vehicle variant, powertrain, and delivery timeline.
              </p>
            </div>

            <div className="bg-navy-800/60 p-6 rounded-2xl border border-navy-700/60 relative">
              <div className="w-8 h-8 rounded-lg bg-blue-500 text-white font-bold text-xs flex items-center justify-center mb-4">
                02
              </div>
              <h3 className="font-bold text-base text-white mb-2">Dealerships Compete</h3>
              <p className="text-xs text-slate-300 leading-relaxed">
                Once milestone is reached, verified OEM franchised dealerships submit their sharpest transparent quotations.
              </p>
            </div>

            <div className="bg-navy-800/60 p-6 rounded-2xl border border-navy-700/60 relative">
              <div className="w-8 h-8 rounded-lg bg-purple-500 text-white font-bold text-xs flex items-center justify-center mb-4">
                03
              </div>
              <h3 className="font-bold text-base text-white mb-2">Compare & Choose</h3>
              <p className="text-xs text-slate-300 leading-relaxed">
                Inspect transparent on-road breakdowns side-by-side with statutory taxes, real discounts, and verified perks.
              </p>
            </div>

            <div className="bg-navy-800/60 p-6 rounded-2xl border border-navy-700/60 relative">
              <div className="w-8 h-8 rounded-lg bg-emerald-500 text-white font-bold text-xs flex items-center justify-center mb-4">
                04
              </div>
              <h3 className="font-bold text-base text-white mb-2">Direct Delivery</h3>
              <p className="text-xs text-slate-300 leading-relaxed">
                Connect directly with the winning dealership for paperwork, finance, and physical vehicle delivery.
              </p>
            </div>
          </div>
        </div>
      </section>


      {/* 5. WHY GAADILELO & BUYER BENEFITS */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-6">
            <div className="inline-flex items-center gap-1.5 text-xs font-bold text-brand-600 uppercase tracking-wider">
              <TrendingUp className="w-4 h-4" />
              The Group Buying Advantage
            </div>
            <h2 className="text-3xl font-black text-navy-950 tracking-tight leading-tight">
              Why Bargain Alone When <br />
              You Can Win Together?
            </h2>
            <p className="text-sm text-slate-600 leading-relaxed">
              In traditional automotive retail, solitary buyers bear dealership marketing overheads, arbitrary accessory packages, and opaque handling charges. {brandName} gives individual buyers the corporate bulk-fleet pricing power previously reserved only for rental companies.
            </p>

            <div className="space-y-4 pt-2">
              <div className="flex items-start gap-3">
                <div className="p-2 rounded-xl bg-orange-100 text-brand-600 mt-0.5">
                  <CheckCircle2 className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="font-bold text-sm text-navy-900">Zero Mandatory Dealer Handling Fees</h4>
                  <p className="text-xs text-slate-500 mt-0.5">Strict platform audit eliminates illegal handling/logistics markups.</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="p-2 rounded-xl bg-blue-100 text-blue-600 mt-0.5">
                  <ShieldCheck className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="font-bold text-sm text-navy-900">Buyer Privacy Protected</h4>
                  <p className="text-xs text-slate-500 mt-0.5">Other group members never see your phone number, email, or personal details.</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="p-2 rounded-xl bg-emerald-100 text-emerald-600 mt-0.5">
                  <Users className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="font-bold text-sm text-navy-900">Non-Binding Flexibility</h4>
                  <p className="text-xs text-slate-500 mt-0.5">Joining a cohort costs ₹0 and involves no binding purchase commitment.</p>
                </div>
              </div>
            </div>

            <div className="pt-2">
              <Link
                href="/groups/create"
                className="inline-flex items-center gap-2 px-6 py-3 bg-brand-500 hover:bg-brand-600 text-white font-semibold text-xs rounded-xl shadow-md shadow-brand-500/20 transition-all"
              >
                Start a New Buying Group in Indore
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>

          {/* Side Comparison Graphic */}
          <div className="bg-gradient-to-tr from-slate-100 to-orange-50 p-6 rounded-3xl border border-slate-200">
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-4">
              <div className="flex justify-between items-center pb-3 border-b border-slate-100">
                <span className="font-bold text-sm text-navy-900">Individual vs Group Buying</span>
                <span className="text-[10px] font-bold uppercase bg-brand-100 text-brand-700 px-2 py-0.5 rounded">
                  Indore Benchmark
                </span>
              </div>

              <div className="space-y-3 text-xs">
                <div className="p-3 bg-red-50/60 rounded-xl border border-red-100">
                  <p className="font-bold text-red-900">Traditional Solo Buyer Walk-In</p>
                  <p className="text-red-700 mt-1">Average Discount: ₹5,000 - ₹15,000</p>
                  <p className="text-slate-500 text-[11px] mt-0.5">Dealership knows you cannot easily compare competing dealership quotes in real time.</p>
                </div>

                <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-200">
                  <div className="flex justify-between items-center">
                    <p className="font-bold text-emerald-900">GaadiLelo Group Cohort (5+ Buyers)</p>
                    <span className="font-black text-emerald-700 text-sm">Save ₹50,000 - ₹1,20,000</span>
                  </div>
                  <p className="text-emerald-800 mt-1">Bulk volume OEM bonus + competitive dealership margin discount.</p>
                  <p className="text-slate-500 text-[11px] mt-0.5">Complimentary accessory packs and verified delivery priority.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>


      {/* 6. TESTIMONIALS (Clearly labeled Demo Content) */}
      <section className="bg-slate-100/70 py-16 border-y border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-10">
            <span className="text-[10px] font-bold uppercase tracking-wider bg-slate-200 text-slate-700 px-2.5 py-1 rounded-full border border-slate-300">
              Pilot User Stories (Demo Representative Content)
            </span>
            <h2 className="text-2xl font-bold text-navy-950 mt-3">What Early Pilot Buyers & Dealers Say</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
              <p className="text-xs text-slate-600 italic leading-relaxed">
                &ldquo;Four of us in Indore were planning to buy the Tata Nexon. We pooled our group together on GaadiLelo, and Sanghi Motors offered us an ₹80,000 on-road discount each plus complimentary mats and coating!&rdquo;
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

            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
              <p className="text-xs text-slate-600 italic leading-relaxed">
                &ldquo;As an EV commuter, negotiating battery pack addons was overwhelming. Through GaadiLelo, our 6-member Ather cohort got transparent quotes directly from certified dealers without middlemen.&rdquo;
              </p>
              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 font-bold text-xs flex items-center justify-center">
                  PV
                </div>
                <div>
                  <h4 className="font-bold text-xs text-navy-900">Priya Verma</h4>
                  <p className="text-[10px] text-slate-400">Palasia, Indore • Ather 450X Cohort</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
              <p className="text-xs text-slate-600 italic leading-relaxed">
                &ldquo;GaadiLelo delivers pre-qualified buyers ready to book. Instead of spending lakhs on retail marketing leads, we pass our customer acquisition savings directly to the group cohort.&rdquo;
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


      {/* 7. FREQUENTLY ASKED QUESTIONS */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-10">
          <h2 className="text-2xl font-bold text-navy-950">Frequently Asked Questions</h2>
          <p className="text-xs text-slate-500 mt-1">Everything you need to know about vehicle group buying</p>
        </div>

        <div className="space-y-4">
          <div className="p-5 bg-white rounded-2xl border border-slate-200 shadow-sm">
            <h3 className="font-bold text-sm text-navy-900 mb-1">Is joining a buying group legally binding?</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              No. Joining a buying group is completely free and non-binding. It represents an expression of high purchase intent. You can leave the group at any time before bidding closes, and you retain full freedom to accept or decline the final dealer quotation.
            </p>
          </div>

          <div className="p-5 bg-white rounded-2xl border border-slate-200 shadow-sm">
            <h3 className="font-bold text-sm text-navy-900 mb-1">Can other members of my group see my personal contact details?</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Never. Buyer privacy is a foundational pillar of {brandName}. Other cohort members only see aggregated counts and vehicle variant preferences. Your contact details are only shared with a specific authorized dealership when you explicitly click &ldquo;Request Callback&rdquo;.
            </p>
          </div>

          <div className="p-5 bg-white rounded-2xl border border-slate-200 shadow-sm">
            <h3 className="font-bold text-sm text-navy-900 mb-1">How are quotations verified by the platform?</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              All participating dealerships are verified against state transport franchise registrations. Every submitted quote is reviewed by our operations team to confirm statutory MP RTO registration slabs, insurance formulas, and genuine group discounts before it is published to buyers.
            </p>
          </div>

          <div className="p-5 bg-white rounded-2xl border border-slate-200 shadow-sm">
            <h3 className="font-bold text-sm text-navy-900 mb-1">Where and how do I receive the vehicle?</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Delivery happens directly at the winning authorized OEM dealership in Indore (e.g. AB Road or Vijay Nagar showroom). You perform standard pre-delivery inspection (PDI), receive original invoices, and register the vehicle in your individual name.
            </p>
          </div>
        </div>
      </section>

    </div>
  );
}
