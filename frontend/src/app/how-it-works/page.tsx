'use client';

import React from 'react';
import Link from 'next/link';
import { 
  Car, Users, ShieldCheck, CheckCircle2, TrendingUp, 
  Sparkles, Award, ArrowRight, Building2, MapPin, Clock 
} from 'lucide-react';

export default function HowItWorksPage() {
  const brandName = process.env.NEXT_PUBLIC_BRAND_NAME || 'GaadiLelo';

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-16">
      
      {/* Hero */}
      <div className="text-center space-y-4 max-w-2xl mx-auto">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-orange-100 text-brand-700 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>The Indian Vehicle Group-Buying Blueprint</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-black text-navy-950">
          How {brandName} Works
        </h1>
        <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
          Step-by-step transparency from demand aggregation to direct showroom delivery in Indore, Madhya Pradesh.
        </p>
      </div>

      {/* 4 Steps In-Depth */}
      <div className="space-y-8">
        
        <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200/80 shadow-sm flex flex-col md:flex-row gap-6 items-start">
          <div className="w-12 h-12 rounded-2xl bg-orange-500 text-white font-black text-lg flex items-center justify-center flex-shrink-0">
            01
          </div>
          <div className="space-y-2">
            <h2 className="text-lg font-bold text-navy-950">
              Demand Aggregation & Cohort Formation
            </h2>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
              Buyers in Indore select their desired vehicle model, variant, powertrain (Petrol, Diesel, EV, CNG), and timeline. You can either join an existing cohort or initiate a new group with a target size (e.g. 5 buyers).
            </p>
            <div className="p-3 bg-slate-50 rounded-xl text-xs text-slate-500 border border-slate-200/60">
              <strong>Key Rule:</strong> 100% Free & Non-Binding. No personal contact details are visible to other members.
            </div>
          </div>
        </div>

        <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200/80 shadow-sm flex flex-col md:flex-row gap-6 items-start">
          <div className="w-12 h-12 rounded-2xl bg-blue-600 text-white font-black text-lg flex items-center justify-center flex-shrink-0">
            02
          </div>
          <div className="space-y-2">
            <h2 className="text-lg font-bold text-navy-950">
              Milestone Qualification & Dealership Invitation
            </h2>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
              When the target member threshold is met (e.g. 5 of 5 buyers), our operations desk verifies high purchase intent and schedules an official bidding window. Only verified OEM franchised dealerships in Indore receive private invitations.
            </p>
            <div className="p-3 bg-slate-50 rounded-xl text-xs text-slate-500 border border-slate-200/60">
              <strong>Key Rule:</strong> Dealerships must possess verified state transport GSTIN and authorized OEM franchise agreements.
            </div>
          </div>
        </div>

        <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200/80 shadow-sm flex flex-col md:flex-row gap-6 items-start">
          <div className="w-12 h-12 rounded-2xl bg-purple-600 text-white font-black text-lg flex items-center justify-center flex-shrink-0">
            03
          </div>
          <div className="space-y-2">
            <h2 className="text-lg font-bold text-navy-950">
              Transparent Bidding & Mathematical Audit
            </h2>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
              Dealerships submit comprehensive itemized quotations through our Vehicle-Agnostic Pricing Engine. Our administrators audit every quote to ensure statutory MP RTO road tax accuracy, genuine OEM discounts, and eliminate arbitrary dealer handling charges.
            </p>
            <div className="p-3 bg-slate-50 rounded-xl text-xs text-slate-500 border border-slate-200/60">
              <strong>Key Rule:</strong> Dealers can revise quotes before deadline; full revision history is logged.
            </div>
          </div>
        </div>

        <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200/80 shadow-sm flex flex-col md:flex-row gap-6 items-start">
          <div className="w-12 h-12 rounded-2xl bg-emerald-600 text-white font-black text-lg flex items-center justify-center flex-shrink-0">
            04
          </div>
          <div className="space-y-2">
            <h2 className="text-lg font-bold text-navy-950">
              Side-by-Side Comparison & Direct Showroom Delivery
            </h2>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
              Approved quotations are unlocked in the group dashboard. Buyers compare competing offers side-by-side, inspect net on-road savings, and independently request a callback to finalize booking directly with the winning showroom.
            </p>
            <div className="p-3 bg-slate-50 rounded-xl text-xs text-slate-500 border border-slate-200/60">
              <strong>Key Rule:</strong> Individual registration, direct dealership invoicing, full OEM manufacturer warranties.
            </div>
          </div>
        </div>

      </div>

      {/* CTA Bottom */}
      <div className="bg-gradient-to-tr from-navy-950 to-slate-900 text-white p-8 rounded-3xl text-center space-y-4">
        <h3 className="text-xl sm:text-2xl font-bold">Ready to Experience Smarter Vehicle Buying?</h3>
        <p className="text-xs text-slate-400 max-w-md mx-auto">
          Start or join an active buying cohort in Indore today. No fees, zero risk.
        </p>
        <div className="flex justify-center gap-3 pt-2">
          <Link
            href="/vehicles"
            className="px-5 py-2.5 bg-brand-500 hover:bg-brand-600 text-white font-semibold text-xs rounded-xl shadow-md shadow-brand-500/20 transition-all flex items-center gap-1.5"
          >
            Explore Vehicles <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            href="/groups/create"
            className="px-5 py-2.5 bg-navy-800 hover:bg-navy-700 text-white font-semibold text-xs rounded-xl border border-navy-700 transition-all"
          >
            Start Cohort
          </Link>
        </div>
      </div>

    </div>
  );
}

