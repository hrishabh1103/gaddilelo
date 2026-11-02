import React from 'react';
import Link from 'next/link';
import { Car, ShieldCheck, MapPin, Phone, Mail, Award, CheckCircle2 } from 'lucide-react';

export default function Footer() {
  const brandName = process.env.NEXT_PUBLIC_BRAND_NAME || 'GaadiLelo';

  return (
    <footer className="bg-navy-950 text-slate-400 text-sm border-t border-navy-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 lg:gap-12">
          
          {/* Brand & Mission */}
          <div className="lg:col-span-2 space-y-4">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-9 h-9 rounded-xl bg-brand-500 flex items-center justify-center text-white">
                <Car className="w-5 h-5" />
              </div>
              <span className="text-xl font-black text-white">
                {brandName}<span className="text-brand-500">.com</span>
              </span>
            </Link>
            <p className="text-xs leading-relaxed text-slate-400 max-w-sm">
              India&apos;s pioneering group-buying platform for passenger and commercial vehicles. 
              By aggregating authentic buyer demand into local cohorts, authorized OEM dealerships compete 
              to provide their sharpest on-road pricing with 100% price transparency.
            </p>
            <div className="flex items-center gap-2 text-xs text-brand-400">
              <MapPin className="w-4 h-4" />
              <span>Pilot Market: Indore, Madhya Pradesh (Expansion Ready)</span>
            </div>
          </div>

          {/* Vehicle Categories */}
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-3">Vehicle Categories</h4>
            <ul className="space-y-2 text-xs">
              <li><Link href="/vehicles?category=car" className="hover:text-white transition-colors">Passenger Cars & SUVs</Link></li>
              <li><Link href="/vehicles?category=electric-vehicle" className="hover:text-white transition-colors">Electric Vehicles (EVs)</Link></li>
              <li><Link href="/vehicles?category=two-wheeler" className="hover:text-white transition-colors">Two-Wheelers & Scooters</Link></li>
              <li><Link href="/vehicles?category=commercial-vehicle" className="hover:text-white transition-colors">Commercial Pickups & LCVs</Link></li>
              <li><Link href="/vehicles?category=three-wheeler" className="hover:text-white transition-colors">Three-Wheelers</Link></li>
            </ul>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-3">Platform</h4>
            <ul className="space-y-2 text-xs">
              <li><Link href="/groups" className="hover:text-white transition-colors">Active Buying Groups</Link></li>
              <li><Link href="/groups/create" className="hover:text-white transition-colors">Start a Buying Group</Link></li>
              <li><Link href="/how-it-works" className="hover:text-white transition-colors">How Group-Buying Works</Link></li>
              <li><Link href="/register?role=DEALER" className="hover:text-brand-400 transition-colors">Dealership Partner Onboarding</Link></li>
              <li><Link href="/login" className="hover:text-white transition-colors">Sign In to Dashboard</Link></li>
            </ul>
          </div>

          {/* Transparency & Governance */}
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-3">Trust & Transparency</h4>
            <ul className="space-y-2 text-xs">
              <li className="flex items-center gap-1.5 text-slate-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                Verified OEM Dealerships
              </li>
              <li className="flex items-center gap-1.5 text-slate-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                Complete PII Privacy Shield
              </li>
              <li className="flex items-center gap-1.5 text-slate-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                Zero Mandatory Handling Fees
              </li>
              <li className="flex items-center gap-1.5 text-slate-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                No Binding Purchase Obligation
              </li>
            </ul>
          </div>

        </div>

        <div className="mt-12 pt-6 border-t border-navy-800 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
          <p>© {new Date().getFullYear()} {brandName}.com. All rights reserved. Designed for Indian Automotive Modernization.</p>
          <div className="flex items-center gap-4">
            <span className="text-[11px] bg-navy-900 px-2 py-0.5 rounded border border-navy-800 text-slate-400">
              Demo Environment — Non-Binding Indicative Quotes
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
}
